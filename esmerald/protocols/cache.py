from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class CacheBackend(ABC):
    """Protocol for caches backends, ensuring compatibility with the decorator."""

    @abstractmethod
    async def get(self, key: str) -> Any | None:
        """Retrieve a cached value by key."""
        raise NotImplementedError("Cache backend must implement get method.")

    @abstractmethod
    async def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Store a value in the caches with an optional TTL."""
        raise NotImplementedError("Cache backend must implement set method.")

    @abstractmethod
    async def delete(self, key: str) -> None:
        """Remove a value from the caches."""
        raise NotImplementedError("Cache backend must implement delete method.")
