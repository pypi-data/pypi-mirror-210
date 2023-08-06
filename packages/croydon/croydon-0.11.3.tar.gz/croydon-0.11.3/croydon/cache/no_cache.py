from typing import Optional, Any
from .abc import AbstractCache


class NoCache(AbstractCache):
    NAME = "NoCache"

    async def has(self, key: str) -> bool:
        return False

    async def set(self, key: str, value: Any) -> None:
        return

    async def get(self, key: str) -> Optional[Any]:
        return None

    async def delete(self, key: str) -> bool:
        return False

    async def initialise(self) -> None:
        return
