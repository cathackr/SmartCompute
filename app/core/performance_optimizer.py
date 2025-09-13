"""
SmartCompute Performance Optimizer
Basic performance optimizations for the free version
"""

import time
import threading
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import weakref
import gc
from functools import wraps


@dataclass
class PerformanceMetrics:
    """Performance metrics tracking"""
    execution_time: float
    memory_before: int
    memory_after: int
    cpu_usage: float
    cache_hits: int = 0
    cache_misses: int = 0
    optimizations_applied: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass  
class CacheEntry:
    """Cache entry with expiration"""
    data: Any
    created_at: datetime
    expires_at: Optional[datetime]
    hit_count: int = 0
    last_accessed: datetime = field(default_factory=datetime.now)


class BasicPerformanceCache:
    """Basic performance cache for free version"""
    
    def __init__(self, max_size: int = 100, default_ttl: int = 300):
        """Initialize basic cache
        
        Args:
            max_size: Maximum cache entries
            default_ttl: Default TTL in seconds
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: Dict[str, CacheEntry] = {}
        self._stats = {"hits": 0, "misses": 0}
        self._lock = threading.RLock()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        with self._lock:
            entry = self._cache.get(key)
            
            if entry is None:
                self._stats["misses"] += 1
                return None
            
            # Check expiration
            if entry.expires_at and datetime.now() > entry.expires_at:
                del self._cache[key]
                self._stats["misses"] += 1
                return None
            
            # Update access stats
            entry.hit_count += 1
            entry.last_accessed = datetime.now()
            self._stats["hits"] += 1
            
            return entry.data
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache"""
        # Determine expiration
        expires_at = None
        if ttl is not None:
            expires_at = datetime.now() + timedelta(seconds=ttl)
        elif self.default_ttl > 0:
            expires_at = datetime.now() + timedelta(seconds=self.default_ttl)
        
        entry = CacheEntry(
            data=value,
            created_at=datetime.now(),
            expires_at=expires_at
        )
        
        with self._lock:
            # Evict if at capacity
            if len(self._cache) >= self.max_size:
                self._evict_lru()
            
            self._cache[key] = entry
    
    def _evict_lru(self) -> None:
        """Evict least recently used entry"""
        if not self._cache:
            return
        
        lru_key = min(self._cache.keys(), 
                     key=lambda k: self._cache[k].last_accessed)
        del self._cache[lru_key]
    
    def clear(self) -> None:
        """Clear cache entries"""
        with self._lock:
            self._cache.clear()
            self._stats["hits"] = 0
            self._stats["misses"] = 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self._lock:
            total_entries = len(self._cache)
            total_requests = self._stats["hits"] + self._stats["misses"]
            hit_rate = (self._stats["hits"] / total_requests) if total_requests > 0 else 0
            
            return {
                "total_entries": total_entries,
                "max_size": self.max_size,
                "utilization": total_entries / self.max_size if self.max_size > 0 else 0,
                "hits": self._stats["hits"],
                "misses": self._stats["misses"],
                "hit_rate": round(hit_rate * 100, 2),
                "total_requests": total_requests
            }


class PerformanceOptimizer:
    """Basic performance optimization controller"""
    
    def __init__(self):
        """Initialize performance optimizer"""
        self.cache = BasicPerformanceCache()
        self.metrics_history: List[PerformanceMetrics] = []
        
        # Basic settings for free version
        self.settings = {
            "cache_enabled": True,
            "cache_ttl": 300,
            "max_cache_size": 100,
            "gc_optimization": False,
            "memory_monitoring": True
        }
        
        print("🚀 Performance Optimizer initialized - Basic version")
    
    def performance_monitor(self, func_name: Optional[str] = None):
        """Decorator to monitor function performance"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                return self._execute_with_monitoring(func, func_name or func.__name__, *args, **kwargs)
            return wrapper
        return decorator
    
    def _execute_with_monitoring(self, func: Callable, func_name: str, *args, **kwargs) -> Any:
        """Execute function with basic performance monitoring"""
        try:
            import psutil
            process = psutil.Process()
            
            # Pre-execution metrics
            start_time = time.time()
            memory_before = process.memory_info().rss
            cpu_before = process.cpu_percent()
            
        except ImportError:
            # Fallback if psutil not available
            start_time = time.time()
            memory_before = 0
            cpu_before = 0
        
        try:
            # Execute function
            result = func(*args, **kwargs)
            
            # Post-execution metrics
            end_time = time.time()
            
            try:
                memory_after = process.memory_info().rss
                cpu_after = process.cpu_percent()
            except:
                memory_after = memory_before
                cpu_after = cpu_before
            
            # Record metrics
            metrics = PerformanceMetrics(
                execution_time=end_time - start_time,
                memory_before=memory_before,
                memory_after=memory_after,
                cpu_usage=max(cpu_before, cpu_after),
                optimizations_applied=["basic_monitoring"]
            )
            
            self._record_metrics(func_name, metrics)
            
            return result
            
        except Exception as e:
            # Record failed execution
            end_time = time.time()
            metrics = PerformanceMetrics(
                execution_time=end_time - start_time,
                memory_before=memory_before,
                memory_after=memory_before,
                cpu_usage=cpu_before,
                optimizations_applied=["error_handling"]
            )
            self._record_metrics(f"{func_name}_error", metrics)
            raise
    
    def _record_metrics(self, func_name: str, metrics: PerformanceMetrics) -> None:
        """Record performance metrics"""
        # Keep only recent metrics to prevent memory bloat
        max_metrics = 500
        
        if len(self.metrics_history) >= max_metrics:
            # Remove oldest 25% of metrics
            self.metrics_history = self.metrics_history[max_metrics // 4:]
        
        self.metrics_history.append(metrics)
        
        # Update cache stats if caching was used
        cache_stats = self.cache.get_stats()
        if cache_stats.get("total_requests", 0) > 0:
            metrics.cache_hits = cache_stats.get("hits", 0)
            metrics.cache_misses = cache_stats.get("misses", 0)
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        if not self.metrics_history:
            return {
                "total_executions": 0,
                "version": "basic"
            }
        
        # Calculate aggregated metrics
        total_executions = len(self.metrics_history)
        avg_execution_time = sum(m.execution_time for m in self.metrics_history) / total_executions
        total_memory_saved = sum(max(0, m.memory_before - m.memory_after) for m in self.metrics_history)
        
        # Cache performance
        cache_stats = self.cache.get_stats()
        
        summary = {
            "version": "basic",
            "execution_stats": {
                "total_executions": total_executions,
                "avg_execution_time": round(avg_execution_time, 4),
                "total_memory_saved_bytes": total_memory_saved
            },
            "cache_performance": cache_stats,
            "settings": self.settings,
            "performance_score": self._calculate_performance_score()
        }
        
        return summary
    
    def _calculate_performance_score(self) -> float:
        """Calculate basic performance score (0-100)"""
        if not self.metrics_history:
            return 0.0
        
        base_score = 50.0  # Base score
        
        # Cache hit rate bonus
        cache_stats = self.cache.get_stats()
        hit_rate = cache_stats.get("hit_rate", 0) / 100.0
        cache_bonus = hit_rate * 20  # Up to 20 points
        
        # Execution time penalty
        avg_time = sum(m.execution_time for m in self.metrics_history) / len(self.metrics_history)
        time_penalty = min(avg_time * 10, 30)  # Max 30 point penalty
        
        score = base_score + cache_bonus - time_penalty
        return max(0, min(100, score))
    
    def optimize_function_cache(self, key_func: Optional[Callable] = None, ttl: Optional[int] = None):
        """Decorator for function result caching"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                if not self.settings.get("cache_enabled"):
                    return func(*args, **kwargs)
                
                # Generate cache key
                if key_func:
                    cache_key = key_func(*args, **kwargs)
                else:
                    cache_key = f"{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
                
                # Try to get from cache
                cached_result = self.cache.get(cache_key)
                if cached_result is not None:
                    return cached_result
                
                # Execute function and cache result
                result = func(*args, **kwargs)
                cache_ttl = ttl or self.settings.get("cache_ttl", 300)
                self.cache.set(cache_key, result, cache_ttl)
                
                return result
            return wrapper
        return decorator
    
    def clear_performance_cache(self) -> Dict[str, Any]:
        """Clear performance cache and return stats"""
        stats_before = self.cache.get_stats()
        self.cache.clear()
        
        return {
            "cleared": True,
            "stats_before_clear": stats_before,
            "version": "basic"
        }


# Global performance optimizer instance
performance_optimizer = PerformanceOptimizer()


def get_performance_optimizer() -> PerformanceOptimizer:
    """Get performance optimizer instance
    
    Returns:
        PerformanceOptimizer instance
    """
    return performance_optimizer