from __future__ import annotations

import logging
import time
from typing import Any

import anyio
import orjson

from esmerald.protocols.cache import CacheBackend

logger = logging.getLogger(__name__)


class InMemoryCache(CacheBackend):
    """Thread-safe in-memory cache with TTL support, matching RedisCache API.

    This cache implementation stores key-value pairs in memory using a dictionary.
    It supports expiration (TTL) and provides both asynchronous and synchronous
    methods to interact with the cache.

    Attributes:
        _store (dict[str, tuple[bytes, float | None]]):
            Internal dictionary where keys are stored as strings and values
            are tuples containing serialized data and an optional expiration timestamp.
    """

    def __init__(self) -> None:
        """Initializes the in-memory cache."""
        self._store: dict[str, tuple[bytes, float | None]] = {}

    async def get(self, key: str) -> Any | None:
        """Retrieve a value from cache asynchronously.

        This method wraps the synchronous `sync_get` method using AnyIO's
        thread execution to allow safe access in async contexts.

        Args:
            key (str): The cache key.

        Returns:
            Any | None: The deserialized value if found and not expired, otherwise `None`.
        """
        return await anyio.to_thread.run_sync(self.sync_get, key)

    async def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Store a value in cache asynchronously with an optional TTL.

        This method wraps the synchronous `sync_set` method using AnyIO's
        thread execution to allow safe access in async contexts.

        Args:
            key (str): The cache key.
            value (Any): The value to be cached.
            ttl (int | None, optional): Time-to-live in seconds. If `None`, the value never expires.
        """
        await anyio.to_thread.run_sync(self.sync_set, key, value, ttl)

    async def delete(self, key: str) -> None:
        """Remove a value from cache asynchronously.

        This method wraps the synchronous `sync_delete` method using AnyIO's
        thread execution to allow safe access in async contexts.

        Args:
            key (str): The cache key to delete.
        """
        await anyio.to_thread.run_sync(self.sync_delete, key)

    def sync_get(self, key: str) -> Any | None:
        """Retrieve a value from cache synchronously.

        This method directly accesses the internal dictionary `_store` to
        fetch the cached value. It checks if the key exists and whether
        its TTL has expired before returning the value.

        Args:
            key (str): The cache key.

        Returns:
            Any | None: The deserialized value if found and not expired, otherwise `None`.

        Raises:
            Exception: If an unexpected error occurs while retrieving the value.
        """
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
        """Store a value in cache synchronously with an optional TTL.

        The value is serialized using `orjson` and stored in `_store` along with
        an expiration timestamp if TTL is provided.

        Args:
            key (str): The cache key.
            value (Any): The value to be cached.
            ttl (int | None, optional): Time-to-live in seconds. If `None`, the value never expires.

        Raises:
            Exception: If an error occurs while serializing or storing the value.
        """
        try:
            expiry = time.time() + ttl if ttl else None
            self._store[key] = (orjson.dumps(value), expiry)
        except Exception as e:
            logger.exception(f"Cache set error: {e}")

    def sync_delete(self, key: str) -> None:
        """Remove a value from cache synchronously.

        This method directly removes the key from `_store`, if it exists.

        Args:
            key (str): The cache key to delete.

        Raises:
            Exception: If an error occurs while deleting the key.
        """
        try:
            self._store.pop(key, None)
            time.sleep(0.1)
        except Exception as e:
            logger.exception(f"Cache delete error: {e}")
