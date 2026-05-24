"""Declares the Dijkstra-based optimal player implementation for Hanoi."""

from __future__ import annotations

from typing import TYPE_CHECKING

from iarena.playing.DijkstraPlayer import DijkstraPlayer

if TYPE_CHECKING:
    from iarena.gaming.Position import Position

from iarena.gaming.hanoi.HanoiPosition import HanoiPosition


class PerfectHanoiPlayer(DijkstraPlayer):
    """Optimal Hanoi player built on top of the generic Dijkstra strategy.

    Purpose:
        Provide a concrete one-player strategy that always selects a move belonging
        to one shortest path to the solved Hanoi configuration.
    How it works:
        Reuses `DijkstraPlayer` search and defines position cost as number of
        performed steps in the current Hanoi position.
    Used for:
        Deterministic benchmark play and oracle score estimation in Hanoi games.
    Public Attributes:
        None declared at class level in this base definition.
    """

    def name(self) -> str:
        """Return the canonical player name for displays and registries.

        Returns:
            str: Stable identifier for this strategy.
        """
        return "hanoi-perfect"

    def current_cost(self, pos: Position) -> float:
        """Return the cumulative path cost associated with one Hanoi position.

        Args:
            pos: Position whose cumulative Hanoi cost should be returned.

        Returns:
            float: Number of executed steps to reach the provided position.
        """
        if not isinstance(pos, HanoiPosition):
            raise TypeError("pos must be an instance of HanoiPosition.")
        return float(pos.steps)
