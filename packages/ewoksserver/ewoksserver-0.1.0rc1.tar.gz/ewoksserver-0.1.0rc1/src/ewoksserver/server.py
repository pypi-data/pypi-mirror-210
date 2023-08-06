import os
import sys
import json
from pprint import pformat
from typing import Optional, Tuple

import argparse
import logging
from contextlib import contextmanager

import flask
from flask_cors import CORS
from flask_socketio import SocketIO
from flask_restful import Api
from flask_apispec import FlaskApiSpec

from celery import current_app as current_celery_app
from ewoksjob.client.local import pool_context

try:
    from ewoksweb.serverutils import get_static_root
except ImportError:

    def get_static_root():
        return "static"


from .resources import add_resources
from .events.websocket import add_events


def create_app(**config) -> Tuple[flask.Flask, Api, FlaskApiSpec]:
    app = flask.Flask(__name__, static_folder=get_static_root(), static_url_path="")
    CORS(app)
    configure_app(app, **config)
    apidoc = add_apidoc(app)
    api = add_api(app, apidoc)
    return app, api, apidoc


def add_api(app: flask.Flask, apidoc: FlaskApiSpec) -> Api:
    api = Api(app)
    add_resources(api, apidoc)
    return api


def configure_app(app: flask.Flask, configuration: Optional[str] = None, **config):
    app.config["CORS_HEADERS"] = "Content-Type"
    filename = os.environ.get("EWOKSSERVER_SETTINGS")
    if configuration:
        filename = configuration
    if filename:
        filename = os.path.relpath(filename, app.config.root_path)
        app.config.from_pyfile(filename, silent=False)
    if config:
        config = {k.upper(): v for k, v in config.items() if v is not None}
        app.config.update(config)
    if app.config.get("CELERY"):
        current_celery_app.conf.update(app.config["CELERY"])


def print_config(app: flask.Flask):
    resourcedir = app.config.get("RESOURCE_DIRECTORY")
    if not resourcedir:
        resourcedir = "."
    print(f"\nRESOURCE DIRECTORY:\n {os.path.abspath(resourcedir)}\n")

    adict = app.config.get("CELERY")
    if adict:
        print(f"\nCELERY:\n {pformat(adict)}\n")
    else:
        print("\nCELERY:\n Not configured (local workflow execution)\n")

    adict = app.config.get("EWOKS")
    if adict:
        print(f"\nEWOKS:\n {pformat(adict)}\n")
    else:
        print("\nEWOKS:\n Not configured (no ewoks execution events)\n")


def print_serve_message(app, port: Optional[int] = None) -> None:
    host = "127.0.0.1"
    if port is None:
        server_name = app.config["SERVER_NAME"]
        if server_name and ":" in server_name:
            port = int(server_name.rsplit(":", 1)[1])
        else:
            port = 5000
    print("\nTo start editing workflows, open this link in a browser:\n")
    print(f"    http://{host}:{port}\n")


def set_log_level(app: Optional[flask.Flask] = None, log_level=logging.WARNING):
    logging.basicConfig(level=log_level)
    if app is not None:
        app.logger.setLevel(log_level)


def add_socket(app: flask.Flask) -> SocketIO:
    socketio = SocketIO(app, cors_allowed_origins="*")
    add_events(socketio)
    return socketio


def add_apidoc(app: flask.Flask) -> FlaskApiSpec:
    app.config.update(
        {
            "APISPEC_TITLE": "ewoks",
            # "APISPEC_OAS_VERSION": "3.0.3",
            "APISPEC_SWAGGER_URL": "/swagger/",
            "APISPEC_SWAGGER_UI_URL": "/swagger-ui/",
        }
    )
    return FlaskApiSpec(app)


def save_apidoc(apidoc: FlaskApiSpec, filename: str) -> None:
    save_spec_dir = os.path.dirname(filename)
    if save_spec_dir:
        os.makedirs(save_spec_dir, exist_ok=True)
    with open(filename, "w") as f:
        json.dump(apidoc.spec.to_dict(), f)


def run_app(
    app: flask.Flask, socketio: Optional[SocketIO] = None, port: int = 5000
) -> None:
    with run_context(app):
        if socketio is None:
            app.run(port=port)
        else:
            # allow_unsafe_werkzeug=True, see MR1877
            socketio.run(app, port=port)


@contextmanager
def run_context(app: flask.Flask):
    with app.app_context():
        if app.config.get("CELERY") is None:
            with pool_context():
                yield
        else:
            yield


def main(argv=None):
    if argv is None:
        argv = sys.argv

    parser = argparse.ArgumentParser(description="REST API for Ewoks")
    parser.add_argument(
        "-l",
        "--log",
        dest="log_level",
        type=str.upper,
        default="WARNING",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set the logging level",
    )
    parser.add_argument(
        "-p",
        "--port",
        dest="port",
        type=int,
        default=5000,
        help="Port number",
    )
    parser.add_argument(
        "-c",
        "--config",
        dest="configuration",
        type=str,
        default=None,
        help="Path to a python script (equivalent to the environment variable 'EWOKSSERVER_SETTINGS')",
    )
    parser.add_argument(
        "-d",
        "--dir",
        dest="resource_directory",
        type=str,
        default=None,
        help="Root directory for resources (e.g. workflows, tasks, icons descriptions)",
    )
    parser.add_argument(
        "-s",
        "--spec-filename",
        dest="spec_filename",
        type=str,
        help="Save the Swagger docs as JSON",
    )
    parser.add_argument(
        "--without-events",
        action="store_true",
        help="Without websocket events",
    )

    args = parser.parse_args(argv[1:])
    log_level = getattr(logging, args.log_level)

    app, _, apidoc = create_app(
        configuration=args.configuration, resource_directory=args.resource_directory
    )
    if args.spec_filename:
        save_apidoc(apidoc, args.spec_filename)
        return
    if args.without_events:
        socketio = None
    else:
        socketio = add_socket(app)
    set_log_level(log_level=log_level)

    print_config(app)
    print_serve_message(app, port=args.port)
    run_app(app, socketio=socketio, port=args.port)


if __name__ == "__main__":
    sys.exit(main())
