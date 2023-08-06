from contextlib import contextmanager
from typing import Iterator, Optional

from flask import current_app

from ewoksjob.events.readers import EwoksEventReader
from ewoksjob.events.readers import instantiate_reader


def reader() -> Optional[EwoksEventReader]:
    cfg = current_app.config.get("EWOKS", dict())
    handlers = cfg.get("handlers", list())
    argmap = {"uri": "url"}
    for name in ("Redis", "Sqlite3", None):
        for handler in handlers:
            if name is None or name in handler["class"]:
                arguments = handler.get("arguments", list())
                arguments = {
                    argmap.get(arg["name"], arg["name"]): arg["value"]
                    for arg in arguments
                }
                return instantiate_reader(**arguments)

    current_app.logger.warning("Configure ewoks event handlers")
    return None


@contextmanager
def reader_context() -> Iterator[Optional[EwoksEventReader]]:
    r = reader()
    try:
        yield r
    finally:
        if r is not None:
            r.close()
