from croydon.taskq.task import BaseTask


class PingTask(BaseTask[None]):

    TYPE = "BASE_PING"


PingTask.register()
