"""Flask resources that implement the REST API.
"""

from flask import current_app
from flask_restful import Api
from flask_apispec import FlaskApiSpec, doc, marshal_with

from . import json
from . import binary
from . import events
from . import utils


class Home(utils.Resource):
    @doc(summary="Ewoks workflow React client")
    @marshal_with(None, code=200)
    def get(self):
        return current_app.send_static_file("index.html")


def add_resources(api: Api, apidoc: FlaskApiSpec):
    """Currently only one resource backend is supported: file system"""
    utils.register_resource(Home, "/", api, apidoc)
    json.add_resources(api, apidoc)
    binary.add_resources(api, apidoc)
    events.add_resources(api, apidoc)
