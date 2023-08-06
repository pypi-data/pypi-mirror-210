from . import resource
from .. import api


class Icon(resource.BinaryResource):
    RESOURCE_TYPE = "icon"

    @api.get_resource("icon")
    def get(
        self, identifier: resource.ResourceIdentifierType
    ) -> resource.ResourceIdentifierType:
        return self.load_resource(identifier)

    @api.delete_resource("icon")
    def delete(
        self, identifier: resource.ResourceIdentifierType
    ) -> resource.ResponseType:
        return self.delete_resource(identifier)

    @api.put_resource("icon")
    def put(
        self, identifier: resource.ResourceIdentifierType, **resource
    ) -> resource.ResponseType:
        return self.save_resource(identifier, resource, error_on_missing=True)

    @api.post_resource("icon")
    def post(
        self, identifier: resource.ResourceIdentifierType, **resource
    ) -> resource.ResponseType:
        return self.save_resource(identifier, resource, error_on_exists=True)


class Icons(resource.BinaryResource):
    RESOURCE_TYPE = "icon"

    @api.list_resource_identifiers("icon")
    def get(self) -> resource.ResponseType:
        return self.list_resource_identifiers()
