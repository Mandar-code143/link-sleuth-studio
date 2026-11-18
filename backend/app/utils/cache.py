"""In-memory concurrency-safe TTL cache respecting CACHE_TTL_SECONDS configuration."""

import threading
import time
from typing import Any, Dict, Optional, Tuple

from ..config import settings


class TTLMemoryCache:
    """Thread-safe in-memory cache with time-to-live expiration and LRU eviction."""

    def __init__(self, ttl_seconds: Optional[int] = None, max_size: int = 500):
        self.ttl_seconds = ttl_seconds if ttl_seconds is not None else settings.cache_ttl_seconds
        self.max_size = max_size
        self._store: Dict[str, Tuple[float, Any]] = {}
        self._lock = threading.Lock()

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            if key not in self._store:
                return None
            created_at, value = self._store[key]
            if time.time() - created_at > self.ttl_seconds:
                del self._store[key]
                return None
            return value

    def set(self, key: str, value: Any) -> None:
        with self._lock:
            if len(self._store) >= self.max_size:
                # Evict oldest entry
                oldest_key = min(self._store.keys(), key=lambda k: self._store[k][0])
                del self._store[oldest_key]
            self._store[key] = (time.time(), value)

    def delete(self, key: str) -> None:
        with self._lock:
            self._store.pop(key, None)

    def clear(self) -> None:
        with self._lock:
            self._store.clear()


# Global analysis cache singleton respecting configured TTL
analysis_cache = TTLMemoryCache(ttl_seconds=settings.cache_ttl_seconds, max_size=250)
