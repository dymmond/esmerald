from esmerald import get
from esmerald.utils.decorators import cache

file_cache = FileCache()


@get("/file-cache/{data}")
@cache(backend=file_cache, ttl=60)
async def file_cached_endpoint(data: str) -> dict:
    return {"data": data, "cached": True}
