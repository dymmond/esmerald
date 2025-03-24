from __future__ import annotations

from typing import Any, Protocol


class CacheBackend(Protocol):
    """Protocol for cache backends, ensuring compatibility with the decorator."""

    async def get(self, key: str) -> Any | None:
        """Retrieve a cached value by key."""
        ...

    async def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Store a value in the cache with an optional TTL."""
        ...

    async def delete(self, key: str) -> None:
        """Remove a value from the cache."""
        ...
