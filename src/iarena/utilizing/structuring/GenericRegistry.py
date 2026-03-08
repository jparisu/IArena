"""Declares a generic name-based registry abstraction."""
# pylint: disable=too-many-lines  # TODO: review

from __future__ import annotations

from abc import ABC
from collections.abc import Callable, Sequence
from typing import Generic, TypeVar

T = TypeVar("T")


class GenericRegistry(ABC, Generic[T]):  # noqa: UP046
    """Generic alias-aware registry for storing values by normalized names.

    Purpose:
        Provides the `GenericRegistry` type within the IArena architecture.
    How it works:
        Encapsulates behavior through its public API and type contracts defined in this class body.
    Used for:
        Building game, mapping, utility, or protocol components that can be composed by other modules.
    Public Attributes:
        None declared at class level in this base definition.
    """

    def __init__(self, name_convention: Callable[[str], str] | None = None) -> None:
        """Initialize storage and alias maps with an optional naming convention.

        What it does:
            Implements `__init__` as part of the public behavior of its declaring class.
        How it works:
            Executes the operation according to the class contract and delegates detailed logic to the implementation.
        Args:
            name_convention (Callable[[str], str] | None, optional): Input consumed by this operation.
        Returns:
            None: Performs side effects or state changes without returning a value.
        """
        self._name_convention = name_convention or self._default_name_convention
        self._values: dict[str, T] = {}
        self._aliases: dict[str, str] = {}

    def register(
        self,
        obj: T,
        name: str,
        aliases: Sequence[str] | None = None,
        overwrite: bool = False,
    ) -> str:
        """Register a value with one primary name and optional aliases.

        What it does:
            Implements `register` as part of the public behavior of its declaring class.
        How it works:
            Executes the operation according to the class contract and delegates detailed logic to the implementation.
        Args:
            obj (T): Input consumed by this operation.
            name (str): Input consumed by this operation.
            aliases (Sequence[str] | None, optional): Input consumed by this operation.
            overwrite (bool, optional): Input consumed by this operation.
        Returns:
            str: Result produced after executing the method contract.
        """
        canonical_name = self._normalize_name(name)
        if canonical_name in self._aliases and not overwrite:
            raise KeyError(f"Name '{name}' is already registered.")

        if canonical_name in self._aliases and overwrite:
            existing_target = self._aliases[canonical_name]
            if canonical_name != existing_target and canonical_name in self._values:
                raise KeyError(f"Cannot overwrite primary name '{name}' as an alias.")

        self._values[canonical_name] = obj
        self._aliases[canonical_name] = canonical_name

        for alias in aliases or []:
            self.register_alias(alias=alias, target_existing_alias=canonical_name, overwrite=overwrite)

        return canonical_name

    def register_alias(self, alias: str, target_existing_alias: str, overwrite: bool = False) -> None:
        """Register an alias pointing to an already registered alias or name.

        What it does:
            Implements `register_alias` as part of the public behavior of its declaring class.
        How it works:
            Executes the operation according to the class contract and delegates detailed logic to the implementation.
        Args:
            alias (str): Input consumed by this operation.
            target_existing_alias (str): Input consumed by this operation.
            overwrite (bool, optional): Input consumed by this operation.
        Returns:
            None: Performs side effects or state changes without returning a value.
        """
        alias_name = self._normalize_name(alias)
        target_name = self._normalize_name(target_existing_alias)

        if target_name not in self._aliases:
            raise KeyError(f"Unknown target alias '{target_existing_alias}'.")

        target_canonical = self._aliases[target_name]

        if alias_name in self._aliases and not overwrite:
            raise KeyError(f"Alias '{alias}' is already registered.")

        if alias_name in self._values and alias_name != target_canonical:
            raise KeyError(f"Cannot remap primary name '{alias}'.")

        self._aliases[alias_name] = target_canonical

    def get(self, name: str, strict: bool = True) -> T | None:
        """Retrieve a registered value by name or alias.

        What it does:
            Implements `get` as part of the public behavior of its declaring class.
        How it works:
            Executes the operation according to the class contract and delegates detailed logic to the implementation.
        Args:
            name (str): Input consumed by this operation.
            strict (bool, optional): Input consumed by this operation.
        Returns:
            T | None: Result produced after executing the method contract.
        """
        normalized_name = self._normalize_name(name)
        if normalized_name not in self._aliases:
            if strict:
                raise KeyError(f"Unknown name or alias '{name}'.")
            return None

        canonical_name = self._aliases[normalized_name]
        return self._values[canonical_name]

    def remove_alias(self, name: str) -> None:
        """Remove one alias without deleting the underlying stored value.

        What it does:
            Implements `remove_alias` as part of the public behavior of its declaring class.
        How it works:
            Executes the operation according to the class contract and delegates detailed logic to the implementation.
        Args:
            name (str): Input consumed by this operation.
        Returns:
            None: Performs side effects or state changes without returning a value.
        """
        normalized_name = self._normalize_name(name)
        if normalized_name not in self._aliases:
            raise KeyError(f"Unknown alias '{name}'.")

        if self._aliases[normalized_name] == normalized_name:
            raise ValueError(f"'{name}' is a primary name and cannot be removed as an alias.")

        del self._aliases[normalized_name]

    def remove_value(self, name: str) -> T | None:
        """Remove a stored value and every alias that points to it.

        What it does:
            Implements `remove_value` as part of the public behavior of its declaring class.
        How it works:
            Executes the operation according to the class contract and delegates detailed logic to the implementation.
        Args:
            name (str): Input consumed by this operation.
        Returns:
            T | None: Result produced after executing the method contract.
        """
        normalized_name = self._normalize_name(name)
        if normalized_name not in self._aliases:
            return None

        canonical_name = self._aliases[normalized_name]
        removed_value = self._values.pop(canonical_name, None)
        if removed_value is None:
            return None

        aliases_to_remove = [alias for alias, target in self._aliases.items() if target == canonical_name]
        for alias in aliases_to_remove:
            del self._aliases[alias]

        return removed_value

    def has(self, name: str) -> bool:
        """Return whether a given name or alias is registered.

        What it does:
            Implements `has` as part of the public behavior of its declaring class.
        How it works:
            Executes the operation according to the class contract and delegates detailed logic to the implementation.
        Args:
            name (str): Input consumed by this operation.
        Returns:
            bool: Result produced after executing the method contract.
        """
        return self.get(name, strict=False) is not None

    def list_aliases(self) -> list[str]:
        """Return all registered aliases.

        What it does:
            Implements `list_aliases` as part of the public behavior of its declaring class.
        How it works:
            Executes the operation according to the class contract and delegates detailed logic to the implementation.
        Args:
            None.
        Returns:
            List[str]: Result produced after executing the method contract.
        """
        return list(self._aliases.keys())

    def __contains__(self, name: str) -> bool:
        """Return whether the registry contains a given name or alias.

        What it does:
            Implements `__contains__` as part of the public behavior of its declaring class.
        How it works:
            Executes the operation according to the class contract and delegates detailed logic to the implementation.
        Args:
            name (str): Input consumed by this operation.
        Returns:
            bool: Result produced after executing the method contract.
        """
        return self.has(name)

    def __len__(self) -> int:
        """Return the number of unique stored values.

        What it does:
            Implements `__len__` as part of the public behavior of its declaring class.
        How it works:
            Executes the operation according to the class contract and delegates detailed logic to the implementation.
        Args:
            None.
        Returns:
            int: Result produced after executing the method contract.
        """
        return len(self._values)

    def clear(self) -> None:
        """Remove all stored values and aliases.

        What it does:
            Implements `clear` as part of the public behavior of its declaring class.
        How it works:
            Executes the operation according to the class contract and delegates detailed logic to the implementation.
        Args:
            None.
        Returns:
            None: Performs side effects or state changes without returning a value.
        """
        self._values.clear()
        self._aliases.clear()

    def _normalize_name(self, name: str) -> str:
        """Normalize one name using the configured name convention.

        Args:
            name (str): Raw input name.
        Returns:
            str: Normalized non-empty name.
        """
        normalized = self._name_convention(name)
        if not normalized:
            raise ValueError("Name must not be empty after normalization.")
        return normalized

    @staticmethod
    def _default_name_convention(name: str) -> str:
        """Normalize names by trimming whitespace and lowercasing.

        Args:
            name (str): Raw input name.
        Returns:
            str: Normalized name.
        """
        return name.strip().lower()
