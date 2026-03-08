"""Declares the streamlit session wrapper used by visualization architecture."""

from __future__ import annotations

from collections.abc import Iterator, Mapping
from typing import Any


class StreamlitSession(Mapping[str, Any]):
    """Mapping-like wrapper for streamlit session state values.

    Purpose:
        Provides a stable, streamlit-agnostic session representation for view and
        player APIs.
    How it works:
        Stores key-value state internally and exposes both mapping and attribute
        style access.
    Used for:
        Passing UI widget state into streamlit-specific input capture methods.
    Public Attributes:
        None declared at class level in this base definition.
    """

    def __init__(self, values: Mapping[str, Any] | None = None) -> None:
        """Create one streamlit session wrapper.

        Args:
            values: Optional initial mapping copied into this session state.

        Returns:
            None.
        """
        self._values: dict[str, Any] = dict(values) if values is not None else {}

    def __getitem__(self, key: str) -> Any:
        """Return one value from the stored session state.

        Args:
            key: Session-state key to resolve.

        Returns:
            Any: Stored value associated with `key`.
        """
        return self._values[key]

    def __iter__(self) -> Iterator[str]:
        """Iterate over stored session-state keys.

        Args:
            None.

        Returns:
            Iterator[str]: Iterator over session-state keys.
        """
        return iter(self._values)

    def __len__(self) -> int:
        """Return the number of stored session-state keys.

        Args:
            None.

        Returns:
            int: Number of key-value entries.
        """
        return len(self._values)

    def __getattr__(self, item: str) -> Any:
        """Return one state value via attribute access when available.

        Args:
            item: Session-state key requested as an attribute.

        Returns:
            Any: Stored value associated with `item`.

        Raises:
            AttributeError: If `item` is not present in the state mapping.
        """
        if item in self._values:
            return self._values[item]
        raise AttributeError(f"StreamlitSession has no attribute '{item}'.")

    def set(self, key: str, value: Any) -> None:
        """Store or replace one session-state key-value entry.

        Args:
            key: Key to set.
            value: Value to persist under `key`.

        Returns:
            None.
        """
        self._values[key] = value

    def pop(self, key: str, default: Any = None) -> Any:
        """Remove one key from session state and return its value.

        Args:
            key: Key to remove.
            default: Fallback value returned when key is missing.

        Returns:
            Any: Removed value or `default` if key did not exist.
        """
        return self._values.pop(key, default)

    def to_dict(self) -> dict[str, Any]:
        """Return a shallow dictionary copy of this session state.

        Args:
            None.

        Returns:
            dict[str, Any]: Copy of current state mapping.
        """
        return dict(self._values)
