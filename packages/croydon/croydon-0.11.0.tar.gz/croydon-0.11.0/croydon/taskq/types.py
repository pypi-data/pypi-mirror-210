from typing import TypeVar, TYPE_CHECKING, Type, TypedDict, Literal
from datetime import datetime
if TYPE_CHECKING:
    from .base_queue import BaseQueue
    from .task import BaseTask


TBaseQueue = TypeVar("TBaseQueue", bound="BaseQueue")
TBaseTask = TypeVar("TBaseTask", bound="BaseTask")
TBaseTaskType = Type[TBaseTask]
TTaskData = TypeVar("TTaskData")

TState = Literal["new", "published", "picked_up", "done", "error"]


class Message(TypedDict):
    id: str
    type: str
    data: str
    created_at: datetime
    state: TState
    status_message: str
