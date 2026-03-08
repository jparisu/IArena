"""Declares the concrete Hanoi position model."""

from __future__ import annotations

from typing import TYPE_CHECKING

from iarena.gaming.Position import Position
from iarena.playing.PlayerIndex import PlayerIndex

if TYPE_CHECKING:
    from iarena.gaming.hanoi.HanoiRules import HanoiRules
    from iarena.gaming.Rules import Rules


class HanoiPosition(Position):
    """Concrete Hanoi position containing peg state and step counter.

    Purpose:
        Models one Tower of Hanoi board state including peg assignments and move count.
    How it works:
        Carries immutable-like game-state fields and exposes the `Position` API expected by arena components.
    Used for:
        Rules evaluation, player decision making, and renderer output in Hanoi matches.
    Public Attributes:
        n_pegs (int): Number of pegs available in the puzzle.
        disks (list[int]): Per-disk peg index assignment describing the current board state.
        steps (int): Number of moves executed since the initial position.
    """

    n_pegs: int
    disks: list[int]
    steps: int

    def __init__(self, n_pegs: int, disks: list[int], steps: int = 0) -> None:
        """Create a Hanoi position with explicit peg/disks layout.

        Args:
            n_pegs: Number of pegs available in the puzzle.
            disks: Per-disk peg assignment, usually from largest to smallest disk.
            steps: Number of moves already executed to reach this position.

        Returns:
            None.
        """
        if n_pegs < 2:
            raise ValueError("n_pegs must be at least 2.")
        if steps < 0:
            raise ValueError("steps must be non-negative.")
        if any(peg < 0 or peg >= n_pegs for peg in disks):
            raise ValueError("All disk peg indices must be within [0, n_pegs).")

        self.n_pegs = n_pegs
        self.disks = list(disks)
        self.steps = steps
        self._rules: HanoiRules | None = None

    def hash(self) -> int:
        """Return a stable hash representation for this position.

        Args:
            None.

        Returns:
            int: Deterministic integer hash for the current board state.
        """
        return hash((self.n_pegs, tuple(self.disks), self.steps))

    def __str__(self) -> str:
        """Return a compact textual representation of this Hanoi position.

        Args:
            None.

        Returns:
            str: Human-readable state summary.
        """
        goal_peg = self.n_pegs - 1
        disks_on_goal = sum(1 for peg in self.disks if peg == goal_peg)
        return (
            "HanoiPosition("
            f"steps={self.steps}, "
            f"pegs={self.n_pegs}, "
            f"disks={self.disks}, "
            f"goal_progress={disks_on_goal}/{len(self.disks)}"
            ")"
        )

    def next_player(self) -> PlayerIndex:
        """Return the next player that must act from this position.

        Args:
            None.

        Returns:
            PlayerIndex: Identifier of the player expected to play next.
        """
        return PlayerIndex(0)

    def get_rules(self) -> Rules:
        """Return the rules object associated with this position.

        Args:
            None.

        Returns:
            Rules: Rules instance that can validate and evolve this position.
        """
        if self._rules is None:
            from iarena.gaming.hanoi.HanoiConfiguration import HanoiConfiguration
            from iarena.gaming.hanoi.HanoiRules import HanoiRules

            self._rules = HanoiRules(HanoiConfiguration(self.n_pegs, self.disks))
        return self._rules
