from pathlib import Path
from typing import List
import pytest
from ewoksserver.server import create_app
from ewoksserver.server import run_context
from ewoksserver.server import add_socket
from ewoksjob.client.local import pool_context
from ewoksjob.tests.conftest import celery_config  # noqa F401
from ewoksjob.tests.conftest import celery_includes  # noqa F401

from .data import resource_filenames
from ..resources.binary.utils import _load_url
from ..resources.data import DEFAULT_ROOT


@pytest.fixture
def rest_client(tmpdir):
    """Client to the REST server (no execution)."""
    app, *_ = create_app(resource_directory=str(tmpdir))
    with run_context(app):
        with app.test_client() as client:
            yield client


@pytest.fixture()
def ewoks_handlers(tmpdir):
    uri = f"file:{tmpdir / 'ewoks_events.db'}"
    return [
        {
            "class": "ewokscore.events.handlers.Sqlite3EwoksEventHandler",
            "arguments": [{"name": "uri", "value": uri}],
        }
    ]


@pytest.fixture
def local_exec_client(tmpdir, ewoks_handlers):
    """Client to the REST server and websocket (execution with process pool)."""
    ewoks_config = {"handlers": ewoks_handlers}
    app, *_ = create_app(resource_directory=str(tmpdir), ewoks=ewoks_config)
    socketio = add_socket(app)
    with run_context(app):
        with pool_context():
            with app.test_client() as client:
                sclient = socketio.test_client(app, flask_test_client=client)
                yield client, sclient
                sclient.disconnect()


@pytest.fixture
def celery_exec_client(tmpdir, celery_session_worker, ewoks_handlers):
    """Client to the REST server and websocket (execution with celery)."""
    ewoks_config = {"handlers": ewoks_handlers}
    app, *_ = create_app(
        resource_directory=str(tmpdir), celery=dict(), ewoks=ewoks_config
    )
    socketio = add_socket(app)
    with run_context(app):
        with app.test_client() as client:
            sclient = socketio.test_client(app, flask_test_client=client)
            yield client, sclient
            sclient.disconnect()


@pytest.fixture
def png_icons():
    filenames = resource_filenames()
    return [_load_url(filename) for filename in filenames if filename.endswith(".png")]


@pytest.fixture
def svg_icons():
    filenames = resource_filenames()
    return [_load_url(filename) for filename in filenames if filename.endswith(".svg")]


@pytest.fixture(scope="session")
def default_icon_identifiers() -> List[Path]:
    return [
        url.name
        for url in (DEFAULT_ROOT / "icons").iterdir()
        if not url.name.startswith("__")
    ]


@pytest.fixture(scope="session")
def default_workflow_identifiers() -> List[Path]:
    return [
        url.stem
        for url in (DEFAULT_ROOT / "workflows").iterdir()
        if url.suffix == ".json"
    ]


@pytest.fixture(scope="session")
def default_task_identifiers() -> List[Path]:
    return [
        url.stem for url in (DEFAULT_ROOT / "tasks").iterdir() if url.suffix == ".json"
    ]
