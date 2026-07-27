import importlib
import pkgutil

import iarena as package


def _iter_submodules(root_package: object):
    """Yield full module names for all submodules of a package."""
    for module_info in pkgutil.walk_packages(root_package.__path__, root_package.__name__ + "."):
        yield module_info.name


def test_all_submodules_importable() -> None:
    """Ensure package submodules import without import errors."""
    for module_name in _iter_submodules(package):
        importlib.import_module(module_name)
