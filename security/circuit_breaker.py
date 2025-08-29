#!/usr/bin/env python3
"""
SmartCompute Circuit Breaker
Implements circuit breaker pattern for external API calls with fallback strategies
"""

import asyncio
import logging
import time
import json
from typing import Dict, Any, Optional, Callable, List, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import httpx
import aiofiles
from collections import deque, defaultdict
import hashlib

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"        # Normal operation
    OPEN = "open"           # Failing, blocking requests  
    HALF_OPEN = "half_open" # Testing if service recovered


@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration"""
    failure_threshold: int = 5          # Failures before opening
    recovery_timeout: int = 60          # Seconds before trying half-open
    success_threshold: int = 3          # Successes needed to close from half-open
    timeout: float = 30.0               # Request timeout seconds
    expected_exception: tuple = (httpx.HTTPError, asyncio.TimeoutError)
    
    # Advanced configuration
    slow_call_threshold: float = 10.0   # Seconds - calls slower than this count as failures
    slow_call_rate_threshold: float = 0.5  # If 50% of calls are slow, trip breaker
    minimum_requests: int = 10          # Minimum requests before evaluating rates
    sliding_window_size: int = 100      # Size of sliding window for rate calculation


@dataclass
class CallRecord:
    """Record of a single API call"""
    timestamp: float
    duration: float
    success: bool
    status_code: Optional[int] = None
    error_type: Optional[str] = None


class CircuitBreakerMetrics:
    """Metrics collection for circuit breaker"""
    
    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.calls = deque(maxlen=window_size)
        self.total_calls = 0
        self.total_failures = 0
        self.total_successes = 0
        self.consecutive_failures = 0
        self.consecutive_successes = 0
    
    def record_call(self, record: CallRecord):
        """Record a call result"""
        self.calls.append(record)
        self.total_calls += 1
        
        if record.success:
            self.total_successes += 1
            self.consecutive_successes += 1
            self.consecutive_failures = 0
        else:
            self.total_failures += 1
            self.consecutive_failures += 1
            self.consecutive_successes = 0
    
    def get_failure_rate(self) -> float:
        """Get current failure rate in sliding window"""
        if not self.calls:
            return 0.0
        
        failures = sum(1 for call in self.calls if not call.success)
        return failures / len(self.calls)
    
    def get_slow_call_rate(self, threshold: float) -> float:
        """Get rate of slow calls in sliding window"""
        if not self.calls:
            return 0.0
        
        slow_calls = sum(1 for call in self.calls if call.duration > threshold)
        return slow_calls / len(self.calls)
    
    def get_average_response_time(self) -> float:
        """Get average response time in sliding window"""
        if not self.calls:
            return 0.0
        
        total_duration = sum(call.duration for call in self.calls)
        return total_duration / len(self.calls)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics"""
        return {
            "total_calls": self.total_calls,
            "total_failures": self.total_failures,
            "total_successes": self.total_successes,
            "consecutive_failures": self.consecutive_failures,
            "consecutive_successes": self.consecutive_successes,
            "current_failure_rate": self.get_failure_rate(),
            "average_response_time": self.get_average_response_time(),
            "window_size": len(self.calls)
        }


class FallbackStrategy:
    """Base class for fallback strategies"""
    
    async def execute(self, *args, **kwargs) -> Any:
        """Execute fallback strategy"""
        raise NotImplementedError
    
    def get_name(self) -> str:
        """Get fallback strategy name"""
        return self.__class__.__name__


class CacheFallback(FallbackStrategy):
    """Use cached response as fallback"""
    
    def __init__(self, cache_duration: int = 3600):
        self.cache_duration = cache_duration
        self.cache: Dict[str, Dict[str, Any]] = {}
    
    async def execute(self, cache_key: str, *args, **kwargs) -> Any:
        """Return cached response if available"""
        if cache_key in self.cache:
            cached_item = self.cache[cache_key]
            if time.time() - cached_item["timestamp"] < self.cache_duration:
                logger.info(f"Using cached fallback for {cache_key}")
                return cached_item["data"]
            else:
                # Remove expired cache entry
                del self.cache[cache_key]
        
        raise Exception("No cached data available")
    
    def update_cache(self, cache_key: str, data: Any):
        """Update cache with successful response"""
        self.cache[cache_key] = {
            "data": data,
            "timestamp": time.time()
        }


class DefaultValueFallback(FallbackStrategy):
    """Return default value as fallback"""
    
    def __init__(self, default_value: Any):
        self.default_value = default_value
    
    async def execute(self, *args, **kwargs) -> Any:
        """Return default value"""
        logger.info(f"Using default value fallback: {self.default_value}")
        return self.default_value


class AlternativeServiceFallback(FallbackStrategy):
    """Use alternative service as fallback"""
    
    def __init__(self, alternative_url: str, alternative_headers: Dict[str, str] = None):
        self.alternative_url = alternative_url
        self.alternative_headers = alternative_headers or {}
    
    async def execute(self, method: str, endpoint: str, **kwargs) -> Any:
        """Call alternative service"""
        url = f"{self.alternative_url}{endpoint}"
        
        headers = kwargs.get("headers", {})
        headers.update(self.alternative_headers)
        kwargs["headers"] = headers
        
        async with httpx.AsyncClient() as client:
            logger.info(f"Using alternative service fallback: {url}")
            response = await client.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text


class CircuitBreaker:
    """Circuit breaker implementation for external API calls"""
    
    def __init__(self, name: str, config: CircuitBreakerConfig = None):
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self.state = CircuitState.CLOSED
        self.metrics = CircuitBreakerMetrics(self.config.sliding_window_size)
        self.last_failure_time = 0
        self.next_attempt_time = 0
        self.fallback_strategies: List[FallbackStrategy] = []
        self.lock = asyncio.Lock()
        
        # State transition callbacks
        self.on_state_change: Optional[Callable[[CircuitState, CircuitState], None]] = None
        self.on_failure: Optional[Callable[[Exception], None]] = None
        self.on_success: Optional[Callable[[], None]] = None
    
    def add_fallback_strategy(self, strategy: FallbackStrategy):
        """Add fallback strategy"""
        self.fallback_strategies.append(strategy)
        logger.info(f"Added fallback strategy {strategy.get_name()} to circuit {self.name}")
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function call through circuit breaker"""
        async with self.lock:
            # Check if circuit is open and if we should try recovery
            if self.state == CircuitState.OPEN:
                if time.time() >= self.next_attempt_time:
                    await self._transition_to_half_open()
                else:
                    # Circuit is open, try fallback strategies
                    return await self._execute_fallbacks(*args, **kwargs)
            
            # If in half-open state, only allow limited requests
            if self.state == CircuitState.HALF_OPEN:
                # Allow only one request at a time in half-open
                pass
        
        # Execute the actual function call
        start_time = time.time()
        
        try:
            # Apply timeout
            result = await asyncio.wait_for(func(*args, **kwargs), timeout=self.config.timeout)
            
            duration = time.time() - start_time
            
            # Check if call was too slow
            if duration > self.config.slow_call_threshold:
                await self._record_failure(duration, "slow_response")
            else:
                await self._record_success(duration)
            
            return result
            
        except asyncio.TimeoutError as e:
            duration = time.time() - start_time
            await self._record_failure(duration, "timeout")
            return await self._execute_fallbacks(*args, **kwargs)
            
        except Exception as e:
            duration = time.time() - start_time
            
            # Check if it's an expected exception type
            if isinstance(e, self.config.expected_exception):
                await self._record_failure(duration, type(e).__name__)
                return await self._execute_fallbacks(*args, **kwargs)
            else:
                # Unexpected exception, don't trigger circuit breaker
                raise
    
    async def _record_success(self, duration: float):
        """Record successful call"""
        record = CallRecord(
            timestamp=time.time(),
            duration=duration,
            success=True,
            status_code=200
        )
        
        self.metrics.record_call(record)
        
        if self.on_success:
            self.on_success()
        
        # Check for state transitions
        if self.state == CircuitState.HALF_OPEN:
            if self.metrics.consecutive_successes >= self.config.success_threshold:
                await self._transition_to_closed()
    
    async def _record_failure(self, duration: float, error_type: str):
        """Record failed call"""
        record = CallRecord(
            timestamp=time.time(),
            duration=duration,
            success=False,
            error_type=error_type
        )
        
        self.metrics.record_call(record)
        self.last_failure_time = time.time()
        
        if self.on_failure:
            self.on_failure(Exception(error_type))
        
        # Check if we should trip the circuit breaker
        await self._evaluate_circuit_state()
    
    async def _evaluate_circuit_state(self):
        """Evaluate if circuit breaker should change state"""
        if self.state == CircuitState.CLOSED:
            # Check failure threshold
            if self.metrics.consecutive_failures >= self.config.failure_threshold:
                await self._transition_to_open()
                return
            
            # Check failure rate (only if we have enough data)
            if len(self.metrics.calls) >= self.config.minimum_requests:
                failure_rate = self.metrics.get_failure_rate()
                slow_call_rate = self.metrics.get_slow_call_rate(self.config.slow_call_threshold)
                
                if (failure_rate > 0.5 or  # 50% failure rate
                    slow_call_rate > self.config.slow_call_rate_threshold):
                    await self._transition_to_open()
        
        elif self.state == CircuitState.HALF_OPEN:
            # If we get a failure in half-open, go back to open
            if not self.metrics.calls or not self.metrics.calls[-1].success:
                await self._transition_to_open()
    
    async def _transition_to_open(self):
        """Transition circuit to open state"""
        old_state = self.state
        self.state = CircuitState.OPEN
        self.next_attempt_time = time.time() + self.config.recovery_timeout
        
        logger.warning(f"Circuit breaker {self.name} opened due to failures")
        
        if self.on_state_change:
            self.on_state_change(old_state, self.state)
    
    async def _transition_to_half_open(self):
        """Transition circuit to half-open state"""
        old_state = self.state
        self.state = CircuitState.HALF_OPEN
        
        logger.info(f"Circuit breaker {self.name} transitioning to half-open for testing")
        
        if self.on_state_change:
            self.on_state_change(old_state, self.state)
    
    async def _transition_to_closed(self):
        """Transition circuit to closed state"""
        old_state = self.state
        self.state = CircuitState.CLOSED
        
        logger.info(f"Circuit breaker {self.name} closed - service recovered")
        
        if self.on_state_change:
            self.on_state_change(old_state, self.state)
    
    async def _execute_fallbacks(self, *args, **kwargs) -> Any:
        """Execute fallback strategies in order"""
        last_exception = None
        
        for strategy in self.fallback_strategies:
            try:
                logger.info(f"Trying fallback strategy {strategy.get_name()} for circuit {self.name}")
                return await strategy.execute(*args, **kwargs)
            except Exception as e:
                logger.warning(f"Fallback strategy {strategy.get_name()} failed: {e}")
                last_exception = e
                continue
        
        # If all fallbacks failed, raise the last exception or a circuit breaker exception
        if last_exception:
            raise last_exception
        else:
            raise Exception(f"Circuit breaker {self.name} is open and no fallbacks available")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current circuit breaker status"""
        return {
            "name": self.name,
            "state": self.state.value,
            "metrics": self.metrics.get_stats(),
            "config": {
                "failure_threshold": self.config.failure_threshold,
                "recovery_timeout": self.config.recovery_timeout,
                "timeout": self.config.timeout
            },
            "next_attempt_time": self.next_attempt_time if self.state == CircuitState.OPEN else None,
            "fallback_strategies": [s.get_name() for s in self.fallback_strategies]
        }
    
    async def force_open(self):
        """Manually force circuit to open state"""
        async with self.lock:
            await self._transition_to_open()
    
    async def force_close(self):
        """Manually force circuit to closed state"""
        async with self.lock:
            await self._transition_to_closed()
    
    async def reset(self):
        """Reset circuit breaker to initial state"""
        async with self.lock:
            self.state = CircuitState.CLOSED
            self.metrics = CircuitBreakerMetrics(self.config.sliding_window_size)
            self.last_failure_time = 0
            self.next_attempt_time = 0
            logger.info(f"Circuit breaker {self.name} reset")


class CircuitBreakerRegistry:
    """Registry to manage multiple circuit breakers"""
    
    def __init__(self):
        self.circuits: Dict[str, CircuitBreaker] = {}
        self.global_config = CircuitBreakerConfig()
    
    def get_circuit(self, name: str, config: CircuitBreakerConfig = None) -> CircuitBreaker:
        """Get or create circuit breaker"""
        if name not in self.circuits:
            circuit_config = config or self.global_config
            self.circuits[name] = CircuitBreaker(name, circuit_config)
            logger.info(f"Created circuit breaker: {name}")
        
        return self.circuits[name]
    
    def get_all_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all circuit breakers"""
        return {name: circuit.get_status() for name, circuit in self.circuits.items()}
    
    async def reset_all(self):
        """Reset all circuit breakers"""
        for circuit in self.circuits.values():
            await circuit.reset()
        logger.info("All circuit breakers reset")


class HTTPClientWithCircuitBreaker:
    """HTTP client with built-in circuit breaker"""
    
    def __init__(self, service_name: str, base_url: str, circuit_config: CircuitBreakerConfig = None):
        self.service_name = service_name
        self.base_url = base_url.rstrip("/")
        self.circuit = CircuitBreaker(service_name, circuit_config)
        
        # Setup cache fallback
        cache_fallback = CacheFallback()
        self.circuit.add_fallback_strategy(cache_fallback)
        self.cache_fallback = cache_fallback
        
        # HTTP client configuration
        self.client_config = {
            "timeout": circuit_config.timeout if circuit_config else 30.0,
            "limits": httpx.Limits(max_keepalive_connections=20, max_connections=100),
            "retries": 0  # We handle retries through circuit breaker
        }
    
    async def request(self, method: str, endpoint: str, cache_key: str = None, **kwargs) -> Any:
        """Make HTTP request through circuit breaker"""
        
        async def make_http_call():
            url = f"{self.base_url}{endpoint}"
            
            async with httpx.AsyncClient(**self.client_config) as client:
                response = await client.request(method, url, **kwargs)
                response.raise_for_status()
                
                result = response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text
                
                # Update cache on successful response
                if cache_key and hasattr(self.circuit.fallback_strategies[0], 'update_cache'):
                    self.cache_fallback.update_cache(cache_key, result)
                
                return result
        
        # Generate cache key if not provided
        if cache_key is None:
            cache_key = self._generate_cache_key(method, endpoint, kwargs)
        
        # Execute through circuit breaker
        return await self.circuit.call(make_http_call, cache_key=cache_key, method=method, endpoint=endpoint, **kwargs)
    
    def _generate_cache_key(self, method: str, endpoint: str, kwargs: Dict[str, Any]) -> str:
        """Generate cache key for request"""
        # Create deterministic cache key from request parameters
        key_data = {
            "service": self.service_name,
            "method": method,
            "endpoint": endpoint,
            "params": kwargs.get("params", {}),
            "json": kwargs.get("json", {})
        }
        
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    async def get(self, endpoint: str, **kwargs) -> Any:
        """GET request"""
        return await self.request("GET", endpoint, **kwargs)
    
    async def post(self, endpoint: str, **kwargs) -> Any:
        """POST request"""
        return await self.request("POST", endpoint, **kwargs)
    
    async def put(self, endpoint: str, **kwargs) -> Any:
        """PUT request"""
        return await self.request("PUT", endpoint, **kwargs)
    
    async def delete(self, endpoint: str, **kwargs) -> Any:
        """DELETE request"""
        return await self.request("DELETE", endpoint, **kwargs)
    
    def get_status(self) -> Dict[str, Any]:
        """Get circuit breaker status"""
        return self.circuit.get_status()


# Global circuit breaker registry
_circuit_registry = CircuitBreakerRegistry()


def get_circuit_breaker(name: str, config: CircuitBreakerConfig = None) -> CircuitBreaker:
    """Get circuit breaker from global registry"""
    return _circuit_registry.get_circuit(name, config)


def create_http_client(service_name: str, base_url: str, config: CircuitBreakerConfig = None) -> HTTPClientWithCircuitBreaker:
    """Create HTTP client with circuit breaker"""
    return HTTPClientWithCircuitBreaker(service_name, base_url, config)


async def get_all_circuit_status() -> Dict[str, Dict[str, Any]]:
    """Get status of all circuit breakers"""
    return _circuit_registry.get_all_status()


if __name__ == "__main__":
    import asyncio
    
    async def test_circuit_breaker():
        """Test circuit breaker functionality"""
        
        # Create circuit breaker with aggressive settings for testing
        config = CircuitBreakerConfig(
            failure_threshold=3,
            recovery_timeout=5,
            success_threshold=2,
            timeout=1.0
        )
        
        circuit = CircuitBreaker("test-service", config)
        
        # Add fallback strategies
        circuit.add_fallback_strategy(DefaultValueFallback({"status": "fallback", "message": "Service unavailable"}))
        
        # Test function that fails
        async def failing_function():
            await asyncio.sleep(2)  # This will timeout
            return {"status": "success"}
        
        # Test function that succeeds
        async def success_function():
            await asyncio.sleep(0.1)
            return {"status": "success"}
        
        print("🔧 Testing circuit breaker...")
        
        # Test failures to trip the breaker
        print("\n1. Testing failures to trip circuit breaker:")
        for i in range(5):
            try:
                result = await circuit.call(failing_function)
                print(f"  Request {i+1}: ✅ {result}")
            except Exception as e:
                print(f"  Request {i+1}: ❌ {e}")
            
            status = circuit.get_status()
            print(f"    State: {status['state']}, Consecutive failures: {status['metrics']['consecutive_failures']}")
        
        print(f"\n2. Circuit state after failures: {circuit.state.value}")
        
        # Test circuit is open (should use fallback)
        print("\n3. Testing fallback while circuit is open:")
        for i in range(2):
            try:
                result = await circuit.call(failing_function)
                print(f"  Fallback {i+1}: ✅ {result}")
            except Exception as e:
                print(f"  Fallback {i+1}: ❌ {e}")
        
        # Wait for recovery timeout
        print(f"\n4. Waiting {config.recovery_timeout} seconds for recovery timeout...")
        await asyncio.sleep(config.recovery_timeout + 1)
        
        # Test recovery with successful calls
        print("\n5. Testing recovery with successful calls:")
        for i in range(3):
            try:
                result = await circuit.call(success_function)
                print(f"  Recovery {i+1}: ✅ {result}")
                status = circuit.get_status()
                print(f"    State: {status['state']}, Consecutive successes: {status['metrics']['consecutive_successes']}")
            except Exception as e:
                print(f"  Recovery {i+1}: ❌ {e}")
        
        final_status = circuit.get_status()
        print(f"\n6. Final circuit state: {final_status['state']}")
        print(f"   Total calls: {final_status['metrics']['total_calls']}")
        print(f"   Total failures: {final_status['metrics']['total_failures']}")
        print(f"   Total successes: {final_status['metrics']['total_successes']}")
        
        print("\n✅ Circuit breaker test completed")
        
        # Test HTTP client with circuit breaker
        print("\n🌐 Testing HTTP client with circuit breaker...")
        
        # This will fail because the URL doesn't exist
        client = create_http_client("test-api", "http://nonexistent-service.local", config)
        
        try:
            result = await client.get("/test-endpoint")
            print(f"HTTP request: ✅ {result}")
        except Exception as e:
            print(f"HTTP request: ❌ {e}")
        
        print(f"HTTP client circuit state: {client.get_status()['state']}")
        
        print("\n✅ All circuit breaker tests completed")
    
    asyncio.run(test_circuit_breaker())