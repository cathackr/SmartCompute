#!/usr/bin/env python3
"""
SmartCompute Advanced Rate Limiting
Implements token bucket, sliding window, and adaptive rate limiting
"""

import asyncio
import logging
import time
import json
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import redis.asyncio as redis
from fastapi import Request, HTTPException
import hashlib
import ipaddress

logger = logging.getLogger(__name__)


class RateLimitStrategy(Enum):
    """Rate limiting strategies"""
    TOKEN_BUCKET = "token_bucket"
    SLIDING_WINDOW = "sliding_window"
    FIXED_WINDOW = "fixed_window"
    ADAPTIVE = "adaptive"


@dataclass
class RateLimit:
    """Rate limit configuration"""
    requests: int  # Number of requests
    window: int    # Time window in seconds
    strategy: RateLimitStrategy = RateLimitStrategy.TOKEN_BUCKET
    burst: Optional[int] = None  # Burst capacity (for token bucket)
    
    def __post_init__(self):
        if self.burst is None:
            self.burst = self.requests * 2  # Default burst is 2x the rate


@dataclass
class ClientInfo:
    """Client information for rate limiting"""
    client_id: str
    client_type: str  # "service", "api_key", "anonymous"
    trust_level: int = 1  # 1-5, higher = more trusted
    last_seen: float = field(default_factory=time.time)
    request_count: int = 0
    violations: int = 0
    
    def update_stats(self):
        """Update client statistics"""
        self.last_seen = time.time()
        self.request_count += 1


class TokenBucket:
    """Token bucket implementation for rate limiting"""
    
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate = refill_rate  # tokens per second
        self.last_refill = time.time()
        self.lock = asyncio.Lock()
    
    async def consume(self, tokens: int = 1) -> bool:
        """Try to consume tokens from bucket"""
        async with self.lock:
            now = time.time()
            # Refill bucket
            elapsed = now - self.last_refill
            self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
            self.last_refill = now
            
            # Try to consume tokens
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get bucket status"""
        return {
            "capacity": self.capacity,
            "tokens": self.tokens,
            "refill_rate": self.refill_rate
        }


class SlidingWindow:
    """Sliding window implementation for rate limiting"""
    
    def __init__(self, window_size: int, max_requests: int):
        self.window_size = window_size
        self.max_requests = max_requests
        self.requests = deque()
        self.lock = asyncio.Lock()
    
    async def add_request(self) -> bool:
        """Add request to sliding window"""
        async with self.lock:
            now = time.time()
            
            # Remove old requests outside the window
            while self.requests and self.requests[0] <= now - self.window_size:
                self.requests.popleft()
            
            # Check if we can add new request
            if len(self.requests) < self.max_requests:
                self.requests.append(now)
                return True
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get window status"""
        return {
            "window_size": self.window_size,
            "max_requests": self.max_requests,
            "current_requests": len(self.requests)
        }


class AdaptiveRateLimiter:
    """Adaptive rate limiter that adjusts based on system load and client behavior"""
    
    def __init__(self, base_limit: RateLimit):
        self.base_limit = base_limit
        self.system_load = 0.5  # 0.0 = no load, 1.0 = max load
        self.error_rate = 0.0   # Current error rate
        self.adaptation_factor = 1.0  # Multiplier for base limit
        
    def adjust_limits(self, system_metrics: Dict[str, float]):
        """Adjust rate limits based on system metrics"""
        # Factors that affect rate limiting
        cpu_usage = system_metrics.get("cpu_usage", 0.5)
        memory_usage = system_metrics.get("memory_usage", 0.5)
        error_rate = system_metrics.get("error_rate", 0.0)
        response_time = system_metrics.get("avg_response_time", 0.1)
        
        # Calculate system load
        self.system_load = max(cpu_usage, memory_usage)
        self.error_rate = error_rate
        
        # Adjust adaptation factor
        if self.system_load > 0.8 or error_rate > 0.1:
            # High load or errors - reduce limits
            self.adaptation_factor = max(0.2, self.adaptation_factor * 0.9)
        elif self.system_load < 0.5 and error_rate < 0.01:
            # Low load and few errors - increase limits
            self.adaptation_factor = min(2.0, self.adaptation_factor * 1.1)
        
        # Response time based adjustment
        if response_time > 1.0:  # Slow responses
            self.adaptation_factor *= 0.95
        
        logger.debug(f"Adaptive factor: {self.adaptation_factor:.2f}, "
                    f"system load: {self.system_load:.2f}, "
                    f"error rate: {error_rate:.2f}")
    
    def get_adjusted_limit(self, client_info: ClientInfo) -> RateLimit:
        """Get adjusted rate limit for client"""
        # Base adjustment
        adjusted_requests = int(self.base_limit.requests * self.adaptation_factor)
        
        # Trust level adjustment
        trust_multiplier = 1.0 + (client_info.trust_level - 1) * 0.5
        adjusted_requests = int(adjusted_requests * trust_multiplier)
        
        # Violation penalty
        if client_info.violations > 0:
            violation_penalty = max(0.1, 1.0 - (client_info.violations * 0.1))
            adjusted_requests = int(adjusted_requests * violation_penalty)
        
        return RateLimit(
            requests=max(1, adjusted_requests),
            window=self.base_limit.window,
            strategy=self.base_limit.strategy,
            burst=max(1, int(adjusted_requests * 1.5))
        )


class DistributedRateLimiter:
    """Distributed rate limiter using Redis"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379/1"):
        self.redis_url = redis_url
        self.redis_pool = None
        
    async def init_redis(self):
        """Initialize Redis connection pool"""
        try:
            self.redis_pool = redis.ConnectionPool.from_url(self.redis_url)
            logger.info("Redis connection pool initialized for rate limiting")
        except Exception as e:
            logger.error(f"Failed to initialize Redis: {e}")
            self.redis_pool = None
    
    async def check_rate_limit(self, key: str, limit: RateLimit) -> Tuple[bool, Dict[str, Any]]:
        """Check rate limit using Redis"""
        if not self.redis_pool:
            # Fallback to allowing request if Redis unavailable
            logger.warning("Redis unavailable, allowing request")
            return True, {"fallback": True}
        
        try:
            async with redis.Redis(connection_pool=self.redis_pool) as r:
                if limit.strategy == RateLimitStrategy.SLIDING_WINDOW:
                    return await self._sliding_window_check(r, key, limit)
                elif limit.strategy == RateLimitStrategy.FIXED_WINDOW:
                    return await self._fixed_window_check(r, key, limit)
                else:
                    return await self._token_bucket_check(r, key, limit)
                    
        except Exception as e:
            logger.error(f"Redis rate limit check failed: {e}")
            return True, {"error": str(e)}
    
    async def _sliding_window_check(self, redis_client, key: str, limit: RateLimit) -> Tuple[bool, Dict[str, Any]]:
        """Sliding window rate limit check"""
        now = time.time()
        window_start = now - limit.window
        
        # Lua script for atomic sliding window
        lua_script = """
        local key = KEYS[1]
        local now = tonumber(ARGV[1])
        local window_start = tonumber(ARGV[2])
        local max_requests = tonumber(ARGV[3])
        local window_size = tonumber(ARGV[4])
        
        -- Remove old entries
        redis.call('ZREMRANGEBYSCORE', key, '-inf', window_start)
        
        -- Count current requests
        local current_count = redis.call('ZCARD', key)
        
        if current_count < max_requests then
            -- Add new request
            redis.call('ZADD', key, now, now)
            redis.call('EXPIRE', key, window_size)
            return {1, current_count + 1, max_requests}
        else
            return {0, current_count, max_requests}
        end
        """
        
        result = await redis_client.eval(
            lua_script, 1, key, now, window_start, limit.requests, limit.window
        )
        
        allowed, current, max_requests = result
        return bool(allowed), {
            "current": current,
            "limit": max_requests,
            "window": limit.window,
            "strategy": "sliding_window"
        }
    
    async def _fixed_window_check(self, redis_client, key: str, limit: RateLimit) -> Tuple[bool, Dict[str, Any]]:
        """Fixed window rate limit check"""
        now = int(time.time())
        window = now // limit.window * limit.window
        window_key = f"{key}:{window}"
        
        # Lua script for atomic fixed window
        lua_script = """
        local key = KEYS[1]
        local max_requests = tonumber(ARGV[1])
        local ttl = tonumber(ARGV[2])
        
        local current = redis.call('GET', key) or 0
        current = tonumber(current)
        
        if current < max_requests then
            local new_count = redis.call('INCR', key)
            redis.call('EXPIRE', key, ttl)
            return {1, new_count, max_requests}
        else
            return {0, current, max_requests}
        end
        """
        
        result = await redis_client.eval(
            lua_script, 1, window_key, limit.requests, limit.window
        )
        
        allowed, current, max_requests = result
        return bool(allowed), {
            "current": current,
            "limit": max_requests,
            "window": limit.window,
            "strategy": "fixed_window"
        }
    
    async def _token_bucket_check(self, redis_client, key: str, limit: RateLimit) -> Tuple[bool, Dict[str, Any]]:
        """Token bucket rate limit check"""
        # Lua script for atomic token bucket
        lua_script = """
        local key = KEYS[1]
        local capacity = tonumber(ARGV[1])
        local refill_rate = tonumber(ARGV[2])
        local tokens_requested = tonumber(ARGV[3])
        local now = tonumber(ARGV[4])
        
        local bucket = redis.call('HMGET', key, 'tokens', 'last_refill')
        local tokens = tonumber(bucket[1]) or capacity
        local last_refill = tonumber(bucket[2]) or now
        
        -- Refill tokens
        local elapsed = now - last_refill
        tokens = math.min(capacity, tokens + elapsed * refill_rate)
        
        if tokens >= tokens_requested then
            tokens = tokens - tokens_requested
            redis.call('HMSET', key, 'tokens', tokens, 'last_refill', now)
            redis.call('EXPIRE', key, 3600)  -- Expire bucket after 1 hour
            return {1, tokens, capacity}
        else
            redis.call('HMSET', key, 'tokens', tokens, 'last_refill', now)
            redis.call('EXPIRE', key, 3600)
            return {0, tokens, capacity}
        end
        """
        
        refill_rate = limit.requests / limit.window
        result = await redis_client.eval(
            lua_script, 1, key, limit.burst, refill_rate, 1, time.time()
        )
        
        allowed, tokens, capacity = result
        return bool(allowed), {
            "tokens": tokens,
            "capacity": capacity,
            "refill_rate": refill_rate,
            "strategy": "token_bucket"
        }


class SmartRateLimiter:
    """Advanced rate limiter with multiple strategies and client intelligence"""
    
    def __init__(self, redis_url: str = None):
        self.distributed_limiter = DistributedRateLimiter(redis_url) if redis_url else None
        self.local_buckets: Dict[str, TokenBucket] = {}
        self.local_windows: Dict[str, SlidingWindow] = {}
        self.clients: Dict[str, ClientInfo] = {}
        self.adaptive_limiter = None
        
        # Rate limit configurations by client type
        self.rate_limits = {
            "anonymous": RateLimit(requests=100, window=3600),  # 100/hour
            "api_key": RateLimit(requests=1000, window=3600),   # 1000/hour
            "service": RateLimit(requests=10000, window=3600, strategy=RateLimitStrategy.TOKEN_BUCKET),
            "premium": RateLimit(requests=5000, window=3600),   # 5000/hour
            "admin": RateLimit(requests=50000, window=3600),    # 50k/hour
        }
        
        # IP-based limits
        self.ip_limits = {
            "default": RateLimit(requests=1000, window=3600),
            "suspicious": RateLimit(requests=10, window=3600),
            "internal": RateLimit(requests=100000, window=3600),
        }
    
    async def initialize(self):
        """Initialize rate limiter"""
        if self.distributed_limiter:
            await self.distributed_limiter.init_redis()
        
        # Initialize adaptive limiter
        base_limit = self.rate_limits["api_key"]
        self.adaptive_limiter = AdaptiveRateLimiter(base_limit)
        
        logger.info("Smart rate limiter initialized")
    
    def _get_client_id(self, request: Request) -> str:
        """Generate unique client ID from request"""
        # Try different identification methods
        
        # 1. Service authentication
        if hasattr(request.state, "auth"):
            auth_info = request.state.auth
            if "service" in auth_info:
                return f"service:{auth_info['service']}"
            elif "client" in auth_info:
                return f"client:{auth_info['client']}"
        
        # 2. API key
        api_key = request.headers.get("X-API-Key")
        if api_key:
            key_hash = hashlib.sha256(api_key.encode()).hexdigest()[:16]
            return f"apikey:{key_hash}"
        
        # 3. IP address (with some privacy protection)
        client_ip = self._get_client_ip(request)
        if client_ip:
            # Hash IP for privacy while maintaining rate limiting
            ip_hash = hashlib.sha256(client_ip.encode()).hexdigest()[:16]
            return f"ip:{ip_hash}"
        
        # 4. Fallback to anonymous
        return "anonymous"
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address from request"""
        # Check headers in order of preference
        headers = [
            "X-Forwarded-For",
            "X-Real-IP", 
            "X-Client-IP",
            "CF-Connecting-IP"  # Cloudflare
        ]
        
        for header in headers:
            ip = request.headers.get(header)
            if ip:
                # Handle comma-separated IPs (X-Forwarded-For)
                return ip.split(",")[0].strip()
        
        # Fallback to direct connection IP
        return request.client.host if request.client else "unknown"
    
    def _classify_ip(self, ip: str) -> str:
        """Classify IP address for rate limiting"""
        try:
            addr = ipaddress.ip_address(ip)
            
            # Internal/private networks get higher limits
            if addr.is_private or addr.is_loopback:
                return "internal"
            
            # TODO: Implement IP reputation/threat intelligence
            # For now, treat all public IPs as default
            return "default"
            
        except ValueError:
            return "default"
    
    def _get_client_info(self, client_id: str, request: Request) -> ClientInfo:
        """Get or create client information"""
        if client_id not in self.clients:
            # Determine client type and trust level
            client_type = "anonymous"
            trust_level = 1
            
            if client_id.startswith("service:"):
                client_type = "service"
                trust_level = 4
            elif client_id.startswith("apikey:"):
                client_type = "api_key"
                trust_level = 3
            elif client_id.startswith("ip:"):
                client_ip = self._get_client_ip(request)
                ip_class = self._classify_ip(client_ip)
                if ip_class == "internal":
                    trust_level = 5
                elif ip_class == "suspicious":
                    trust_level = 1
                else:
                    trust_level = 2
            
            self.clients[client_id] = ClientInfo(
                client_id=client_id,
                client_type=client_type,
                trust_level=trust_level
            )
        
        client_info = self.clients[client_id]
        client_info.update_stats()
        return client_info
    
    def _get_rate_limit(self, client_info: ClientInfo) -> RateLimit:
        """Get appropriate rate limit for client"""
        # Get base limit by client type
        base_limit = self.rate_limits.get(client_info.client_type, self.rate_limits["anonymous"])
        
        # Apply adaptive adjustment if enabled
        if self.adaptive_limiter and client_info.client_type in ["api_key", "anonymous"]:
            return self.adaptive_limiter.get_adjusted_limit(client_info)
        
        return base_limit
    
    async def check_rate_limit(self, request: Request) -> Tuple[bool, Dict[str, Any]]:
        """Check if request should be rate limited"""
        client_id = self._get_client_id(request)
        client_info = self._get_client_info(client_id, request)
        rate_limit = self._get_rate_limit(client_info)
        
        # Use distributed limiter if available, otherwise local
        if self.distributed_limiter:
            allowed, info = await self.distributed_limiter.check_rate_limit(
                f"rl:{client_id}", rate_limit
            )
        else:
            allowed, info = await self._local_rate_limit_check(client_id, rate_limit)
        
        # Update violation count if rate limited
        if not allowed:
            client_info.violations += 1
            logger.warning(f"Rate limit exceeded for {client_id}: {info}")
        
        # Add client info to response
        info.update({
            "client_id": client_id[:20] + "..." if len(client_id) > 20 else client_id,
            "client_type": client_info.client_type,
            "trust_level": client_info.trust_level,
            "violations": client_info.violations
        })
        
        return allowed, info
    
    async def _local_rate_limit_check(self, client_id: str, limit: RateLimit) -> Tuple[bool, Dict[str, Any]]:
        """Local rate limit check (fallback when Redis unavailable)"""
        if limit.strategy == RateLimitStrategy.TOKEN_BUCKET:
            if client_id not in self.local_buckets:
                refill_rate = limit.requests / limit.window
                self.local_buckets[client_id] = TokenBucket(limit.burst, refill_rate)
            
            bucket = self.local_buckets[client_id]
            allowed = await bucket.consume(1)
            return allowed, bucket.get_status()
            
        elif limit.strategy == RateLimitStrategy.SLIDING_WINDOW:
            if client_id not in self.local_windows:
                self.local_windows[client_id] = SlidingWindow(limit.window, limit.requests)
            
            window = self.local_windows[client_id]
            allowed = await window.add_request()
            return allowed, window.get_status()
        
        # Fallback to allowing request
        return True, {"strategy": "fallback"}
    
    async def update_system_metrics(self, metrics: Dict[str, float]):
        """Update system metrics for adaptive rate limiting"""
        if self.adaptive_limiter:
            self.adaptive_limiter.adjust_limits(metrics)


class RateLimitMiddleware:
    """FastAPI middleware for rate limiting"""
    
    def __init__(self, rate_limiter: SmartRateLimiter):
        self.rate_limiter = rate_limiter
    
    async def __call__(self, request: Request, call_next):
        """Process request through rate limiter"""
        
        # Skip rate limiting for certain endpoints
        if request.url.path in ["/health", "/metrics"]:
            return await call_next(request)
        
        try:
            # Check rate limit
            allowed, info = await self.rate_limiter.check_rate_limit(request)
            
            if not allowed:
                # Return rate limit exceeded response
                raise HTTPException(
                    status_code=429,
                    detail="Rate limit exceeded",
                    headers={
                        "X-RateLimit-Limit": str(info.get("limit", "unknown")),
                        "X-RateLimit-Remaining": str(max(0, info.get("limit", 0) - info.get("current", 0))),
                        "X-RateLimit-Reset": str(int(time.time() + info.get("window", 3600))),
                        "Retry-After": str(info.get("window", 3600))
                    }
                )
            
            # Process request
            response = await call_next(request)
            
            # Add rate limit headers to response
            if info:
                response.headers["X-RateLimit-Limit"] = str(info.get("limit", "unknown"))
                response.headers["X-RateLimit-Remaining"] = str(max(0, info.get("limit", 0) - info.get("current", 0)))
                response.headers["X-RateLimit-Client-Type"] = info.get("client_type", "unknown")
            
            return response
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Rate limiting middleware error: {e}")
            # Allow request if rate limiter fails
            return await call_next(request)


# Factory functions
def create_rate_limiter(redis_url: str = None) -> SmartRateLimiter:
    """Create and initialize rate limiter"""
    return SmartRateLimiter(redis_url)


def create_rate_limit_middleware(redis_url: str = None) -> RateLimitMiddleware:
    """Create rate limiting middleware"""
    rate_limiter = create_rate_limiter(redis_url)
    return RateLimitMiddleware(rate_limiter)


if __name__ == "__main__":
    import asyncio
    
    async def test_rate_limiter():
        """Test rate limiter functionality"""
        
        # Create rate limiter
        limiter = SmartRateLimiter()
        await limiter.initialize()
        
        # Mock request
        class MockRequest:
            def __init__(self, client_host: str = "127.0.0.1"):
                self.client = type('obj', (object,), {'host': client_host})
                self.headers = {}
                self.url = type('obj', (object,), {'path': '/test'})
                self.state = type('obj', (object,), {})
        
        request = MockRequest()
        
        # Test rate limiting
        print("Testing rate limiter...")
        
        for i in range(10):
            allowed, info = await limiter.check_rate_limit(request)
            print(f"Request {i+1}: {'✅ Allowed' if allowed else '❌ Rate Limited'} - {info}")
            
            if not allowed:
                break
            
            await asyncio.sleep(0.1)
        
        print("✅ Rate limiter test completed")
    
    asyncio.run(test_rate_limiter())