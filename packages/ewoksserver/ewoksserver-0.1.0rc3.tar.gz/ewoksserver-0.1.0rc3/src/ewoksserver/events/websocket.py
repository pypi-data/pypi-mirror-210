from datetime import datetime
import threading
from typing import Optional

import flask
from flask import copy_current_request_context
from flask_socketio import SocketIO
from flask_socketio import emit

from .ewoks_events import reader_context

fversion = tuple(map(int, flask.__version__.split(".")))[:2]
if fversion < (2, 2):
    from flask.globals import _app_ctx_stack
else:
    _app_ctx_stack = None


def copy_current_app_context(fn):
    if _app_ctx_stack is None:
        return fn

    app_context = _app_ctx_stack.top

    def wrapper(*args, **kwargs):
        with app_context:
            return fn(*args, **kwargs)

    return wrapper


def add_events(socketio: SocketIO):
    socketio.on("connect")(connect)
    socketio.on("disconnect")(disconnect)


def connect():
    _EMITTER.connect()


def disconnect():
    _EMITTER.disconnect()


def is_running():
    return _EMITTER.is_running()


class EwoksEventEmitter:
    def __init__(self) -> None:
        self._stop_event = threading.Event()
        self._thread = None
        self._counter = 0

    def connect(self) -> None:
        self._counter += 1
        self.start()

    def disconnect(self) -> None:
        self._counter = max(self._counter - 1, 0)
        if self._counter == 0:
            self.stop(timeout=3)

    def is_running(self) -> bool:
        return self._is_running(self._thread)

    @staticmethod
    def _is_running(thread: Optional[threading.Thread] = None) -> bool:
        return thread is not None and thread.is_alive()

    def start(self) -> None:
        if self.is_running():
            return

        # Flask context's have thread affinity
        @copy_current_request_context
        @copy_current_app_context
        def main():
            self._main()

        self._stop_event.clear()
        thread = threading.Thread(target=main, daemon=True)
        thread.start()
        self._thread = thread

    def stop(self, timeout: Optional[float] = None) -> None:
        thread = self._thread
        if not self._is_running(thread):
            return
        self._stop_event.set()
        thread.join(timeout=timeout)

    def _main(self) -> None:
        try:
            with reader_context() as reader:
                if reader is None:
                    return
                starttime = datetime.now().astimezone()
                for event in reader.wait_events(
                    starttime=starttime, stop_event=self._stop_event
                ):
                    if self._stop_event.is_set():
                        break
                    emit("Executing", event, broadcast=True)
        finally:
            self._thread = None


_EMITTER = EwoksEventEmitter()
