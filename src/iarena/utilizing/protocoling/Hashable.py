"""Defines the protocol for hashable domain objects."""

from __future__ import annotations

from abc import abstractmethod
from typing import Protocol


class Hashable(Protocol):
    """Behavioral contract for objects that expose a stable hash value.

    API Notes:
        - This protocol defines the minimum API required by IArena components
          that index, cache, or deduplicate domain values.
        - Implementers must ensure that equal objects return the same value from
          :meth:`hash`.
        - The protocol does not prescribe hashing strategy; it only requires the
          method signature and return type.
    """

    @abstractmethod
    def hash(self) -> int:
        """Compute an integer hash that identifies the current object state.

        Returns:
            int: Deterministic hash value for this instance, suitable for
                hashed collections and equality-based indexing workflows.

        Raises:
            NotImplementedError: Raised by the protocol stub to signal that
                concrete implementations must provide this behavior.
        """
        raise NotImplementedError
