from __future__ import annotations

import logging
import time
from typing import Any

import anyio
import orjson

from esmerald.protocols.cache import CacheBackend

logger = logging.getLogger(__name__)


class InMemoryCache(CacheBackend):
    """Thread-safe in-memory cache with TTL support, matching RedisCache API."""

    def __init__(self) -> None:
        self._store: dict[str, tuple[bytes, float | None]] = {}

    async def get(self, key: str) -> Any | None:
        """Retrieve a value from cache asynchronously."""
        return await anyio.to_thread.run_sync(self.sync_get, key)

    async def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Store a value in cache asynchronously with optional TTL."""
        await anyio.to_thread.run_sync(self.sync_set, key, value, ttl)

    async def delete(self, key: str) -> None:
        """Remove a value from cache asynchronously."""
        await anyio.to_thread.run_sync(self.sync_delete, key)

    def sync_get(self, key: str) -> Any | None:
        """Retrieve a value from cache synchronously."""
        try:
            data = self._store.get(key)
            if not data:
                return None

            value, expiry = data
            if expiry is not None and expiry < time.time():
                self.sync_delete(key)
                return None

            return orjson.loads(value)
        except Exception as e:
            logger.exception(f"Cache get error: {e}")
            return None

    def sync_set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Store a value in cache synchronously with optional TTL."""
        try:
            expiry = time.time() + ttl if ttl else None
            self._store[key] = (orjson.dumps(value), expiry)
        except Exception as e:
            logger.exception(f"Cache set error: {e}")

    def sync_delete(self, key: str) -> None:
        """Remove a value from cache synchronously."""
        try:
            self._store.pop(key, None)
        except Exception as e:
            logger.exception(f"Cache delete error: {e}")
