from flask import current_app

from ewoksjob.client import submit
from ewoksjob.client.local import submit as submit_local
from . import resource
from .. import api


class Workflow(resource.JsonResource):
    RESOURCE_TYPE = "workflow"

    def get_identifier(
        self, resource: resource.ResourceContentType
    ) -> resource.ResourceIdentifierType:
        return resource["graph"]["id"]

    @api.get_resource("workflow")
    def get(self, identifier: resource.ResourceIdentifierType) -> resource.ResponseType:
        return self.load_resource(identifier)

    @api.put_resource("workflow")
    def put(
        self, identifier: resource.ResourceIdentifierType, **resource
    ) -> resource.ResponseType:
        return self.save_resource(
            resource, error_on_missing=True, identifier=identifier
        )

    @api.delete_resource("workflow")
    def delete(
        self, identifier: resource.ResourceIdentifierType
    ) -> resource.ResponseType:
        return self.delete_resource(identifier)


class Workflows(resource.JsonResource):
    RESOURCE_TYPE = "workflow"

    def get_identifier(
        self, resource: resource.ResourceContentType
    ) -> resource.ResourceIdentifierType:
        return resource["graph"]["id"]

    @api.list_resource_identifiers("workflow")
    def get(self) -> resource.ResponseType:
        return self.list_resource_identifiers()

    @api.post_resource("workflow")
    def post(self, **resource) -> resource.ResponseType:
        return self.save_resource(resource, error_on_exists=True)


class Description(resource.JsonResource):
    RESOURCE_TYPE = "workflow"

    def get_identifier(
        self, resource: resource.ResourceContentType
    ) -> resource.ResourceIdentifierType:
        return resource["graph"]["id"]

    @api.list_resource_descriptions("workflow")
    def get(self) -> resource.ResponseType:
        return self.list_resource_descriptions()


class Execute(resource.JsonResource):
    RESOURCE_TYPE = "workflow"

    def get_identifier(
        self, resource: resource.ResourceContentType
    ) -> resource.ResourceIdentifierType:
        return resource["graph"]["id"]

    @api.execute_resource("workflow")
    def post(
        self,
        identifier: resource.ResourceIdentifierType,
        execute_arguments=None,
        worker_options=None,
    ):
        graph, error_code = self.load_resource(identifier)
        if error_code != 200:
            return graph, error_code

        if execute_arguments is None:
            execute_arguments = dict()
        if worker_options is None:
            submit_kwargs = dict()
        else:
            submit_kwargs = dict(worker_options)
        submit_kwargs["args"] = (graph,)
        submit_kwargs["kwargs"] = execute_arguments

        ewoks_config = current_app.config.get("EWOKS")
        if ewoks_config:
            execinfo = execute_arguments.setdefault("execinfo", dict())
            handlers = execinfo.setdefault("handlers", list())
            for handler in ewoks_config.get("handlers", list()):
                if handler not in handlers:
                    handlers.append(handler)

        if current_app.config.get("CELERY") is None:
            future = submit_local(**submit_kwargs)
        else:
            future = submit(**submit_kwargs)
        return self.make_response(200, job_id=future.task_id)
