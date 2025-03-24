import json
import os
from typing import Any

from esmerald.protocols.cache import CacheBackend


class FileCache(CacheBackend):
    def __init__(self, directory: str = "cache_files") -> None:
        self.directory = directory
        os.makedirs(directory, exist_ok=True)

    async def get(self, key: str) -> Any | None:
        filepath = os.path.join(self.directory, key)
        if os.path.exists(filepath):
            with open(filepath) as f:
                return json.load(f)
        return None

    async def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        filepath = os.path.join(self.directory, key)
        with open(filepath, "w") as f:
            json.dump(value, f)

    async def delete(self, key: str) -> None:
        filepath = os.path.join(self.directory, key)
        if os.path.exists(filepath):
            os.remove(filepath)
