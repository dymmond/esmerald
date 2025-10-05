from ravyn import get
from ravyn.core.caches.redis import RedisCache
from ravyn.utils.decorators import cache

redis_cache = RedisCache(redis_url="redis://localhost:6379")


@get("/data/{key}")
@cache(backend=redis_cache, ttl=30)
async def fetch_data(key: str) -> dict:
    return {"key": key, "value": key[::-1]}  # Simulating an expensive operation
