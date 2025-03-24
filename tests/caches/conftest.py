from __future__ import annotations

import pytest
from esmerald import Esmerald, Gateway, get
from esmerald.testclient import EsmeraldTestClient
from esmerald.conf import settings
from esmerald.protocols.cache import CacheBackend

from typing import Any

from esmerald.caches.memory import InMemoryCache
from esmerald.caches.redis import RedisCache

try:
    import aioredis
except ImportError:
    aioredis = None

CACHE_TTL = 10  # 2 seconds for quick TTL tests


@pytest.fixture(scope="function")
def memory_cache() -> InMemoryCache:
    """Fixture providing a fresh InMemoryCache instance."""
    return InMemoryCache()


@pytest.fixture(scope="function")
async def redis_cache() -> RedisCache:
    """Fixture providing a fresh RedisCache instance."""
    if aioredis is None:
        pytest.skip("aioredis is required for RedisCache tests")

    redis = await aioredis.from_url("redis://localhost", decode_responses=False)
    await redis.flushdb()  # Ensure clean test environment
    return RedisCache("redis://localhost")


@pytest.fixture(scope="function")
def esmerald_app(memory_cache: CacheBackend) -> Esmerald:
    """Fixture for an Esmerald app with caching."""
    settings.cache_backend = memory_cache

    @get("/cache/{key}")
    async def get_cache_value(key: str) -> Any:
        return await settings.cache_backend.get(key)

    @get("/set-cache/{key}/{value}")
    async def set_cache_value(key: str, value: str) -> str:
        await settings.cache_backend.set(key, value, CACHE_TTL)
        return "Cached"

    @get("/delete-cache/{key}")
    async def delete_cache_value(key: str) -> str:
        await settings.cache_backend.delete(key)
        return "Deleted"

    return Esmerald(
        routes=[
            Gateway(handler=get_cache_value),
            Gateway(handler=set_cache_value),
            Gateway(handler=delete_cache_value),
        ]
    )


@pytest.fixture(scope="function")
def client(esmerald_app: Esmerald) -> EsmeraldTestClient:
    """Fixture for an Esmerald test client."""
    return EsmeraldTestClient(esmerald_app)
