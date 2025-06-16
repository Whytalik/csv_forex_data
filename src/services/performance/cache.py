import time
from typing import Dict, Any, Optional


class DataCache:
    """Simple in-memory cache for timeframe data with LRU eviction."""

    def __init__(self, max_size: int = 100):
        self.cache: Dict[str, Any] = {}
        self.access_times: Dict[str, float] = {}
        self.max_size = max_size
        self.cache_version = "v2"  # Add version to invalidate old cache entries

    def get(self, key: str) -> Optional[Any]:
        """Get cached data"""
        versioned_key = f"{key}_{self.cache_version}"
        if versioned_key in self.cache:
            self.access_times[versioned_key] = time.time()
            return self.cache[versioned_key]
        return None

    def set(self, key: str, value: Any) -> None:
        """Set cached data with LRU eviction"""
        versioned_key = f"{key}_{self.cache_version}"

        if len(self.cache) >= self.max_size:
            # Remove least recently used item
            oldest_key = min(
                self.access_times.keys(), key=lambda k: self.access_times[k]
            )
            del self.cache[oldest_key]
            del self.access_times[oldest_key]

        self.cache[versioned_key] = value
        self.access_times[versioned_key] = time.time()

    def clear(self) -> None:
        """Clear all cached data"""
        self.cache.clear()
        self.access_times.clear()

    def size(self) -> int:
        """Get cache size"""
        return len(self.cache)


# Global instance
data_cache = DataCache()
