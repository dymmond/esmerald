from esmerald import EsmeraldAPISettings
from esmerald.caches.redis import RedisCache


class CustomSettings(EsmeraldAPISettings):
    cache_backend = RedisCache(redis_url="redis://localhost:6379")
