"""Defines the REST API.
"""

from typing import Callable
from flask_apispec import marshal_with, doc, use_kwargs
from marshmallow import Schema, fields


class ErrorSchema(Schema):
    message = fields.Str(required=True)
    type = fields.Str()
    identifier = fields.Str()


class JobInfoSchema(Schema):
    job_id = fields.Str(required=True)


class JobInputSchema(Schema):
    execute_arguments = fields.Mapping()
    worker_options = fields.Mapping()


class ResourceIdentifierSchema(Schema):
    identifier = fields.Str(required=True)


class ResourceIdentifierListSchema(Schema):
    identifiers = fields.List(fields.Str, required=True)


class EwoksGraphSchema(Schema):
    graph = fields.Mapping()
    nodes = fields.List(fields.Mapping)
    links = fields.List(fields.Mapping)


class EwoksGraphDescriptionSchema(Schema):
    id = fields.Str()
    label = fields.Str()
    category = fields.Str()


class EwoksDataUrlSchema(Schema):
    data_url = fields.Str(required=True)


class EwoksTaskSchema(Schema):
    task_type = fields.Str(required=True)
    task_identifier = fields.Str(required=True)
    category = fields.Str()
    icon = fields.Str()
    required_input_names = fields.List(fields.Str)
    optional_input_names = fields.List(fields.Str)
    output_names = fields.List(fields.Str)


class EwoksGraphListSchema(Schema):
    items = fields.List(fields.Nested(EwoksGraphSchema()))


class EwoksGraphDescriptionListSchema(Schema):
    items = fields.List(fields.Nested(EwoksGraphDescriptionSchema()))


class EwoksTaskListSchema(Schema):
    items = fields.List(fields.Nested(EwoksTaskSchema()))


class DiscoverSchema(Schema):
    modules = fields.List(fields.Str)


class EwoksEventSchema(Schema):
    host_name = fields.Str(required=True)
    process_id = fields.Int(required=True)
    user_name = fields.Str(required=True)
    job_id = fields.Str(required=True)
    binding = fields.Str(dump_default=None, load_default=None)
    context = fields.Str(required=True)
    workflow_id = fields.Str(required=True)
    node_id = fields.Str(dump_default=None, load_default=None)
    task_id = fields.Str(dump_default=None, load_default=None)
    type = fields.Str(required=True)
    time = fields.Str(required=True)
    error = fields.Boolean(dump_default=None, load_default=None)
    error_message = fields.Str(dump_default=None, load_default=None)
    error_traceback = fields.Str(dump_default=None, load_default=None)
    progress = fields.Int(dump_default=None, load_default=None)
    task_uri = fields.Str(dump_default=None, load_default=None)
    input_uris = fields.List(fields.Mapping, dump_default=None, load_default=None)
    output_uris = fields.List(fields.Mapping, dump_default=None, load_default=None)


class EwoksEventQuerySchema(Schema):
    user_name = fields.Str()
    job_id = fields.Str()
    context = fields.Str()
    workflow_id = fields.Str()
    node_id = fields.Str()
    task_id = fields.Str()
    type = fields.Str()
    starttime = fields.Str()
    endtime = fields.Str()
    error = fields.Boolean()


class EwoksEventListSchema(Schema):
    jobs = fields.List(fields.List(fields.Nested(EwoksEventSchema())))


def get_resource_content_schema(resource_type: str):
    if resource_type == "workflow":
        return EwoksGraphSchema
    elif resource_type == "task":
        return EwoksTaskSchema
    elif resource_type == "icon":
        return EwoksDataUrlSchema
    else:
        raise TypeError(resource_type)


def get_resource_content_list_schema(resource_type: str):
    if resource_type == "workflow":
        return EwoksGraphListSchema
    elif resource_type == "task":
        return EwoksTaskListSchema
    else:
        raise TypeError(resource_type)


def get_resource_description_list_schema(resource_type: str):
    if resource_type == "workflow":
        return EwoksGraphDescriptionListSchema
    else:
        raise TypeError(resource_type)


def get_resource(resource_type: str):
    def wrapper(func: Callable):
        bodyschema = get_resource_content_schema(resource_type)
        func = doc(summary=f"Get a {resource_type}")(func)
        func = marshal_with(
            bodyschema,
            code=200,
            description=f"{resource_type} returned",
        )(func)
        func = marshal_with(
            ErrorSchema,
            code=403,
            description=f"no permission to read the {resource_type}",
        )(func)
        func = marshal_with(
            ErrorSchema,
            code=404,
            description=f"requested {resource_type} is not found",
        )(func)
        return func

    return wrapper


def put_resource(resource_type: str):
    def wrapper(func: Callable):
        bodyschema = get_resource_content_schema(resource_type)
        func = doc(summary=f"Update a {resource_type}")(func)
        func = use_kwargs(bodyschema)(func)
        func = marshal_with(
            bodyschema,
            code=200,
            description=f"{resource_type} was overwritten",
        )(func)
        func = marshal_with(
            ErrorSchema,
            code=400,
            description=f"bad {resource_type} update request",
        )(func)
        func = marshal_with(
            ErrorSchema,
            code=403,
            description=f"no permission to write the {resource_type}",
        )(func)
        func = marshal_with(
            ErrorSchema,
            code=404,
            description=f"requested {resource_type} is not found",
        )(func)
        return func

    return wrapper


def post_resource(resource_type: str):
    def wrapper(func: Callable):
        bodyschema = get_resource_content_schema(resource_type)
        func = doc(summary=f"Create a {resource_type}")(func)
        func = use_kwargs(bodyschema)(func)
        func = marshal_with(
            bodyschema,
            code=200,
            description=f"{resource_type} was created",
        )(func)
        func = marshal_with(
            ErrorSchema,
            code=400,
            description=f"bad {resource_type} create request",
        )(func)
        func = marshal_with(
            ErrorSchema,
            code=403,
            description=f"no permission to write the {resource_type}",
        )(func)
        func = marshal_with(
            ErrorSchema,
            code=409,
            description=f"requested {resource_type} already exists",
        )(func)
        return func

    return wrapper


def delete_resource(resource_type: str):
    def wrapper(func: Callable):
        func = doc(summary=f"Delete a {resource_type}")(func)
        func = marshal_with(
            ResourceIdentifierSchema,
            code=200,
            description=f"{resource_type} has been removed or did not exist",
        )(func)
        func = marshal_with(
            ErrorSchema,
            code=403,
            description=f"no permission to delete the {resource_type}",
        )(func)
        return func

    return wrapper


def list_resource_identifiers(resource_type: str):
    def wrapper(func: Callable):
        func = doc(summary=f"Get a list of {resource_type} identifiers")(func)
        func = marshal_with(ResourceIdentifierListSchema, code=200)(func)
        return func

    return wrapper


def list_resource_content(resource_type: str):
    def wrapper(func: Callable):
        func = doc(summary=f"Get a list of {resource_type}s")(func)
        func = marshal_with(get_resource_content_list_schema(resource_type), code=200)(
            func
        )
        return func

    return wrapper


def list_resource_descriptions(resource_type: str):
    def wrapper(func: Callable):
        func = doc(summary=f"Get a list of {resource_type}s")(func)
        func = marshal_with(
            get_resource_description_list_schema(resource_type), code=200
        )(func)
        return func

    return wrapper


def execute_resource(resource_type: str):
    def wrapper(func: Callable):
        func = doc(summary=f"Start {resource_type} execution")(func)
        func = use_kwargs(JobInputSchema)(func)
        func = marshal_with(
            JobInfoSchema,
            code=200,
            description=f"{resource_type} execution started",
        )(func)
        func = marshal_with(
            ErrorSchema,
            code=403,
            description=f"no permission to read the {resource_type}",
        )(func)
        func = marshal_with(
            ErrorSchema,
            code=404,
            description=f"requested {resource_type} is not found",
        )(func)
        return func

    return wrapper


def discover_resources(resource_type: str):
    def wrapper(func: Callable):
        func = doc(summary=f"Discover {resource_type}s")(func)
        func = use_kwargs(DiscoverSchema)(func)
        func = marshal_with(ResourceIdentifierListSchema, code=200)(func)
        func = marshal_with(
            ErrorSchema,
            code=403,
            description=f"no permission to write the {resource_type}",
        )(func)
        func = marshal_with(
            ErrorSchema,
            code=404,
            description="module not found",
        )(func)
        func = marshal_with(
            ErrorSchema,
            code=409,
            description=f"requested {resource_type} already exists",
        )(func)
        return func

    return wrapper


def get_ewoks_events():
    def wrapper(func: Callable):
        func = doc(summary="Get ewoks execution events")(func)
        func = use_kwargs(EwoksEventQuerySchema, location="query")(func)
        func = marshal_with(EwoksEventListSchema, code=200)(func)
        func = marshal_with(
            ErrorSchema,
            code=500,
            description="most likely the server was not configured for ewoks events",
        )(func)
        return func

    return wrapper
