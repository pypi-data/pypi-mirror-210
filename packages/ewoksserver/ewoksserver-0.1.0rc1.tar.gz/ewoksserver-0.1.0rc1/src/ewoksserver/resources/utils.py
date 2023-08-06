from typing import Type
from flask_restful import Api
from flask_apispec import FlaskApiSpec
from flask_restful import Resource as _Resource
from flask_apispec import MethodResource


class Resource(MethodResource, _Resource):
    pass


def register_resource(
    resource: Type[Resource], path: str, api: Api, apidoc: FlaskApiSpec
):
    api.add_resource(resource, path)
    apidoc.register(resource)
