import uvicorn
from argparse import ArgumentParser, Namespace
from croydon.command import Command


class Prod(Command):

    NAME = "prod"
    HELP = "run production server"
    ASYNC_RUN = False

    host: str
    port: int

    async def setup(self, args: Namespace) -> None:
        self.host = args.host
        self.port = args.port

    def run_sync(self):
        uvicorn.run("app:app", host=self.host, port=self.port, reload=False)

    def init_argument_parser(self, parser: ArgumentParser) -> None:
        parser.add_argument("-P", "--port", type=int, help="port to listen on", default=8000)
        parser.add_argument("-H", "--host", type=str, help="host to bind to", default="127.0.0.1")
