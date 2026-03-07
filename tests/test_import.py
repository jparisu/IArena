# tests/test_import.py


from __future__ import annotations

import importlib
import pkgutil

import iarena


def _iter_submodules(package):
    """Yield full module names for all submodules of a package."""
    for module_info in pkgutil.walk_packages(package.__path__, package.__name__ + "."):
        # module_info is (module_finder, name, ispkg)
        yield module_info.name


def test_all_submodules_importable():
    """
    Ensure that all submodules in iarena can be imported
    without syntax or import errors.
    """
    for module_name in _iter_submodules(iarena):
        # Importing will raise if there is a syntax/import error
        importlib.import_module(module_name)
