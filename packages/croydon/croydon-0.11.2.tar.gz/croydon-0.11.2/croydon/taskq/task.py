import json
from typing import Dict, Optional, Generic, Self
from datetime import datetime

from ..util import uuid4_string, now
from ..context import ctx
from .types import TTaskData, TBaseTaskType, TBaseTask, Message, TState


class BaseTask(Generic[TTaskData]):

    TYPE: str = "base"
    REGISTRY: Dict[str, TBaseTaskType] = {}

    id: str
    data: TTaskData
    created_at: datetime
    state: TState
    status_message: str
    _received_by: Optional[str]

    def __init__(self,
                 data: TTaskData,
                 task_id: Optional[str] = None,
                 created_at: Optional[datetime] = None,
                 state: TState = "new",
                 status_message: str = "") -> None:
        self.id = task_id or uuid4_string()
        self.data = data
        self.created_at = created_at or now()
        self.state = state
        self.status_message = status_message

    def to_message(self) -> Message:
        return Message(
            id=self.id,
            type=self.TYPE,
            data=json.dumps(self.data),
            created_at=self.created_at,
            state=self.state,
            status_message=self.status_message,
        )

    def _get_received_by(self) -> Optional[str]:
        return self._received_by

    def _set_received_by(self, value: str):
        self._received_by = value

    received_by = property(_get_received_by, _set_received_by)

    @property
    def is_received(self) -> bool:
        return self._received_by is not None

    async def publish(self) -> bool:
        return await ctx.queue.enqueue(self)

    async def done(self, status_message: str = "ok") -> None:
        return await ctx.queue.set_task_done(self, status_message)

    @classmethod
    def from_message(cls, msg: Message) -> TBaseTask:
        if "data" not in msg:
            ctx.log.error("malformed message, no data field: %s", msg)
        task_id = msg["id"]
        task_type = msg["type"]
        created_at = msg["created_at"]
        state = msg["state"]
        status_message = msg["status_message"]
        data = json.loads(msg["data"])

        ctx.log.debug(f"processing queue message with task type {task_type}")
        if task_type in cls.REGISTRY:
            task_class = cls.REGISTRY[task_type]
            ctx.log.debug(f"task type {task_type} is in registry, task class is {task_class}")
        else:
            task_class = cls
            ctx.log.debug(f"task type {task_type} is NOT in registry, task class is {task_class}")

        return task_class(
            data=data,
            task_id=task_id,
            created_at=created_at,
            state=state,
            status_message=status_message
        )

    @classmethod
    def register(cls):
        ctx.log.info("Registering task type %s", cls.TYPE)
        BaseTask.REGISTRY[cls.TYPE] = cls

    def __str__(self):
        return (
            f"<{self.__class__.__name__} {self.TYPE} id={self.id} data={json.dumps(self.data)} "
            + f"created_at={self.created_at} state={self.state} status_message=\"{self.status_message}\">"
        )

    def __repr__(self):
        return self.__str__()
