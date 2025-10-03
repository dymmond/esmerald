from ravyn import RavynSettings
from ravyn.core.caches.redis import RedisCache


class CustomSettings(RavynSettings):
    cache_backend = RedisCache(redis_url="redis://localhost:6379")
