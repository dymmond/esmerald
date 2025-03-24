import asyncio

import pytest

from .conftest import CACHE_TTL


def test_memory_cache_basic_operations(memory_cache) -> None:
    """Test setting, getting, and deleting values in MemoryCache."""
    key, value = "test_key", {"data": 123}

    memory_cache.sync_set(key, value, CACHE_TTL)
    assert memory_cache.sync_get(key) == value

    memory_cache.sync_delete(key)
    assert memory_cache.sync_get(key) is None


@pytest.mark.asyncio
async def test_redis_cache_basic_operations(redis_cache) -> None:
    """Test setting, getting, and deleting values in RedisCache."""
    key, value = "redis_key", {"number": 42}

    await redis_cache.set(key, value, CACHE_TTL)
    assert await redis_cache.get(key) == value

    await redis_cache.delete(key)
    assert await redis_cache.get(key) is None


@pytest.mark.asyncio
async def test_memory_cache_ttl_expiry(memory_cache) -> None:
    """Ensure MemoryCache entries expire correctly."""
    key, value = "expiring_key", "expire_me"

    await memory_cache.set(key, value, 1)  # 1-second TTL
    assert await memory_cache.get(key) == value

    await asyncio.sleep(1.5)  # Wait for TTL to expire
    assert await memory_cache.get(key) is None


@pytest.mark.asyncio
async def test_redis_cache_ttl_expiry(redis_cache) -> None:
    """Ensure RedisCache entries expire correctly."""
    key, value = "redis_expiry", "will_disappear"

    await redis_cache.set(key, value, 1)
    assert await redis_cache.get(key) == value

    await asyncio.sleep(1.5)
    assert await redis_cache.get(key) is None
