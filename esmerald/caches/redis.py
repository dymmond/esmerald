from __future__ import annotations

import asyncio
import time
from typing import Any

import anyio
import orjson

from esmerald.protocols.cache import CacheBackend

try:
    import redis.asyncio as redis
except ImportError:
    redis = None


class RedisCache(CacheBackend):
    """Redis cache backend using asyncio with orjson serialization.

    This class provides an asynchronous and thread-safe cache implementation
    using Redis as the backend. It supports automatic connection management
    for multiple event loops and both synchronous and asynchronous methods.

    Attributes:
        redis_url (str): The Redis connection URL.
        _async_clients (dict[int, redis.Redis]): A mapping of event loop IDs to Redis clients.
    """

    def __init__(self, redis_url: str) -> None:
        """Initializes the Redis cache backend.

        Args:
            redis_url (str): The Redis connection URL.

        Raises:
            ImportError: If the `redis` package is not installed.
        """
        if redis is None:
            raise ImportError("You must install 'redis' to use this cache backend.")
        self.redis_url: str = redis_url
        self._async_clients: dict[int, redis.Redis] = {}  # Store clients per event loop

    @property
    def async_client(self) -> redis.Redis:
        """Returns the Redis client instance for the current event loop.

        Ensures that each event loop gets its own dedicated Redis client to
        prevent conflicts when working in multi-threaded environments.

        Returns:
            redis.Redis: The Redis client instance for the current event loop.
        """
        loop_id = id(asyncio.get_running_loop())

        if loop_id not in self._async_clients:
            self._async_clients[loop_id] = redis.Redis.from_url(
                self.redis_url, decode_responses=False
            )

        return self._async_clients[loop_id]

    @async_client.setter
    def async_client(self, client: redis.Redis) -> None:
        """Sets a custom Redis client for the current event loop.

        This is mainly useful for testing, allowing dependency injection of
        a mock Redis instance.

        Args:
            client (redis.Redis): A Redis client instance.

        Raises:
            ValueError: If `client` is not an instance of `redis.Redis`.
        """
        loop_id = id(asyncio.get_running_loop())

        if not isinstance(client, redis.Redis):
            raise ValueError("async_client must be an instance of redis.Redis")

        self._async_clients[loop_id] = client

    async def get(self, key: str) -> Any | None:
        """Retrieves a value from the Redis cache asynchronously.

        Args:
            key (str): The cache key.

        Returns:
            Any | None: The deserialized value if found, otherwise `None`.
        """
        value = await self.async_client.get(key)
        return orjson.loads(value) if value is not None else None

    async def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Stores a value in the Redis cache asynchronously.

        Args:
            key (str): The cache key.
            value (Any): The value to be cached.
            ttl (int | None, optional): Time-to-live in seconds. If `None`, the value never expires.
        """
        data: bytes = orjson.dumps(value)
        if ttl:
            await self.async_client.setex(key, ttl, data)
        else:
            await self.async_client.set(key, data)

    async def delete(self, key: str) -> None:
        """Deletes a value from the Redis cache asynchronously.

        Args:
            key (str): The cache key to delete.
        """
        await self.async_client.delete(key)

    async def close(self) -> None:
        """Closes all Redis client connections.

        Ensures all event loop-specific Redis clients are properly shut down
        and removed from the internal registry.
        """
        for client in self._async_clients.values():
            await client.aclose()
        self._async_clients.clear()

    def sync_get(self, key: str) -> Any | None:
        """Retrieves a value from the Redis cache synchronously.

        This method wraps the asynchronous `get` method inside a thread-safe
        AnyIO execution to allow usage in synchronous contexts.

        Args:
            key (str): The cache key.

        Returns:
            Any | None: The deserialized value if found, otherwise `None`.
        """

        def get_cached() -> bytes | None | Any:
            return anyio.run(self.async_client.get, key)

        value = anyio.to_thread.run_sync(get_cached)
        return orjson.loads(value) if value is not None else None  # type: ignore

    def sync_set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Stores a value in the Redis cache synchronously.

        This method wraps the asynchronous `set` method inside a thread-safe
        AnyIO execution to allow usage in synchronous contexts.

        Args:
            key (str): The cache key.
            value (Any): The value to be cached.
            ttl (int | None, optional): Time-to-live in seconds. If `None`, the value never expires.
        """

        def set_cached() -> None:
            data: bytes = orjson.dumps(value)
            if ttl:
                anyio.run(self.async_client.setex, key, ttl, data)
            else:
                anyio.run(self.async_client.set, key, data)

        anyio.to_thread.run_sync(set_cached)  # type: ignore

    def sync_delete(self, key: str) -> None:
        """Deletes a value from the Redis cache synchronously and ensures it is removed.

        This method wraps the asynchronous `delete` method inside a thread-safe
        AnyIO execution to allow usage in synchronous contexts. It also ensures
        that Redis has actually removed the key before proceeding.

        Args:
            key (str): The cache key to delete.
        """

        def delete_cached() -> None:
            """Runs the deletion and verifies the key is gone."""
            anyio.run(self.async_client.delete, key)

            # Wait until the key is actually removed
            for _ in range(50):  # Retry for up to 5 seconds
                remaining_keys = anyio.run(self.async_client.keys, "*")
                if key.encode() not in remaining_keys:
                    break
                time.sleep(0.1)  # Small delay to let Redis process deletion

        anyio.to_thread.run_sync(delete_cached)  # type: ignore
