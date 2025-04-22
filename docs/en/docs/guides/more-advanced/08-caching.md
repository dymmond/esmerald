# Caching in Esmerald

This guide explains how to implement powerful caching in Esmerald using in-memory and Redis backends.
It walks you through setting up cache decorators, backend configurations, and cache invalidation strategies.

---

## What is Caching?

Caching is the process of storing data in a temporary storage layer (cache) so that future requests for that data can
be served faster.

### Benefits
- Reduces database and computation load
- Improves application performance
- Enables predictable performance at scale

---

## Caching in Esmerald

Esmerald provides a native `@cache()` decorator that can be applied to any function-based handler to cache its result.

The decorator supports multiple backends and time-to-live (TTL) settings.

---

## Basic Usage with In-Memory Cache

```python
from esmerald.utils.decorators import cache
from esmerald.responses import JSONResponse
from esmerald import get

@get("/cached")
@cache(ttl=60)  # Cache result for 60 seconds
def cached_route() -> JSONResponse:
    return JSONResponse({"message": "This is cached."})
```

This example caches the return value for 60 seconds using the default in-memory backend.

---

## Using Redis as a Backend

To use Redis, first install the required library:

```bash
pip install redis
```

Then configure Esmerald to use Redis:

```python
from esmerald.conf import EsmeraldAPISettings
from esmerald.core.caches.redis import RedisCache
from esmerald.core.protocols.cache import CacheBackend


class Settings(EsmeraldAPISettings):
    cache_backend: CacheBackend = RedisCache("redis://localhost:6379")
```

Now all `@cache()` calls use Redis automatically.

---

## Custom TTL and Backend

You can override the default backend or TTL at the decorator level:

```python
from esmerald.core.caches.memory import InMemoryCache
from esmerald.utils.decorators import cache

@get("/override")
@cache(ttl=10, backend=InMemoryCache())
def custom_cache() -> dict:
    return {"status": "fresh data"}
```

---

## Automatic Cache Key Generation

Esmerald automatically generates cache keys based on the function's name and arguments.
You can customize this behavior by writing a custom key builder.

---

## Building Custom Cache Backends

You can implement your own cache backend by subclassing `BaseCacheBackend`.

```python
from esmerald.core.protocols.cache import CacheBackend


class CustomCache(CacheBackend):
    async def get(self, key):
        ...

    async def set(self, key, value, ttl):
        ...

    async def delete(self, key):
        ...
```

---

## Best Practices

- Use TTLs that reflect how often your data changes
- Prefer Redis for multi-instance deployments
- Invalidate caches explicitly when needed
- Avoid caching sensitive or user-specific data unless securely scoped

---

## Summary

✅ Esmerald supports in-memory and Redis caching
✅ Decorator-based usage makes caching declarative
✅ Custom backends and TTLs are supported
✅ Encoders ensure correct serialization for cached content
✅ Hooks enable flexible cache invalidation strategies
