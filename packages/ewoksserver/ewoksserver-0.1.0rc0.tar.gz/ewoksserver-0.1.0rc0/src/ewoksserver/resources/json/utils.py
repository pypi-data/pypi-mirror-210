import json
import logging
from pathlib import Path
from typing import Iterator, Union
from ..data import DEFAULT_ROOT


ResourceIdentifierType = str
ResourceUrlType = Path
ResourceContentType = dict
ResourceDescriptionType = dict

_logger = logging.getLogger(__name__)


def root_url(root_url: Union[str, Path, None], category: str) -> ResourceUrlType:
    if not root_url:
        root_url = Path(".")
    elif isinstance(root_url, str):
        root_url = Path(root_url)
    return root_url / category


def resource_identifiers(root: ResourceUrlType) -> Iterator[ResourceIdentifierType]:
    for url in _resource_urls(root):
        yield _url_to_identifier(url)


def resources(root: ResourceUrlType) -> Iterator[ResourceContentType]:
    for url in _resource_urls(root):
        yield _load_url(url)


def resource_descriptions(root: ResourceUrlType) -> Iterator[ResourceDescriptionType]:
    for res in resources(root):
        resDict = {
            key: res["graph"][key]
            for key in ("id", "label", "category")
            if key in res["graph"]
        }
        yield resDict


def resource_exists(root: ResourceUrlType, identifier: ResourceIdentifierType) -> bool:
    for root in [root, _default_root_url(root)]:
        if _identifier_to_url(root, identifier).exists():
            return True
    return False


def _default_root_url(root: ResourceUrlType) -> ResourceUrlType:
    return DEFAULT_ROOT / root.name


def _resource_urls(root: ResourceUrlType) -> Iterator[ResourceUrlType]:
    for root in [root, _default_root_url(root)]:
        if not root.exists():
            continue
        for url in root.iterdir():
            if _is_resource(url):
                yield url


def _is_resource(url: ResourceUrlType) -> bool:
    return url.is_file() and url.name.endswith(".json")


def save_resource(
    root: ResourceUrlType,
    identifier: ResourceIdentifierType,
    resource: ResourceContentType,
):
    url = _identifier_to_url(root, identifier)
    _save_url(url, resource)


def load_resource(
    root: ResourceUrlType, identifier: ResourceIdentifierType
) -> ResourceContentType:
    url = _identifier_to_url(root, identifier)
    try:
        return _load_url(url)
    except FileNotFoundError:
        url = _identifier_to_url(DEFAULT_ROOT / root.name, identifier)
        return _load_url(url)


def delete_resource(root: ResourceUrlType, identifier: ResourceIdentifierType) -> None:
    url = _identifier_to_url(root, identifier)
    _delete_url(url)


def _identifier_to_url(root: ResourceUrlType, identifier: ResourceIdentifierType):
    return root / (identifier + ".json")


def _url_to_identifier(url: ResourceUrlType) -> ResourceIdentifierType:
    return url.stem


def _save_url(url: ResourceUrlType, resource: ResourceContentType):
    _logger.debug("Save file '%s'", url)
    url.parent.mkdir(parents=True, exist_ok=True)
    with open(url, "w") as f:
        json.dump(resource, f, indent=2)


def _load_url(url: ResourceUrlType) -> ResourceContentType:
    try:
        with open(url, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        _logger.error(f"'{url}' not found")
        raise


def _delete_url(url: ResourceUrlType) -> ResourceContentType:
    if url.exists():
        _logger.debug("Delete file '%s'", url)
        url.unlink()
