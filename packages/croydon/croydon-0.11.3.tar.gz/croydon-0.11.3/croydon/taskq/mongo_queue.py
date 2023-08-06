import asyncio
from typing import AsyncGenerator
from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo import ReturnDocument
from .base_queue import BaseQueue
from .types import TBaseTask
from ..config import MongoQueueConfig
from ..util import now
from ..context import ctx


class MongoQueue(BaseQueue):
    _cfg: MongoQueueConfig
    _initialised: bool = False

    def __init__(self, cfg: MongoQueueConfig):
        super().__init__()
        self._cfg = cfg

    async def initialise(self):
        await self.ensure_indexes()
        await self.cleanup()

    async def ensure_indexes(self):
        ctx.log.info("setting up indexes for task queue")
        coll = self.tasks_collection
        await coll.create_index("state")
        await coll.create_index("id")

    async def cleanup(self):
        ctx.log.info("cleaning up task queue")
        old_ts = now() - self._cfg.keep_done_tasks_for
        coll = self.tasks_collection
        res = await coll.delete_many(
            {
                "state": {"$in": ["error", "done"]},
                "created_at": {"$lt": old_ts},
            }
        )
        ctx.log.info("cleaning up completed, %d tasks removed", res.deleted_count)

    @property
    def tasks_collection(self) -> AsyncIOMotorCollection:
        return ctx.db.meta.conn[self._cfg.tasks_collection]

    async def enqueue(self, task: TBaseTask) -> bool:
        if not self._initialised:
            await self.initialise()
        super().enqueue(task)
        coll = self.tasks_collection
        doc = task.to_message()
        await coll.insert_one(doc)
        await coll.find_one_and_update(
            {"id": task.id, "state": "new"},
            {"$set": {"state": "published"}},
        )
        task.state = "published"
        return True

    async def set_task_done(self, task: TBaseTask, status_message: str = "ok") -> bool:
        if not self._initialised:
            await self.initialise()
        super().set_task_done(task, status_message)
        coll = self.tasks_collection
        doc = await coll.find_one_and_update(
            {"id": task.id},
            {"$set": {"state": "done", "status_message": status_message}},
            return_document=ReturnDocument.AFTER,
        )
        task.state = doc["state"]
        task.status_message = doc["status_message"]
        return True

    async def tasks(self, no_block: bool = False) -> AsyncGenerator[TBaseTask, None]:
        from .task import BaseTask

        ctx.log.info(f"entering tasks queue loop, registry={BaseTask.REGISTRY}")
        if not self._initialised:
            await self.initialise()

        coll = self.tasks_collection

        next_cleanup = now() + self._cfg.cleanup_interval

        while True:
            doc = await coll.find_one_and_update(
                {"state": "published"},
                {"$set": {"state": "picked_up"}},
                return_document=ReturnDocument.AFTER,
            )
            if doc:
                task = BaseTask.from_message(doc)
                ctx.log.debug(f"yielding task {task}")
                yield task
                continue

            if now() > next_cleanup:
                await self.cleanup()
                next_cleanup = now() + self._cfg.cleanup_interval

            if no_block:
                return

            await asyncio.sleep(0.1)
