from croydon.taskq.worker import BaseWorker
from croydon.taskq.types import TBaseTask


class Worker(BaseWorker):

    async def run_task(self, task: TBaseTask) -> None:
        raise NotImplemented(
            "extend Worker class in app.tasks.worker to teach it "
            "how to process tasks of various types"
        )
