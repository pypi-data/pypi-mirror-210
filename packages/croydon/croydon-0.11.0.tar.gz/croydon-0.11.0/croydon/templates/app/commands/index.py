import os
import importlib
import inspect
from typing import Dict, Type
from croydon import ctx
from croydon.models.storable_model import StorableModel
from croydon.models.counter import Counter
from croydon.command import Command


class Index(Command):

    NAME = "index"
    HELP = "Create indexes for the application models"

    async def run_async(self) -> None:
        from app import app
        app.initialise()

        models_dir = os.path.join(ctx.project_dir, "app/models")
        classes: Dict[str, Type['StorableModel']] = {
            "Counter": Counter
        }

        for filename in os.listdir(models_dir):
            if filename.endswith(".py") and not filename.startswith("__"):
                modulename = filename[:-3]
                module = importlib.import_module(f"app.models.{modulename}")

                for attr in dir(module):
                    cls = getattr(module, attr)
                    if inspect.isclass(cls) and issubclass(cls, StorableModel) and not cls is StorableModel:
                        classes[cls.__name__] = cls

        for cls_name, cls in classes.items():
            ctx.log.debug(f"Creating index for model {cls_name}")
            await cls.ensure_indexes(loud=True)
