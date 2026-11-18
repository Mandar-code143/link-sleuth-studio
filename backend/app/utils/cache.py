"""In-memory TTL cache for safe website extraction and analysis results."""

import time
from typing import Any, Dict, Optional, Tuple


class TTLMemoryCache:
    """Simple in-memory thread-safe cache with time-to-live expiration."""

    def __init__(self, ttl_seconds: int = 3600, max_size: int = 200):
        self.ttl_seconds = ttl_seconds
        self.max_size = max_size
        self._store: Dict[str, Tuple[float, Any]] = {}

    def get(self, key: str) -> Optional[Any]:
        if key not in self._store:
            return None
        created_at, value = self._store[key]
        if time.time() - created_at > self.ttl_seconds:
            del self._store[key]
            return None
        return value

    def set(self, key: str, value: Any) -> None:
        if len(self._store) >= self.max_size:
            # Evict oldest entry
            oldest_key = min(self._store.keys(), key=lambda k: self._store[k][0])
            del self._store[oldest_key]
        self._store[key] = (time.time(), value)

    def clear(self) -> None:
        self._store.clear()


# Global analysis cache singleton
analysis_cache = TTLMemoryCache(ttl_seconds=3600, max_size=100)
