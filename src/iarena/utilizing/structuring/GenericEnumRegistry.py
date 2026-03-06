from __future__ import annotations

from enum import Enum
from typing import Any, Optional, TypeVar, cast

from iarena.utilizing.names import naming_convention

T = TypeVar("T", bound="GenericEnumRegistry")


class GenericEnumRegistry(Enum):
    """
    Abstract base class for Enums Registry.

    Provides utility methods for:
    - Retrieving all underlying values defined in the Enum.
    - Accessing values with optional indexing for sequences.
    - Finding members by name or value with case-insensitive matching and alias support.

    Dev-Note:
        This class cannot inherit from ABC because Enum already uses a custom metaclass.

    """

    @classmethod
    def get_all_values(cls) -> list[Any]:
        """Returns a list of all underlying values defined in the Enum."""
        return [member.value for member in cls]

    def get(self, index: int | None = None) -> Any:
        """
        Returns the value. If an index is provided and the value is a
        Sequence (tuple/list), returns the element at that index.
        """
        if index is not None:
            if isinstance(self.value, (list, tuple)):
                return self.value[index]
            raise TypeError(f"Member {self.name} value is not a Sequence; cannot access index {index}.")
        return self.value

    @classmethod
    def find(cls: type[T], query: str, throw: bool = True, only_keys: bool = False) -> T | None:
        """
        Searches for a match by name or within the stored values.
        Matches are case-insensitive for names and strings > 1 char.
        """
        q = str(query)
        q_convention = cls.name_convention(q)

        for member in cls:
            member_name_convention = cls.name_convention(member.name)

            # 1. Match against Enum Name
            if member_name_convention == q_convention:
                return member

            # 2. Match against Value(s)
            if not only_keys:
                vals = member.value if isinstance(member.value, (list, tuple)) else [member.value]

                for v in vals:
                    v_str = str(v)
                    v_name_convention = cls.name_convention(v_str)

                    if v_name_convention == q_convention:
                        return member

        if throw:
            raise ValueError(f"Could not find {cls.__name__} matching: '{query}'")
        return cls.default()

    @classmethod
    def from_string(cls: type[T], value: str, throw: bool = True) -> T | None:
        """Build a member from a string key/value representation."""
        return cls.find(value, throw=throw)

    @classmethod
    def name_convention(cls, name: str) -> str:
        """
        Converts any string to a standardized naming convention (lowercase, no punctuation).
        """
        # Check if the name is inside aliases
        aliases = cls.aliases()
        if name in aliases:
            return naming_convention(aliases[name])

        # Convert to naming convention (lowercase, no punctuation)
        name = naming_convention(name)

        # Check again after conversion if the name is inside aliases
        if name in aliases:
            return naming_convention(aliases[name])

        # Not alias, return the converted name
        return name

    @classmethod
    def default(cls) -> T | None:
        """Return the default enum member (first member) or ``None`` if empty."""
        return cast(Optional[T], next(iter(cls), None))

    @classmethod
    def aliases(cls) -> dict[str, str]:
        """Returns a dictionary of aliases for the Enum members."""
        return {}
