import time
import psutil  # type: ignore
from pathlib import Path
from typing import Dict, Any, Optional
from functools import wraps


class PerformanceMonitor:
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.cpu_usage = []
        self.memory_usage = []

    def start_monitoring(self):
        """Start performance monitoring"""
        self.start_time = time.time()

    def stop_monitoring(self):
        """Stop performance monitoring"""
        self.end_time = time.time()

    def get_current_stats(self) -> Dict[str, float]:
        """Get current system stats"""
        return {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "memory_used_gb": psutil.virtual_memory().used / (1024**3),
        }

    def get_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        if self.start_time and self.end_time:
            duration = self.end_time - self.start_time
            current_stats = self.get_current_stats()

            return {
                "duration_seconds": round(duration, 2),
                "duration_minutes": round(duration / 60, 2),
                **current_stats,
            }
        return {}


class DataCache:
    """Simple in-memory cache for timeframe data"""

    def __init__(self, max_size: int = 100):
        self.cache: Dict[str, Any] = {}
        self.access_times: Dict[str, float] = {}
        self.max_size = max_size

    def get(self, key: str) -> Optional[Any]:
        """Get cached data"""
        if key in self.cache:
            self.access_times[key] = time.time()
            return self.cache[key]
        return None

    def set(self, key: str, value: Any) -> None:
        """Set cached data with LRU eviction"""
        if len(self.cache) >= self.max_size:
            # Remove least recently used item
            oldest_key = min(
                self.access_times.keys(), key=lambda k: self.access_times[k]
            )
            del self.cache[oldest_key]
            del self.access_times[oldest_key]

        self.cache[key] = value
        self.access_times[key] = time.time()

    def clear(self) -> None:
        """Clear all cached data"""
        self.cache.clear()
        self.access_times.clear()

    def size(self) -> int:
        """Get cache size"""
        return len(self.cache)


def async_timing_decorator(func):
    """Decorator to time async functions"""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        result = await func(*args, **kwargs)
        end_time = time.time()
        duration = end_time - start_time
        print(f"⏱️ {func.__name__} completed in {duration:.2f}s")
        return result

    return wrapper


def timing_decorator(func):
    """Decorator to time regular functions"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        duration = end_time - start_time
        print(f"⏱️ {func.__name__} completed in {duration:.2f}s")
        return result

    return wrapper


class ConfigManager:
    """Manage configuration settings"""

    @staticmethod
    def get_optimal_concurrency() -> int:
        """Get optimal concurrency based on system resources"""
        cpu_count = psutil.cpu_count()
        memory_gb = psutil.virtual_memory().total / (1024**3)

        # Conservative approach for forex data processing
        if memory_gb > 16:
            return min(8, cpu_count)
        elif memory_gb > 8:
            return min(5, cpu_count)
        else:
            return min(3, cpu_count)

    @staticmethod
    def get_chunk_size(file_size_mb: float) -> int:
        """Get optimal chunk size for processing based on file size"""
        if file_size_mb > 100:
            return 10000
        elif file_size_mb > 50:
            return 5000
        else:
            return 1000


# Global instances
performance_monitor = PerformanceMonitor()
data_cache = DataCache()
