from typing import AsyncGenerator
from abc import abstractmethod, ABC
from .task import BaseTask
from .types import TBaseTask


class BaseQueue(ABC):

    @abstractmethod
    def enqueue(self, task: TBaseTask) -> bool:
        if not isinstance(task, BaseTask):
            raise TypeError("only instances of BaseTask subclasses are allowed")
        return False

    @abstractmethod
    def set_task_done(self, task: TBaseTask, status_message: str = "ok") -> None:
        if not isinstance(task, BaseTask):
            raise TypeError("only instances of BaseTask subclasses are allowed")

    @abstractmethod
    async def tasks(self, no_block: bool = False) -> AsyncGenerator[TBaseTask, None]: ...
