"""Declares the base configuration contract used to build game rules."""

from abc import ABC

from iarena.utilizing.structuring.GenericParameter import GenericParameter


class Configuration(GenericParameter, ABC):
    """Abstract configuration object used to construct game rules.

    Purpose:
        Provides the `Configuration` type within the IArena architecture.
    How it works:
        Encapsulates behavior through its public API and type contracts defined in this class body.
    Used for:
        Building game, mapping, utility, or protocol components that can be composed by other modules.
    Public Attributes:
        None declared at class level in this base definition.
    """
