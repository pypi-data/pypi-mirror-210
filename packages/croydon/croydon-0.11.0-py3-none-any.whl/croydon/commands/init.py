import os.path
import shutil
import sys
from argparse import ArgumentParser, Namespace
from ..command import Command


class Init(Command):

    NAME = "init"
    HELP = "initialize a new project in the current directory"
    ASYNC_RUN = False

    _quiet: bool = False
    _overwrite: bool = False

    def init_argument_parser(self, parser: ArgumentParser) -> None:
        parser.add_argument("-q", "--quiet", action="store_true", default=False, help="disable progress messages")
        parser.add_argument("-w", "--overwrite", action="store_true", default=False,
                            help="overwrite files and directories if they exist")

    async def setup(self, args: Namespace) -> None:
        self._quiet = args.quiet
        self._overwrite = args.overwrite

    def process_directory(self, dir_name: str):
        curr_dir = os.path.abspath(os.curdir)
        for filename in os.listdir(dir_name):
            if filename == "__pycache__" or filename.endswith(".pyc"):
                continue
            full_filename = os.path.join(dir_name, filename)
            if os.path.isdir(full_filename):
                new_dir = os.path.join(curr_dir, filename)
                if not self._quiet:
                    print(f"creating new directory {new_dir}")

                create_dir = True
                if os.path.isdir(new_dir):
                    print(f"file or directory {new_dir} already exists")
                    if self._overwrite:
                        create_dir = False
                    else:
                        sys.exit(1)

                if create_dir:
                    os.makedirs(new_dir)

                if not self._quiet:
                    print(f"jumping into {new_dir}")
                os.chdir(new_dir)
                self.process_directory(full_filename)
                if not self._quiet:
                    print(f"jumping back into {curr_dir}")
                os.chdir(curr_dir)
            else:
                new_filename = os.path.abspath(os.path.join(curr_dir, filename))
                if os.path.exists(new_filename) and not self._overwrite:
                    print(f"file or directory {new_filename} already exists")
                    sys.exit(1)
                if not self._quiet:
                    print(f"copying {full_filename} to {new_filename}")
                shutil.copy(full_filename, new_filename)

    def run_sync(self) -> None:

        init_command_dir = os.path.dirname(__file__)
        croydon_dir = os.path.abspath(os.path.join(init_command_dir, ".."))
        templates_dir = os.path.join(croydon_dir, "templates")
        if not self._quiet:
            print(f"using templates directory {templates_dir}")
        self.process_directory(templates_dir)
