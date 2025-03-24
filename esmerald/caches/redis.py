from __future__ import annotations

import asyncio
from typing import Any

import anyio
import orjson

from esmerald.protocols.cache import CacheBackend

try:
    import redis.asyncio as redis
except ImportError:
    redis = None


class RedisCache(CacheBackend):
    """Redis cache backend using asyncio with orjson serialization."""

    def __init__(self, redis_url: str) -> None:
        if redis is None:
            raise ImportError("You must install 'redis' to use this cache backend.")
        self.redis_url: str = redis_url
        self._async_clients: dict[int, redis.Redis] = {}  # Store clients per event loop

    @property
    def async_client(self) -> redis.Redis:
        """Ensure a separate Redis client per event loop to prevent loop conflicts."""
        loop_id = id(asyncio.get_running_loop())  # ✅ FIXED

        if loop_id not in self._async_clients:
            self._async_clients[loop_id] = redis.Redis.from_url(
                self.redis_url, decode_responses=False
            )

        return self._async_clients[loop_id]

    @async_client.setter
    def async_client(self, client: redis.Redis) -> None:
        """Set a custom Redis client (useful for testing)."""
        loop_id = id(asyncio.get_running_loop())  # ✅ FIXED

        if not isinstance(client, redis.Redis):
            raise ValueError("async_client must be an instance of redis.Redis")

        self._async_clients[loop_id] = client

    async def get(self, key: str) -> Any | None:
        """Retrieve a value from cache asynchronously."""
        value = await self.async_client.get(key)
        return orjson.loads(value) if value is not None else None

    async def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Set a value in the cache asynchronously with an optional TTL."""
        data: bytes = orjson.dumps(value)
        if ttl:
            await self.async_client.setex(key, ttl, data)
        else:
            await self.async_client.set(key, data)

    async def delete(self, key: str) -> None:
        """Remove a value from the cache asynchronously."""
        await self.async_client.delete(key)

    async def close(self) -> None:
        """Ensure Redis connections are closed properly per event loop."""
        for client in self._async_clients.values():
            await client.aclose()
        self._async_clients.clear()

    def sync_get(self, key: str) -> Any | None:
        """Retrieve a value from cache synchronously (thread-safe with AnyIO)."""

        def get_cached() -> bytes | None | Any:
            return anyio.run(self.async_client.get, key)

        value = anyio.to_thread.run_sync(get_cached)
        return orjson.loads(value) if value is not None else None  # type: ignore

    def sync_set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Store a value in the cache synchronously (thread-safe with AnyIO)."""

        def set_cached() -> None:
            data: bytes = orjson.dumps(value)
            if ttl:
                anyio.run(self.async_client.setex, key, ttl, data)
            else:
                anyio.run(self.async_client.set, key, data)

        anyio.to_thread.run_sync(set_cached)  # type: ignore

    def sync_delete(self, key: str) -> None:
        """Delete a cache entry synchronously (thread-safe with AnyIO)."""

        def delete_cached() -> None:
            anyio.run(self.async_client.delete, key)

        anyio.to_thread.run_sync(delete_cached)  # type: ignore
