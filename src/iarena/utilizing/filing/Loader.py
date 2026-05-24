"""Declares a backward-compatible alias for Python file loading utilities."""

from __future__ import annotations

from iarena.utilizing.filing.PythonLoader import PythonLoader


class Loader(PythonLoader):
    """Compatibility wrapper that preserves the historical `Loader` API.

    Purpose:
        Keep legacy imports (`iarena.utilizing.filing.Loader`) working while
        sharing implementation with `PythonLoader`.
    How it works:
        Inherits all behavior from `PythonLoader` without overriding methods.
    Used for:
        Existing code and tests that still import `Loader`.
    Public Attributes:
        None declared at class level in this utility class.
    """

