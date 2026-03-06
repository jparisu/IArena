"""Terminal-visualization contract that games can implement."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence

from iarena.desining.gaming.Movement import Movement
from iarena.desining.gaming.Position import Position


class TerminalGame(ABC):
    """Define methods required for terminal-based visualization and input."""

    @abstractmethod
    def position_to_terminal(self, position: Position) -> str:
        """Convert a position into terminal-friendly text.

        Args:
            position: Position to convert.

        Returns:
            String representation of the provided position.
        """
        raise NotImplementedError

    def terminal_instructions(self) -> str | None:
        """Return optional terminal instructions.

        Args:
            None.

        Returns:
            Instructions string, or ``None`` when not provided.
        """
        return None

    def movement_from_terminal(self, raw_movement: str, possible_movements: Sequence[Movement]) -> Movement:
        """Parse terminal input into one selected movement.

        Default behavior expects an integer string and selects the n-th
        movement (1-based indexing).

        Args:
            raw_movement: Raw movement string entered by the user.
            possible_movements: Legal movements available in current position.

        Returns:
            Selected movement.

        Raises:
            ValueError: If input does not match a valid movement index.
        """
        try:
            movement_index = int(raw_movement.strip())
        except ValueError as exc:
            raise ValueError("movement input must be an integer") from exc

        if movement_index < 1 or movement_index > len(possible_movements):
            raise ValueError(f"movement index must be between 1 and {len(possible_movements)}")

        return possible_movements[movement_index - 1]

    def movement_to_terminal(self, movement: Movement) -> str:
        """Convert one movement into terminal-friendly text.

        Args:
            movement: Movement to convert.

        Returns:
            String representation of ``movement``.
        """
        return str(movement)
