"""Position model for the Hanoi game."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from iarena.desining.gaming.Position import Position
from iarena.desining.playing.Player import PlayerIndex
from iarena.gaming.Hanoi.Hanoi import HanoiDisc, HanoiPegIndex, HanoiPegsState
from iarena.utilizing.protocoling import ITextRenderable

if TYPE_CHECKING:
    from iarena.gaming.Hanoi.HanoiGameRules import HanoiGameRules


@dataclass(frozen=True, slots=True)
class HanoiPosition(Position, ITextRenderable):
    """Store one full Towers of Hanoi state.

    The `pegs` tuple stores one tuple per peg, from bottom to top. For example,
    ``(3, 2, 1)`` means disk ``1`` is on top and can be moved next.
    """

    rules: HanoiGameRules = field(compare=False, repr=False)
    pegs: HanoiPegsState
    move_count: int = 0

    def next_player(self) -> PlayerIndex:
        """Return the active player index for this turn.

        Args:
            None.

        Returns:
            Always ``0`` because Hanoi is modeled as single-player.
        """
        return 0

    def top_disc(self, peg_index: HanoiPegIndex) -> HanoiDisc | None:
        """Return the top disc of one peg.

        Args:
            peg_index: Peg index to inspect.

        Returns:
            Top disc value, or ``None`` if the peg is empty.
        """
        self.rules.require_valid_peg_index(peg_index)
        peg = self.pegs[peg_index]
        return peg[-1] if peg else None

    def can_move(self, from_peg: HanoiPegIndex, to_peg: HanoiPegIndex) -> bool:
        """Return whether one transfer is legal from this position.

        Args:
            from_peg: Source peg index.
            to_peg: Destination peg index.

        Returns:
            ``True`` when the transfer satisfies Hanoi constraints.
        """
        if from_peg == to_peg:
            return False
        self.rules.require_valid_peg_index(from_peg)
        self.rules.require_valid_peg_index(to_peg)

        source_top = self.top_disc(from_peg)
        if source_top is None:
            return False
        destination_top = self.top_disc(to_peg)
        if destination_top is None:
            return True
        return source_top < destination_top

    def to_text(self) -> str:
        """Render this position as terminal-friendly text.

        Args:
            None.

        Returns:
            Multiline textual representation of pegs and progress.
        """
        lines: list[str] = [
            f"Move count: {self.move_count}",
            f"Target peg: {self.rules.target_peg()}",
            "Pegs:",
        ]

        for peg_index, peg in enumerate(self.pegs):
            top = peg[-1] if peg else "-"
            lines.append(f"  - Peg {peg_index}: {list(peg)} (top: {top})")

        if self.rules.finished(self):
            lines.append("Status: solved")
        else:
            lines.append("Status: in progress")

        return "\n".join(lines)

    def __str__(self) -> str:
        """Render this position using the text-rendering protocol.

        Args:
            None.

        Returns:
            Same value as :meth:`to_text`.
        """
        return self.to_text()
