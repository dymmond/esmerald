import pytest

pytestmark = pytest.mark.anyio


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


async def test_esmerald_redis_cache(client, redis_settings) -> None:
    """Test cache operations in Esmerald routes with RedisCache."""
    client.app.settings_module = redis_settings
    key, value = "redis_api_key", "cached_value"

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
