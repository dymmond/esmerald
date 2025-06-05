from esmerald import EsmeraldSettings
from esmerald.core.caches.redis import RedisCache


class CustomSettings(EsmeraldSettings):
    cache_backend = RedisCache(redis_url="redis://localhost:6379")
