from ewokscore import task_discovery
from . import resource
from .. import api


class Task(resource.JsonResource):
    RESOURCE_TYPE = "task"

    def get_identifier(
        self, resource: resource.ResourceContentType
    ) -> resource.ResourceIdentifierType:
        return resource["task_identifier"]

    @api.get_resource("task")
    def get(self, identifier: resource.ResourceIdentifierType) -> resource.ResponseType:
        return self.load_resource(identifier)

    @api.put_resource("task")
    def put(
        self, identifier: resource.ResourceIdentifierType, **resource
    ) -> resource.ResponseType:
        return self.save_resource(
            resource, error_on_missing=True, identifier=identifier
        )

    @api.delete_resource("task")
    def delete(
        self, identifier: resource.ResourceIdentifierType
    ) -> resource.ResponseType:
        return self.delete_resource(identifier)


class Tasks(resource.JsonResource):
    RESOURCE_TYPE = "task"

    def get_identifier(
        self, resource: resource.ResourceContentType
    ) -> resource.ResourceIdentifierType:
        return resource["task_identifier"]

    @api.list_resource_identifiers("task")
    def get(self) -> resource.ResponseType:
        return self.list_resource_identifiers()

    @api.post_resource("task")
    def post(self, **resource) -> resource.ResponseType:
        return self.save_resource(resource, error_on_exists=True)


class Descriptions(resource.JsonResource):
    RESOURCE_TYPE = "task"

    def get_identifier(
        self, resource: resource.ResourceContentType
    ) -> resource.ResourceIdentifierType:
        return resource["task_identifier"]

    @api.list_resource_content("task")
    def get(self):
        return self.list_resource_content()


class DiscoverTasks(resource.JsonResource):
    RESOURCE_TYPE = "task"

    def get_identifier(
        self, resource: resource.ResourceContentType
    ) -> resource.ResourceIdentifierType:
        return resource["task_identifier"]

    @api.discover_resources("task")
    def post(self, modules=None, task_type="class"):
        try:
            tasks = task_discovery.discover_tasks_from_modules(
                *modules, task_type=task_type
            )
        except ModuleNotFoundError as e:
            return self.make_response(404, message=str(e))
        for _resource in tasks:
            self._default_task_properties(_resource)
            response, code = self.save_resource(_resource, error_on_exists=True)
            if code != 200:
                return response, code
        tasks = [desc["task_identifier"] for desc in tasks]
        return self.make_response(200, identifiers=tasks)

    @staticmethod
    def _default_task_properties(_resource: dict) -> None:
        if not _resource.get("icon"):
            _resource["icon"] = "default.png"
        if not _resource.get("label"):
            task_identifier = _resource.get("task_identifier")
            if task_identifier:
                _resource["label"] = task_identifier.split(".")[-1]
