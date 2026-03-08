"""Declares the concrete GoldMine movement model."""

from __future__ import annotations

from iarena.gaming.Movement import Movement
from iarena.utilizing.mapping.square_map.SquareMapDirection import SquareMapDirection


class GoldMineMovement(Movement):
    """Concrete GoldMine movement defining one cardinal direction.

    Purpose:
        Represents one move in GoldMine as a cardinal direction on the map.
    How it works:
        Stores a validated `SquareMapDirection` consumed by rules and renderers.
    Used for:
        Driving state transitions from one `GoldMinePosition` to the next.
    Public Attributes:
        direction (SquareMapDirection): Direction selected for the move.
    """

    direction: SquareMapDirection

    def __init__(self, direction: SquareMapDirection) -> None:
        """Create one GoldMine movement from a map direction.

        Args:
            direction: Cardinal direction selected by the player.

        Returns:
            None.
        """
        if not isinstance(direction, SquareMapDirection):
            raise TypeError("direction must be an instance of SquareMapDirection.")
        self.direction = direction

    def __str__(self) -> str:
        """Return a user-friendly terminal representation of the movement.

        Args:
            None.

        Returns:
            str: Human-readable direction name.
        """
        return f"<Move {self.direction.name}>"

    def __repr__(self) -> str:
        """Return a debug-oriented representation of the movement.

        Args:
            None.

        Returns:
            str: Constructor-like textual representation.
        """
        return f"GoldMineMovement(direction={self.direction.name})"
