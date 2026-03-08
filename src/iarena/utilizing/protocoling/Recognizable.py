"""Defines the protocol for objects exposing a recognizable name."""

from __future__ import annotations

from abc import abstractmethod
from typing import Protocol


class Recognizable(Protocol):
    """Behavioral contract for objects that can expose a canonical name.

    API Notes:
        - This protocol is used by registry, UI, and diagnostics layers that
          need a stable textual identifier for a value.
        - The returned name should be human-readable and stable for the same
          semantic object.
        - Implementers are free to decide naming strategy as long as they
          comply with the declared method signature.
    """

    @abstractmethod
    def name(self) -> str:
        """Return the canonical display or identifier name for this object.

        Args:
            No positional or keyword arguments are required.

        Returns:
            str: Stable name associated with the current object instance.

        Raises:
            NotImplementedError: Raised by the protocol stub to signal that
                concrete implementations must provide this behavior.
        """
        raise NotImplementedError
