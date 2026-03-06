"""Movement model for the Hanoi game."""

from __future__ import annotations

from dataclasses import dataclass

from iarena.desining.gaming.Movement import Movement
from iarena.gaming.Hanoi.Hanoi import HanoiPegIndex
from iarena.utilizing.protocoling import ITextRenderable


@dataclass(frozen=True, slots=True)
class HanoiMovement(Movement, ITextRenderable):
    """Represent one legal disc transfer between two pegs.

    A movement contains only source and destination peg indices. The rules
    object determines whether the move is legal in a specific position.
    """

    from_peg: HanoiPegIndex
    to_peg: HanoiPegIndex

    def to_text(self) -> str:
        """Render this movement as terminal-friendly text.

        Args:
            None.

        Returns:
            Human-readable movement description.
        """
        return f"<Move {self.from_peg} -> {self.to_peg}>"

    def __str__(self) -> str:
        """Render this movement using the text-rendering protocol.

        Args:
            None.

        Returns:
            Same value as :meth:`to_text`.
        """
        return self.to_text()
