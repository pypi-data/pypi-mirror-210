import asyncio
import importlib
import inspect
import os.path
from argparse import ArgumentParser, Namespace
from typing import Generator, AnyStr, Type, TypeVar, List, Dict


class Command:

    NAME: str
    HELP: str
    ASYNC_RUN: bool = True

    def __init__(self, parser: ArgumentParser) -> None:
        self.init_argument_parser(parser)

    def run(self, args: Namespace) -> None:
        asyncio.run(self.setup(args))
        if self.ASYNC_RUN:
            asyncio.run(self.run_async())
        else:
            self.run_sync()

    async def setup(self, args: Namespace) -> None:
        pass

    def init_argument_parser(self, parser: ArgumentParser) -> None:
        pass

    def run_sync(self) -> None:
        pass

    async def run_async(self) -> None:
        pass


CC = Type[Command]
CI = TypeVar("CI", bound=Command)


def _collect_commands() -> List[CC]:

    search_module_paths = ["croydon.commands", "app.commands"]
    commands: List[CC] = []

    def module_names_in_dir(mod_dir: AnyStr) -> Generator[str, None, None]:
        for filename in os.listdir(mod_dir):
            if filename.endswith(".py"):
                filename = os.path.basename(filename)[:-3]
                yield filename

    for modpath in search_module_paths:
        try:
            base_module = importlib.import_module(modpath)
        except ModuleNotFoundError:
            continue
        for modname in module_names_in_dir(os.path.dirname(base_module.__file__)):
            module = importlib.import_module(f"{modpath}.{modname}")
            for cls in module.__dict__.values():
                if inspect.isclass(cls) and issubclass(cls, Command) and cls is not Command:
                    commands.append(cls)

    commands.sort(key=lambda cmd: cmd.NAME)

    return commands


def main():
    parser = ArgumentParser()
    subparsers = parser.add_subparsers(
        title="command",
        required=True,
        help="command to run",
        dest="command"
    )

    cmd_map: Dict[str, CI] = {}

    for cmd_class in _collect_commands():
        sp = subparsers.add_parser(cmd_class.NAME, help=cmd_class.HELP)
        cmd = cmd_class(sp)
        cmd_map[cmd.NAME] = cmd

    args = parser.parse_args()
    cmd = cmd_map.get(args.command)
    cmd.run(args)
