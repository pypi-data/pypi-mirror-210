"""Flask resources that implement the REST API using json as backend.
"""

from flask_restful import Api
from flask_apispec import FlaskApiSpec
from . import tasks
from . import workflows
from ..utils import register_resource


def add_resources(api: Api, apidoc: FlaskApiSpec):
    # Save/load/execute workflows
    register_resource(workflows.Workflows, "/workflows", api, apidoc)
    register_resource(workflows.Description, "/workflows/descriptions", api, apidoc)
    register_resource(workflows.Workflow, "/workflow/<string:identifier>", api, apidoc)
    register_resource(workflows.Execute, "/execute/<string:identifier>", api, apidoc)

    # Save/load tasks
    register_resource(tasks.Tasks, "/tasks", api, apidoc)
    register_resource(tasks.Task, "/task/<string:identifier>", api, apidoc)
    register_resource(tasks.Descriptions, "/tasks/descriptions", api, apidoc)
    register_resource(tasks.DiscoverTasks, "/tasks/discover", api, apidoc)
