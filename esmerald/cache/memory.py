from __future__ import annotations

import time
from typing import Any

from loguru import logger

from esmerald.protocols.cache import CacheBackend


class InMemoryCache(CacheBackend):
    """Simple in-memory cache with TTL support."""

    def __init__(self) -> None:
        self._store: dict[str, tuple[Any, float | None]] = {}

    async def get(self, key: str) -> Any | None:
        """Retrieve a value from cache if valid."""
        try:
            data = self._store.get(key)
            if not data:
                return None

            value, expiry = data
            if expiry is not None and expiry < time.time():
                # Expired, remove it
                await self.delete(key)
                return None

            return value
        except Exception as e:
            logger.exception(f"Cache get error: {e}")
            return None

    async def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Set a value in the cache with an optional TTL."""
        try:
            expiry = time.time() + ttl if ttl else None
            self._store[key] = (value, expiry)
        except Exception as e:
            logger.exception(f"Cache set error: {e}")

    async def delete(self, key: str) -> None:
        """Remove a value from the cache."""
        try:
            self._store.pop(key, None)
        except Exception as e:
            logger.exception(f"Cache delete error: {e}")
