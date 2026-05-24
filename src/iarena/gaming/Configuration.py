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

    def __str__(self) -> str:
        """Return one compact string representation of this configuration.

        Returns:
            str: Class name and serialized public fields.
        """
        parts = [f"{field_name}={field_value!r}" for field_name, field_value in sorted(self.to_dict().items())]
        return f"{type(self).__name__}({', '.join(parts)})"
