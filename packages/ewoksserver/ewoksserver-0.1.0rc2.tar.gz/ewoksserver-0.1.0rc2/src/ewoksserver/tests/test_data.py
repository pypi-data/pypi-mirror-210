import pytest
import shutil
from pathlib import Path
from ..resources.binary import utils as binary_utils
from ..resources.json import utils as json_utils
from ..resources.data import DEFAULT_ROOT


def test_icon_fallback(tmpdir, default_icon_identifiers):
    category = "icons"
    existing = "default.png"
    nonexisting = "nonexisting.png"
    user = "user.png"
    assert_resource_fallback(
        binary_utils,
        tmpdir,
        category,
        existing,
        nonexisting,
        user,
        ".png",
        default_icon_identifiers,
    )


def test_workflows_fallback(tmpdir, default_workflow_identifiers):
    category = "workflows"
    existing = "demo"
    nonexisting = "nonexisting"
    user = "user"
    assert_resource_fallback(
        json_utils,
        tmpdir,
        category,
        existing,
        nonexisting,
        user,
        ".json",
        default_workflow_identifiers,
    )


def assert_resource_fallback(
    utils, user_root, category, existing, nonexisting, user, extension, all_resources
):
    user_root = Path(user_root).resolve()
    user_icons_root = utils.root_url(user_root, category)
    default_icons_root = utils.root_url(DEFAULT_ROOT, category)

    source = (default_icons_root / existing).with_suffix(extension)
    dest = (user_icons_root / user).with_suffix(extension)
    user_icons_root.mkdir()
    shutil.copyfile(source, dest)

    # File only in default root
    utils.load_resource(user_icons_root, existing)

    # File neither in  default nore in user root
    with pytest.raises(FileNotFoundError):
        utils.load_resource(user_icons_root, nonexisting)

    # File only in user root
    utils.load_resource(user_icons_root, user)

    # Find all resources
    found = sorted(utils.resource_identifiers(user_icons_root))
    assert found == sorted(all_resources + [user])

    # Delete user resource
    utils.delete_resource(user_icons_root, user)

    found = sorted(utils.resource_identifiers(user_icons_root))
    assert found == sorted(all_resources)
