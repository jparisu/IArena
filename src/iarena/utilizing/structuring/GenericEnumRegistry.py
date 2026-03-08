"""Declares an enum helper with normalized lookup semantics."""

from __future__ import annotations

from enum import Enum
from typing import Any, TypeVar

T = TypeVar("T")


class GenericEnumRegistry(Enum):
    """Enum helper base adding normalized lookup and alias support.

    Purpose:
        Provides the `GenericEnumRegistry` type within the IArena architecture.
    How it works:
        Encapsulates behavior through its public API and type contracts defined in this class body.
    Used for:
        Building game, mapping, utility, or protocol components that can be composed by other modules.
    Public Attributes:
        None declared at class level in this base definition.
    """

    @classmethod
    def get_all_values(cls) -> list[Any]:
        """Return the list of values for all enum members.

        What it does:
            Implements `get_all_values` as part of the public behavior of its declaring class.
        How it works:
            Executes the operation according to the class contract and delegates detailed logic to the implementation.
        Args:
            None.
        Returns:
            List[Any]: Result produced after executing the method contract.
        """
        return [member.value for member in cls]

    def get(self, index: int | None = None) -> Any:
        """Return member value or indexed item when value is a sequence.

        What it does:
            Implements `get` as part of the public behavior of its declaring class.
        How it works:
            Executes the operation according to the class contract and delegates detailed logic to the implementation.
        Args:
            index (int | None, optional): Input consumed by this operation.
        Returns:
            Any: Result produced after executing the method contract.
        """
        if index is None:
            return self.value
        return self.value[index]

    @classmethod
    def find(cls: type[T], query: str, throw: bool = True, only_keys: bool = False) -> T | None:
        """Find and return a member matching query by key or value.

        What it does:
            Implements `find` as part of the public behavior of its declaring class.
        How it works:
            Executes the operation according to the class contract and delegates detailed logic to the implementation.
        Args:
            query (str): Input consumed by this operation.
            throw (bool, optional): Input consumed by this operation.
            only_keys (bool, optional): Input consumed by this operation.
        Returns:
            T | None: Result produced after executing the method contract.
        """
        normalized_query = cls.name_convention(query)

        for member in cls:
            if cls.name_convention(member.name) == normalized_query:
                return member

        if not only_keys:
            for member in cls:
                value = member.value
                value_name = value if isinstance(value, str) else str(value)
                if cls.name_convention(value_name) == normalized_query:
                    return member

        if throw:
            raise ValueError(f"Could not resolve '{query}' in {cls.__name__}.")
        return None

    @classmethod
    def from_string(cls: type[T], value: str, throw: bool = True) -> T | None:
        """Resolve an enum member from its string representation.

        What it does:
            Implements `from_string` as part of the public behavior of its declaring class.
        How it works:
            Executes the operation according to the class contract and delegates detailed logic to the implementation.
        Args:
            value (str): Input consumed by this operation.
            throw (bool, optional): Input consumed by this operation.
        Returns:
            T | None: Result produced after executing the method contract.
        """
        return cls.find(query=value, throw=throw)

    @classmethod
    def name_convention(cls, name: str) -> str:
        """Normalize a name using alias resolution and naming conventions.

        What it does:
            Implements `name_convention` as part of the public behavior of its declaring class.
        How it works:
            Executes the operation according to the class contract and delegates detailed logic to the implementation.
        Args:
            name (str): Input consumed by this operation.
        Returns:
            str: Result produced after executing the method contract.
        """
        normalized = name.strip().lower().replace("_", "").replace("-", "").replace(" ", "")
        alias_target = cls.aliases().get(normalized)
        if alias_target is None:
            return normalized
        return alias_target.strip().lower().replace("_", "").replace("-", "").replace(" ", "")

    @classmethod
    def default(cls) -> T | None:
        """Return the default enum member when available.

        What it does:
            Implements `default` as part of the public behavior of its declaring class.
        How it works:
            Executes the operation according to the class contract and delegates detailed logic to the implementation.
        Args:
            None.
        Returns:
            T | None: Result produced after executing the method contract.
        """
        return None

    @classmethod
    def aliases(cls) -> dict[str, str]:
        """Return alias mappings for enum member names.

        What it does:
            Implements `aliases` as part of the public behavior of its declaring class.
        How it works:
            Executes the operation according to the class contract and delegates detailed logic to the implementation.
        Args:
            None.
        Returns:
            dict[str, str]: Result produced after executing the method contract.
        """
        return {}
