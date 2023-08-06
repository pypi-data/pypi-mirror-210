"""Flask resources that implement the REST API using the ewoks event database as backend.
"""

from flask_restful import Api
from flask_apispec import FlaskApiSpec
from . import resource
from ..utils import register_resource


def add_resources(api: Api, apidoc: FlaskApiSpec):
    register_resource(resource.ExecutionEvents, "/execution/events", api, apidoc)
