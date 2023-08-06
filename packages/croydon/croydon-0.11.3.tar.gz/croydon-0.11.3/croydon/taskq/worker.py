import asyncio
from abc import abstractmethod, ABC
from .types import TBaseTask
from .. import ctx


class BaseWorker(ABC):

    @abstractmethod
    async def run_task(self, task: TBaseTask) -> None: ...

    async def run(self):
        try:
            async for task in ctx.queue.tasks():
                ctx.log.debug("worker accepted task %s", task)
                await self.run_task(task)
        except asyncio.CancelledError:
            pass
