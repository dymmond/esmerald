from __future__ import annotations

import anyio

from esmerald.protocols.cache import CacheBackend

try:
    import aioredis
    import redis
except ImportError:
    aioredis = None
    redis = None

from typing import Any

import orjson


class RedisCache(CacheBackend):
    """Redis caches backend supporting both sync and async operations with orjson serialization."""

    def __init__(self, redis_url: str) -> None:
        if aioredis is None or redis is None:
            raise ImportError(
                "You must install 'aioredis' and 'redis' to use this caches backend."
            )

        self.redis_url: str = redis_url
        self.sync_client: redis.Redis = redis.Redis.from_url(redis_url, decode_responses=False)
        self.async_client: aioredis.Redis | None = None  # Lazy initialization

    async def _get_async_client(self) -> aioredis.Redis:
        """Lazy initialization for the async Redis client."""
        if self.async_client is None:
            self.async_client = await aioredis.from_url(self.redis_url, decode_responses=False)  # type: ignore[no-untyped-call]
        return self.async_client

    async def get(self, key: str) -> Any | None:
        """Retrieve a value from caches asynchronously."""
        client = await self._get_async_client()
        value = await client.get(key)
        return orjson.loads(value) if value is not None else None

    async def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Set a value in the caches asynchronously with an optional TTL."""
        client = await self._get_async_client()
        data: bytes = orjson.dumps(value)

        if ttl:
            await client.setex(key, ttl, data)
        else:
            await client.set(key, data)

    async def delete(self, key: str) -> None:
        """Remove a value from the caches asynchronously."""
        client = await self._get_async_client()
        await client.delete(key)

    def sync_get(self, key: str) -> Any | None:
        """Retrieve a value from the caches synchronously (thread-safe with AnyIO)."""

        def get_cached() -> bytes | None:
            return self.sync_client.get(key)  # type: ignore

        value = anyio.to_thread.run_sync(get_cached)
        return orjson.loads(value) if value is not None else None  # type: ignore

    def sync_set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Store a value in the caches synchronously (thread-safe with AnyIO)."""

        def set_cached() -> None:
            data: bytes = orjson.dumps(value)
            if ttl:
                self.sync_client.setex(key, ttl, data)
            else:
                self.sync_client.set(key, data)

        anyio.to_thread.run_sync(set_cached)  # type: ignore

    def sync_delete(self, key: str) -> None:
        """Delete a caches entry synchronously (thread-safe with AnyIO)."""

        def delete_cached() -> None:
            self.sync_client.delete(key)

        anyio.to_thread.run_sync(delete_cached)  # type: ignore
