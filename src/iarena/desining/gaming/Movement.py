"""Base movement abstractions for game-specific actions."""

from __future__ import annotations

from typing import Protocol, runtime_checkable


class Movement:
    """Base movement type for all game-specific actions."""


@runtime_checkable
class StrMovement(Protocol):
    """Opt-in capability to provide a stable text representation."""

    def to_str(self) -> str:
        """Return a string representation of one movement.

        Args:
            None.

        Returns:
            Stable text representation of this movement.
        """
        raise NotImplementedError
