"""Declares the abstract canvas surface used by views to render output."""

from abc import ABC


class Canvas(ABC):  # noqa: B024
    """Abstract canvas surface used by views to render output.

    Purpose:
        Provides the `Canvas` type within the IArena architecture.
    How it works:
        Encapsulates behavior through its public API and type contracts defined in this class body.
    Used for:
        Building rendering and visualization components that can be composed by view modules.
    Public Attributes:
        None declared at class level in this base definition.
    """
