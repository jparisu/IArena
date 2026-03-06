"""Generic registry with alias support and normalized lookup."""

from __future__ import annotations

import uuid
from abc import ABC
from collections.abc import Sequence
from typing import Callable, Generic, TypeVar

from iarena.utilizing.names import naming_convention


def default_naming_convention(name: str) -> str:
    """Default name normalizer used by the registry."""
    return naming_convention(name)


T = TypeVar("T")


class GenericRegistry(ABC, Generic[T]):
    """Store values and access them through one or many aliases."""

    def __init__(self, name_convention: Callable[[str], str] | None = None) -> None:
        # The actual data storage: {random_index: object}
        self._storage: dict[str, T] = {}
        # Mapping: {alias_name: random_index}
        self._alias_map: dict[str, str] = {}
        # Formatting function for normalization
        self._name_convention = name_convention or default_naming_convention

    def register(
        self,
        obj: T,
        name: str,
        aliases: Sequence[str] | None = None,
        overwrite: bool = False,
    ) -> str:
        """
        Registers an object under a primary name and optional aliases.
        All names point to a generated random index.

        :param obj: The object to store.
        :param name: The main identifier.
        :param aliases: Additional identifiers for the same object.
        :param overwrite: If True, replaces existing names/aliases. If False, raises ValueError on conflict.
        :return: The random index (internal key) generated for this entry.
        """
        fmt_name = self._format_name(name)
        fmt_aliases = [self._format_name(a) for a in (aliases or [])]
        all_names = [fmt_name] + fmt_aliases

        # 1. Conflict Validation
        if not overwrite:
            for n in all_names:
                if n in self._alias_map:
                    raise ValueError(f"Name/Alias '{n}' is already in use. Set overwrite=True to replace.")

        # 2. Generate Random Index
        internal_key = uuid.uuid4().hex

        # 3. Handle Overwrites/Cleanup
        for n in all_names:
            if n in self._alias_map:
                old_key = self._alias_map[n]
                self.remove_alias(n)
                self._cleanup_orphaned_value(old_key)

        # 4. Store
        self._storage[internal_key] = obj
        for n in all_names:
            self._alias_map[n] = internal_key

        return internal_key

    def register_alias(self, alias: str, target_existing_alias: str, overwrite: bool = False) -> None:
        """
        Points a new alias to the same random index as an existing alias/name.

        :param alias: The new name to register.
        :param target_existing_alias: An existing name already in the registry.
        :param overwrite: If True, replaces the alias if it already exists.
        """
        fmt_alias = self._format_name(alias)
        fmt_target = self._format_name(target_existing_alias)

        if fmt_target not in self._alias_map:
            raise KeyError(f"Target name '{target_existing_alias}' does not exist.")

        if not overwrite and fmt_alias in self._alias_map:
            raise ValueError(f"Alias '{alias}' is already in use.")

        if overwrite and fmt_alias in self._alias_map:
            old_key = self._alias_map[fmt_alias]
            self.remove_alias(alias)
            self._cleanup_orphaned_value(old_key)

        # Link the new alias to the existing internal random index
        self._alias_map[fmt_alias] = self._alias_map[fmt_target]

    def get(self, name: str, strict: bool = True) -> T | None:
        """
        Retrieves the object associated with a name/alias.

        :param name: The alias to look up.
        :param strict: If True, raises KeyError if not found. Else returns None.
        """
        fmt_name = self._format_name(name)
        internal_key = self._alias_map.get(fmt_name)

        if not internal_key:
            if strict:
                raise KeyError(f"Name '{name}' not found in registry.")
            return None

        return self._storage.get(internal_key)

    def remove_alias(self, name: str) -> None:
        """
        Removes a specific alias pointer. The underlying value remains
        accessible by other aliases.
        """
        fmt_name = self._format_name(name)
        if fmt_name in self._alias_map:
            del self._alias_map[fmt_name]
        else:
            raise KeyError(f"Alias '{name}' not found.")

    def remove_value(self, name: str) -> T | None:
        """
        Removes the underlying value and ALL aliases associated with it.

        :param name: Any alias pointing to the value to be destroyed.
        :return: The removed object.
        """
        fmt_name = self._format_name(name)
        internal_key = self._alias_map.get(fmt_name)

        if not internal_key:
            raise KeyError(f"No value found associated with '{name}'.")

        # 1. Remove all aliases pointing to this index
        aliases_to_clear = [k for k, v in self._alias_map.items() if v == internal_key]
        for a in aliases_to_clear:
            del self._alias_map[a]

        # 2. Remove from storage
        return self._storage.pop(internal_key)

    def has(self, name: str) -> bool:
        """Checks if a name or alias exists in the registry."""
        return self._format_name(name) in self._alias_map

    def list_aliases(self) -> list[str]:
        """Returns all registered aliases."""
        return list(self._alias_map.keys())

    def __contains__(self, name: str) -> bool:
        return self.has(name)

    def __len__(self) -> int:
        """Returns the number of unique values stored."""
        return len(self._storage)

    def clear(self) -> None:
        """Wipes all data and aliases."""
        self._storage.clear()
        self._alias_map.clear()

    def _format_name(self, name: str) -> str:
        """Normalizes names based on the provided convention."""
        return self._name_convention(name)

    def _cleanup_orphaned_value(self, internal_key: str) -> None:
        """Delete an internal value if no aliases reference it anymore."""
        if internal_key not in self._alias_map.values():
            self._storage.pop(internal_key, None)
