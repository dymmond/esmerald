import pytest

from esmerald.conf import settings
from esmerald.testclient import override_settings


def test_esmerald_memory_cache(client) -> None:
    """Test cache operations in Esmerald routes with MemoryCache."""
    key, value = "api_test_key", "hello_esmerald"

    response = client.get(f"/set-cache/{key}/{value}")
    assert response.status_code == 200
    assert response.json() == "Cached"

    response = client.get(f"/cache/{key}")
    assert response.status_code == 200
    assert response.json() == value

    response = client.get(f"/delete-cache/{key}")
    assert response.status_code == 200
    assert response.json() == "Deleted"

    response = client.get(f"/cache/{key}")
    assert response.status_code == 200
    assert response.text == ""


@pytest.mark.asyncio
async def xtest_esmerald_redis_cache(redis_cache, client) -> None:
    """Test cache operations in Esmerald routes with RedisCache."""

    with override_settings(cache_backend=await redis_cache):
        settings.cache_backend = redis_cache

        key, value = "redis_api_key", "cached_value"

        response = await client.get(f"/set-cache/{key}/{value}")
        assert response.status_code == 200
        assert response.json() == "Cached"

        response = await client.get(f"/cache/{key}")
        assert response.status_code == 200
        assert response.json() == value

        response = await client.get(f"/delete-cache/{key}")
        assert response.status_code == 200
        assert response.json() == "Deleted"

        response = await client.get(f"/cache/{key}")
        assert response.status_code == 200
        assert response.json() is None
