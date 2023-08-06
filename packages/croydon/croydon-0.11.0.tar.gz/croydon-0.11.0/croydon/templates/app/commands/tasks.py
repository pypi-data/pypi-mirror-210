from croydon import ctx
from croydon.command import Command
from app.tasks.worker import Worker


class Tasks(Command):

    NAME = "tasks"
    HELP = "run task processing worker"

    async def run_async(self) -> None:
        from app import app
        app.initialise()

        wrk = Worker()
        future = wrk.run()
        try:
            await future
        except KeyboardInterrupt:
            ctx.log.info("SIGINT received, terminating worker")
