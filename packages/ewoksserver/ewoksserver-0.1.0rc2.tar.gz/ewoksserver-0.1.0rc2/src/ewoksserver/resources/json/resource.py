from typing import Optional, Tuple

from flask import current_app
from ..utils import Resource
from . import utils
from .utils import ResourceUrlType
from .utils import ResourceContentType
from .utils import ResourceIdentifierType

ResponseType = Tuple[dict, int]


class JsonResource(Resource):
    """Base class without end points"""

    RESOURCE_TYPE = NotImplemented

    @property
    def root_url(self) -> ResourceUrlType:
        return utils.root_url(
            current_app.config.get("RESOURCE_DIRECTORY"), self.RESOURCE_TYPE + "s"
        )

    def save_resource(
        self,
        resource: ResourceContentType,
        error_on_exists: bool = False,
        error_on_missing: bool = False,
        identifier: Optional[ResourceIdentifierType] = None,
    ) -> ResponseType:
        """
        200: OK
        400: bad request (fails due to a client error)
        403: forbidden
        404: not found (`error_on_missing=True`)
        409: already exists  (`error_on_exists=True`)
        """
        try:
            ridentifier = self.get_identifier(resource)
        except Exception as e:
            return self.make_response(
                400,
                message=f"Failed to extract {self.RESOURCE_TYPE} identifier from '{resource}': {e}.",
                identifier=identifier,
            )
        if identifier is None:
            identifier = ridentifier

        if identifier != ridentifier:
            return self.make_response(
                400,
                message=f"Resource identifier '{identifier}' is not equal to '{ridentifier}'.",
                identifier=identifier,
            )

        root_url = self.root_url
        exists = utils.resource_exists(root_url, identifier)
        if error_on_exists and exists:
            return self.make_response(
                409,
                message=f"{self.RESOURCE_TYPE.capitalize()} '{identifier}' already exists.",
                identifier=identifier,
            )

        if error_on_missing and not exists:
            return self.make_response(
                404,
                message=f"{self.RESOURCE_TYPE.capitalize()} '{identifier}' is not found.",
                identifier=identifier,
            )

        try:
            utils.save_resource(root_url, identifier, resource)
        except PermissionError:
            return self.make_response(
                403,
                message=f"No permission to write {self.RESOURCE_TYPE} '{identifier}.'",
                identifier=identifier,
            )

        return resource, 200

    def load_resource(
        self,
        identifier: ResourceIdentifierType,
    ) -> ResponseType:
        """
        200: OK
        403: forbidden
        404: not found
        """
        try:
            return utils.load_resource(self.root_url, identifier), 200
        except PermissionError:
            return self.make_response(
                403,
                message=f"No permission to read {self.RESOURCE_TYPE} '{identifier}'",
                identifier=identifier,
            )
        except FileNotFoundError:
            return self.make_response(
                404,
                message=f"{self.RESOURCE_TYPE.capitalize()} '{identifier}' is not found.",
                identifier=identifier,
            )

    def delete_resource(self, identifier: ResourceIdentifierType) -> ResponseType:
        """
        200: OK
        403: forbidden
        """
        try:
            utils.delete_resource(self.root_url, identifier)
        except PermissionError:
            return self.make_response(
                403,
                message=f"No permission to delete {self.RESOURCE_TYPE} '{identifier}'.",
                identifier=identifier,
            )
        return self.make_response(200, identifier=identifier)

    def list_resource_identifiers(self) -> ResponseType:
        """
        200: OK
        """
        body = {"identifiers": list(utils.resource_identifiers(self.root_url))}
        return body, 200

    def list_resource_content(self) -> ResponseType:
        """
        200: OK
        """
        body = {"items": list(utils.resources(self.root_url))}
        return body, 200

    def list_resource_descriptions(self) -> ResponseType:
        """
        200: OK
        """
        body = {"items": list(utils.resource_descriptions(self.root_url))}
        return body, 200

    def get_identifier(self, resource: ResourceContentType) -> ResourceIdentifierType:
        raise NotImplementedError

    @classmethod
    def make_response(cls, code: int, **body) -> ResponseType:
        body["type"] = cls.RESOURCE_TYPE
        return body, code
