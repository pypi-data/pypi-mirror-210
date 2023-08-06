"""Flask resources that implement the REST API using binary as backend.
"""

from flask_restful import Api
from flask_apispec import FlaskApiSpec
from . import icons
from ..utils import register_resource


def add_resources(api: Api, apidoc: FlaskApiSpec):
    # Save/load icons
    register_resource(icons.Icons, "/icons", api, apidoc)
    register_resource(icons.Icon, "/icon/<string:identifier>", api, apidoc)
