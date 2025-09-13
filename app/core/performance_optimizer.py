"""
SmartCompute Performance Optimizer
Secure performance optimizations with enterprise monitoring
"""

import asyncio
import time
import threading
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import weakref
import gc
from functools import wraps, lru_cache
import json
import os


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
    """Cache entry with expiration and security metadata"""
    data: Any
    created_at: datetime
    expires_at: Optional[datetime]
    access_level: str
    hit_count: int = 0
    last_accessed: datetime = field(default_factory=datetime.now)


class SecurePerformanceCache:
    """Security-aware performance cache with access level isolation"""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 300):
        """Initialize secure cache
        
        Args:
            max_size: Maximum cache entries
            default_ttl: Default TTL in seconds
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: Dict[str, CacheEntry] = {}
        self._access_stats: Dict[str, Dict[str, int]] = {
            "starter": {"hits": 0, "misses": 0},
            "enterprise": {"hits": 0, "misses": 0},
            "industrial": {"hits": 0, "misses": 0}
        }
        self._lock = threading.RLock()
        
        # Start cleanup task
        self._cleanup_task = None
        self._start_cleanup_task()
    
    def _start_cleanup_task(self):
        """Start background cleanup task"""
        def cleanup_loop():
            while True:
                time.sleep(60)  # Cleanup every minute
                self._cleanup_expired()
        
        cleanup_thread = threading.Thread(target=cleanup_loop, daemon=True)
        cleanup_thread.start()
    
    def _generate_key(self, key: str, access_level: str) -> str:
        """Generate cache key with access level isolation"""
        return f"{access_level}:{key}"
    
    def get(self, key: str, access_level: str = "starter") -> Optional[Any]:
        """Get value from cache with access level check"""
        cache_key = self._generate_key(key, access_level)
        
        with self._lock:
            entry = self._cache.get(cache_key)
            
            if entry is None:
                self._access_stats[access_level]["misses"] += 1
                return None
            
            # Check expiration
            if entry.expires_at and datetime.now() > entry.expires_at:
                del self._cache[cache_key]
                self._access_stats[access_level]["misses"] += 1
                return None
            
            # Update access stats
            entry.hit_count += 1
            entry.last_accessed = datetime.now()
            self._access_stats[access_level]["hits"] += 1
            
            return entry.data
    
    def set(self, key: str, value: Any, access_level: str = "starter", 
            ttl: Optional[int] = None) -> None:
        """Set value in cache with access level isolation"""
        cache_key = self._generate_key(key, access_level)
        
        # Determine expiration
        expires_at = None
        if ttl is not None:
            expires_at = datetime.now() + timedelta(seconds=ttl)
        elif self.default_ttl > 0:
            expires_at = datetime.now() + timedelta(seconds=self.default_ttl)
        
        # Security check - don't cache sensitive data for too long
        if access_level in ["enterprise", "industrial"] and ttl is None:
            expires_at = datetime.now() + timedelta(seconds=min(self.default_ttl, 60))
        
        entry = CacheEntry(
            data=value,
            created_at=datetime.now(),
            expires_at=expires_at,
            access_level=access_level
        )
        
        with self._lock:
            # Evict if at capacity
            if len(self._cache) >= self.max_size:
                self._evict_lru()
            
            self._cache[cache_key] = entry
    
    def _evict_lru(self) -> None:
        """Evict least recently used entry"""
        if not self._cache:
            return
        
        # Find LRU entry
        lru_key = min(self._cache.keys(), 
                     key=lambda k: self._cache[k].last_accessed)
        del self._cache[lru_key]
    
    def _cleanup_expired(self) -> None:
        """Remove expired entries"""
        with self._lock:
            now = datetime.now()
            expired_keys = [
                key for key, entry in self._cache.items()
                if entry.expires_at and now > entry.expires_at
            ]
            
            for key in expired_keys:
                del self._cache[key]
    
    def clear(self, access_level: Optional[str] = None) -> None:
        """Clear cache entries"""
        with self._lock:
            if access_level is None:
                self._cache.clear()
                for level_stats in self._access_stats.values():
                    level_stats["hits"] = 0
                    level_stats["misses"] = 0
            else:
                # Clear only entries for specific access level
                keys_to_remove = [
                    key for key in self._cache.keys()
                    if key.startswith(f"{access_level}:")
                ]
                for key in keys_to_remove:
                    del self._cache[key]
                
                self._access_stats[access_level]["hits"] = 0
                self._access_stats[access_level]["misses"] = 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self._lock:
            total_entries = len(self._cache)
            
            # Calculate hit rates
            stats = {
                "total_entries": total_entries,
                "max_size": self.max_size,
                "utilization": total_entries / self.max_size if self.max_size > 0 else 0,
                "access_levels": {}
            }
            
            for level, level_stats in self._access_stats.items():
                total_requests = level_stats["hits"] + level_stats["misses"]
                hit_rate = (level_stats["hits"] / total_requests) if total_requests > 0 else 0
                
                stats["access_levels"][level] = {
                    "hits": level_stats["hits"],
                    "misses": level_stats["misses"],
                    "hit_rate": round(hit_rate * 100, 2),
                    "total_requests": total_requests
                }
            
            return stats


class PerformanceOptimizer:
    """Main performance optimization controller"""
    
    def __init__(self, access_level: str = "starter"):
        """Initialize performance optimizer
        
        Args:
            access_level: "starter", "enterprise", or "industrial"
        """
        self.access_level = access_level
        self.cache = SecurePerformanceCache()
        self.metrics_history: List[PerformanceMetrics] = []
        self._optimization_enabled = access_level in ["enterprise", "industrial"]
        
        # Performance settings by access level
        self.settings = self._get_optimization_settings()
        
        print(f"🚀 Performance Optimizer initialized - {access_level.title()} level")
        if not self._optimization_enabled:
            print("ℹ️  Advanced optimizations available in Enterprise/Industrial versions")
    
    def _get_optimization_settings(self) -> Dict[str, Any]:
        """Get optimization settings based on access level"""
        base_settings = {
            "cache_enabled": True,
            "cache_ttl": 300,
            "max_cache_size": 100,
            "gc_optimization": False,
            "async_processing": False,
            "memory_monitoring": False
        }
        
        if self.access_level == "enterprise":
            base_settings.update({
                "cache_ttl": 600,
                "max_cache_size": 500,
                "gc_optimization": True,
                "async_processing": True,
                "memory_monitoring": True
            })
        elif self.access_level == "industrial":
            base_settings.update({
                "cache_ttl": 900,
                "max_cache_size": 1000,
                "gc_optimization": True,
                "async_processing": True,
                "memory_monitoring": True,
                "predictive_caching": True,
                "resource_pooling": True
            })
        
        return base_settings
    
    def performance_monitor(self, func_name: Optional[str] = None):
        """Decorator to monitor function performance"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                return self._execute_with_monitoring(func, func_name or func.__name__, *args, **kwargs)
            return wrapper
        return decorator
    
    def async_performance_monitor(self, func_name: Optional[str] = None):
        """Decorator to monitor async function performance"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(*args, **kwargs):
                return await self._execute_async_with_monitoring(func, func_name or func.__name__, *args, **kwargs)
            return wrapper
        return decorator
    
    def _execute_with_monitoring(self, func: Callable, func_name: str, *args, **kwargs) -> Any:
        """Execute function with performance monitoring"""
        import psutil
        process = psutil.Process()
        
        # Pre-execution metrics
        start_time = time.time()
        memory_before = process.memory_info().rss
        cpu_before = process.cpu_percent()
        
        try:
            # Execute function
            result = func(*args, **kwargs)
            
            # Post-execution metrics
            end_time = time.time()
            memory_after = process.memory_info().rss
            cpu_after = process.cpu_percent()
            
            # Record metrics
            metrics = PerformanceMetrics(
                execution_time=end_time - start_time,
                memory_before=memory_before,
                memory_after=memory_after,
                cpu_usage=max(cpu_before, cpu_after),
                optimizations_applied=self._get_applied_optimizations(func_name)
            )
            
            self._record_metrics(func_name, metrics)
            
            # Apply post-execution optimizations if enabled
            if self._optimization_enabled and self.settings.get("gc_optimization"):
                if metrics.execution_time > 1.0:  # Only for slow functions
                    gc.collect()
            
            return result
            
        except Exception as e:
            # Record failed execution
            end_time = time.time()
            metrics = PerformanceMetrics(
                execution_time=end_time - start_time,
                memory_before=memory_before,
                memory_after=process.memory_info().rss,
                cpu_usage=cpu_before,
                optimizations_applied=["error_handling"]
            )
            self._record_metrics(f"{func_name}_error", metrics)
            raise
    
    async def _execute_async_with_monitoring(self, func: Callable, func_name: str, *args, **kwargs) -> Any:
        """Execute async function with performance monitoring"""
        import psutil
        process = psutil.Process()
        
        start_time = time.time()
        memory_before = process.memory_info().rss
        
        try:
            result = await func(*args, **kwargs)
            
            end_time = time.time()
            memory_after = process.memory_info().rss
            
            metrics = PerformanceMetrics(
                execution_time=end_time - start_time,
                memory_before=memory_before,
                memory_after=memory_after,
                cpu_usage=0,  # CPU usage harder to measure for async
                optimizations_applied=self._get_applied_optimizations(func_name)
            )
            
            self._record_metrics(f"async_{func_name}", metrics)
            
            return result
            
        except Exception as e:
            end_time = time.time()
            metrics = PerformanceMetrics(
                execution_time=end_time - start_time,
                memory_before=memory_before,
                memory_after=process.memory_info().rss,
                cpu_usage=0,
                optimizations_applied=["async_error_handling"]
            )
            self._record_metrics(f"async_{func_name}_error", metrics)
            raise
    
    def _get_applied_optimizations(self, func_name: str) -> List[str]:
        """Get list of optimizations applied"""
        optimizations = []
        
        if self.settings.get("cache_enabled"):
            optimizations.append("caching")
        
        if self.settings.get("async_processing") and "async" in func_name.lower():
            optimizations.append("async_processing")
        
        if self.settings.get("gc_optimization"):
            optimizations.append("memory_optimization")
        
        if self.access_level in ["enterprise", "industrial"]:
            optimizations.append(f"{self.access_level}_optimizations")
        
        return optimizations
    
    def _record_metrics(self, func_name: str, metrics: PerformanceMetrics) -> None:
        """Record performance metrics"""
        # Keep only recent metrics to prevent memory bloat
        max_metrics = 1000 if self.access_level == "industrial" else 500
        
        if len(self.metrics_history) >= max_metrics:
            # Remove oldest 25% of metrics
            self.metrics_history = self.metrics_history[max_metrics // 4:]
        
        self.metrics_history.append(metrics)
        
        # Update cache stats if caching was used
        cache_stats = self.cache.get_stats()
        access_stats = cache_stats["access_levels"].get(self.access_level, {})
        
        if access_stats.get("total_requests", 0) > 0:
            metrics.cache_hits = access_stats.get("hits", 0)
            metrics.cache_misses = access_stats.get("misses", 0)
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        if not self.metrics_history:
            return {
                "access_level": self.access_level,
                "total_executions": 0,
                "optimization_enabled": self._optimization_enabled
            }
        
        # Calculate aggregated metrics
        total_executions = len(self.metrics_history)
        avg_execution_time = sum(m.execution_time for m in self.metrics_history) / total_executions
        total_memory_saved = sum(max(0, m.memory_before - m.memory_after) for m in self.metrics_history)
        
        # Get unique optimizations applied
        all_optimizations = []
        for metrics in self.metrics_history:
            all_optimizations.extend(metrics.optimizations_applied)
        unique_optimizations = list(set(all_optimizations))
        
        # Cache performance
        cache_stats = self.cache.get_stats()
        
        summary = {
            "access_level": self.access_level,
            "optimization_enabled": self._optimization_enabled,
            "execution_stats": {
                "total_executions": total_executions,
                "avg_execution_time": round(avg_execution_time, 4),
                "total_memory_saved_bytes": total_memory_saved
            },
            "cache_performance": cache_stats,
            "optimizations_applied": unique_optimizations,
            "settings": self.settings,
            "performance_score": self._calculate_performance_score()
        }
        
        # Add advanced metrics for enterprise/industrial
        if self.access_level in ["enterprise", "industrial"]:
            summary["advanced_metrics"] = self._get_advanced_metrics()
        
        return summary
    
    def _calculate_performance_score(self) -> float:
        """Calculate overall performance score (0-100)"""
        if not self.metrics_history:
            return 0.0
        
        base_score = 50.0  # Base score
        
        # Cache hit rate bonus
        cache_stats = self.cache.get_stats()
        access_stats = cache_stats["access_levels"].get(self.access_level, {})
        hit_rate = access_stats.get("hit_rate", 0) / 100.0
        cache_bonus = hit_rate * 20  # Up to 20 points
        
        # Execution time penalty
        avg_time = sum(m.execution_time for m in self.metrics_history) / len(self.metrics_history)
        time_penalty = min(avg_time * 10, 30)  # Max 30 point penalty
        
        # Optimization bonus
        optimization_bonus = len(self._get_applied_optimizations("sample")) * 5
        
        # Access level bonus
        level_bonus = {"starter": 0, "enterprise": 10, "industrial": 20}[self.access_level]
        
        score = base_score + cache_bonus - time_penalty + optimization_bonus + level_bonus
        return max(0, min(100, score))
    
    def _get_advanced_metrics(self) -> Dict[str, Any]:
        """Get advanced metrics for enterprise/industrial"""
        recent_metrics = self.metrics_history[-100:] if len(self.metrics_history) > 100 else self.metrics_history
        
        if not recent_metrics:
            return {}
        
        # Performance trends
        execution_times = [m.execution_time for m in recent_metrics]
        memory_usage = [m.memory_after - m.memory_before for m in recent_metrics]
        
        return {
            "performance_trend": {
                "execution_time_trend": "improving" if len(execution_times) > 1 and execution_times[-1] < execution_times[0] else "stable",
                "memory_trend": "optimized" if len(memory_usage) > 1 and memory_usage[-1] < memory_usage[0] else "stable"
            },
            "resource_efficiency": {
                "avg_memory_delta": sum(memory_usage) / len(memory_usage),
                "peak_execution_time": max(execution_times),
                "fastest_execution_time": min(execution_times)
            },
            "optimization_effectiveness": {
                "functions_optimized": len(set(tuple(m.optimizations_applied) for m in recent_metrics if m.optimizations_applied)),
                "total_optimizations": sum(len(m.optimizations_applied) for m in recent_metrics)
            }
        }
    
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
                cached_result = self.cache.get(cache_key, self.access_level)
                if cached_result is not None:
                    return cached_result
                
                # Execute function and cache result
                result = func(*args, **kwargs)
                cache_ttl = ttl or self.settings.get("cache_ttl", 300)
                self.cache.set(cache_key, result, self.access_level, cache_ttl)
                
                return result
            return wrapper
        return decorator
    
    def clear_performance_cache(self) -> Dict[str, Any]:
        """Clear performance cache and return stats"""
        stats_before = self.cache.get_stats()
        self.cache.clear(self.access_level)
        
        return {
            "cleared": True,
            "stats_before_clear": stats_before,
            "access_level": self.access_level
        }


# Global performance optimizer instances
starter_optimizer = PerformanceOptimizer("starter")
enterprise_optimizer = PerformanceOptimizer("enterprise") 
industrial_optimizer = PerformanceOptimizer("industrial")


def get_performance_optimizer(access_level: str = "starter") -> PerformanceOptimizer:
    """Get performance optimizer for access level
    
    Args:
        access_level: "starter", "enterprise", or "industrial"
        
    Returns:
        PerformanceOptimizer instance
    """
    optimizers = {
        "starter": starter_optimizer,
        "enterprise": enterprise_optimizer,
        "industrial": industrial_optimizer
    }
    return optimizers.get(access_level.lower(), starter_optimizer)