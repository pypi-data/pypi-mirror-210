import time
from ..events.websocket import is_running


def test_websocket_connection_local(local_exec_client):
    _, sclient = local_exec_client
    _test_websocket_connection(sclient)


def test_websocket_connection_celery(celery_exec_client):
    _, sclient = celery_exec_client
    _test_websocket_connection(sclient)


def _test_websocket_connection(sclient):
    assert sclient.is_connected()
    _assert_eventloop_is_running(True)
    sclient.disconnect()
    _assert_eventloop_is_running(False)
    sclient.connect()
    _assert_eventloop_is_running(True)


def _assert_eventloop_is_running(running, timeout=3):
    t0 = time.time()
    while True:
        if is_running() == running:
            return
        time.sleep(0.1)
        if time.time() - t0 > timeout:
            raise TimeoutError
