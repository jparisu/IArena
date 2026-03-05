"""Movement model for the GoldMine game."""

from __future__ import annotations

from dataclasses import dataclass

from iarena.gaming.GoldMine.GoldMine import GoldMineDirection
from iarena.interfacing.IMovement import IMovement
from iarena.utilizing.protocoling import ITextRenderable


@dataclass(frozen=True, slots=True)
class GoldMineMovement(IMovement, ITextRenderable):
    """Represent a one-step movement in a cardinal direction."""

    direction: GoldMineDirection

    def to_text(self) -> str:
        """Render this movement as terminal-friendly text.

        Args:
            None.

        Returns:
            Human-readable movement description.
        """
        return f"<Move {self.direction.name}>"

    def __str__(self) -> str:
        """Render this movement using the text-rendering protocol.

        Args:
            None.

        Returns:
            Same value as :meth:`to_text`.
        """
        return self.to_text()
