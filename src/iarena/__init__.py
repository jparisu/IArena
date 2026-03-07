"""iarena package."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("iarena")
except PackageNotFoundError:
    __version__ = "0.0.0"
