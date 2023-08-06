import json
from jupyter_server.base.handlers import APIHandler
from jupyter_server.utils import url_path_join
from tornado.web import authenticated
import os


def setup_handlers(web_app):
    class CurrentUserHandler(APIHandler):
        @authenticated
        def get(self):
            jupyterhub_user = os.environ.get('JUPYTERHUB_USER', '')
            self.finish(json.dumps({"user_name": jupyterhub_user}))

    host_pattern = ".*$"
    app_url_prefix = url_path_join(web_app.settings["base_url"], "codepeers")
    handlers = [
        (url_path_join(app_url_prefix, "current_user"), CurrentUserHandler),
    ]
    web_app.add_handlers(host_pattern, handlers)
