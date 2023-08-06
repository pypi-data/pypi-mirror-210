from typing import Optional, Any, Dict
from .abc import AbstractCache

STATIC_CACHE: Dict[str, Any] = {}


class SimpleCache(AbstractCache):
    NAME = "SimpleCache"

    async def initialise(self) -> None:
        pass

    async def get(self, key: str) -> Optional[Any]:
        return STATIC_CACHE.get(key)

    async def set(self, key: str, value: Any) -> None:
        STATIC_CACHE[key] = value

    async def has(self, key: str) -> bool:
        return key in STATIC_CACHE

    async def delete(self, key: str) -> bool:
        had = await self.has(key)
        if had:
            del STATIC_CACHE[key]
        return had
