import os.path
from croydon.baseapp import BaseApp


class App(BaseApp):

    def __init__(self):
        app_dir = os.path.abspath(os.path.dirname(__file__))
        project_dir = os.path.abspath(os.path.join(app_dir, ".."))
        super().__init__(project_dir=project_dir)

    def setup_routes(self) -> None:
        from .controllers.api.v1.account import account_ctrl
        self.include_router(account_ctrl)


app = App()
