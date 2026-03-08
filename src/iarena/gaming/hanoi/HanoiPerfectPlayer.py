"""Declares the ideal-strategy player type for the Hanoi game."""

from __future__ import annotations

from collections import deque
from typing import TYPE_CHECKING

from iarena.playing.Player import Player

if TYPE_CHECKING:
    from iarena.gaming.hanoi.HanoiMovement import HanoiMovement
    from iarena.gaming.hanoi.HanoiPosition import HanoiPosition
    from iarena.gaming.hanoi.HanoiRules import HanoiRules
    from iarena.playing.PlayerIndex import PlayerIndex

from iarena.gaming.hanoi.HanoiMovement import HanoiMovement


class HanoiPerfectPlayer(Player):
    """Concrete player implementation that uses the optimal Hanoi solution strategy.

    Purpose:
        Represents an automated Hanoi player intended to choose optimal moves.
    How it works:
        Consumes current position and rules context to output the next movement.
    Used for:
        Baseline benchmarking and deterministic puzzle solving in Hanoi arenas.
    Public Attributes:
        None declared at class level in this base definition.
    """

    def name(self) -> str:
        """Return the canonical player name for displays and registries.

        Args:
            None.

        Returns:
            str: Stable identifier for this player strategy.
        """
        return "hanoi-perfect"

    def _top_disk_index(self, disks: tuple[int, ...], peg: int) -> int | None:
        """Return the index of the top movable disk currently on one peg.

        Args:
            disks: Per-disk peg assignment tuple.
            peg: Peg index whose top disk should be queried.

        Returns:
            Disk index for the top movable disk, or `None` if the peg is empty.
        """
        top: int | None = None
        for disk_index, disk_peg in enumerate(disks):
            if disk_peg == peg:
                top = disk_index
        return top

    def _legal_moves(self, state: tuple[int, ...], n_pegs: int) -> list[HanoiMovement]:
        """Return all legal moves from one Hanoi state.

        Args:
            state: Per-disk peg assignment tuple.
            n_pegs: Number of pegs available in the puzzle.

        Returns:
            List of legal `HanoiMovement` objects from `state`.
        """
        moves: list[HanoiMovement] = []
        for from_peg in range(n_pegs):
            moving_disk = self._top_disk_index(state, from_peg)
            if moving_disk is None:
                continue
            for to_peg in range(n_pegs):
                if to_peg == from_peg:
                    continue
                target_top = self._top_disk_index(state, to_peg)
                if target_top is None or moving_disk > target_top:
                    moves.append(HanoiMovement(from_peg=from_peg, to_peg=to_peg))
        return moves

    def _apply_move(self, state: tuple[int, ...], move: HanoiMovement) -> tuple[int, ...]:
        """Return the next state produced by applying one legal move.

        Args:
            state: Per-disk peg assignment tuple.
            move: Legal movement to apply.

        Returns:
            New per-disk peg assignment tuple.
        """
        moving_disk = self._top_disk_index(state, move.from_peg)
        if moving_disk is None:
            raise ValueError("Cannot apply move from an empty peg.")

        next_state = list(state)
        next_state[moving_disk] = move.to_peg
        return tuple(next_state)

    def _compute_next_move(self, pos: HanoiPosition) -> HanoiMovement:
        """Compute the first move of one shortest path from `pos` to the goal.

        Args:
            pos: Current Hanoi position.

        Returns:
            Hanoi movement that advances along a shortest solution path.

        Raises:
            ValueError: If no path to goal exists or the puzzle is already solved.
        """
        start = tuple(pos.disks)
        goal = tuple([pos.n_pegs - 1] * len(pos.disks))

        if start == goal:
            raise ValueError("No movement available: the puzzle is already solved.")

        queue: deque[tuple[int, ...]] = deque([start])
        visited: set[tuple[int, ...]] = {start}
        parent: dict[tuple[int, ...], tuple[tuple[int, ...], HanoiMovement]] = {}

        while queue:
            current = queue.popleft()
            if current == goal:
                break

            for move in self._legal_moves(current, pos.n_pegs):
                nxt = self._apply_move(current, move)
                if nxt in visited:
                    continue
                visited.add(nxt)
                parent[nxt] = (current, move)
                queue.append(nxt)

        if goal not in parent:
            raise ValueError("Could not compute a path to the Hanoi goal state.")

        trace_state = goal
        while parent[trace_state][0] != start:
            trace_state = parent[trace_state][0]
        return parent[trace_state][1]

    def play(self, pos: HanoiPosition) -> HanoiMovement:
        """Select and return the next movement for the provided position.

        Args:
            pos: Current Hanoi position where the player must act.

        Returns:
            HanoiMovement: Movement selected according to the player strategy.
        """
        return self._compute_next_move(pos)

    def starting_game(self, rules: HanoiRules, player_index: PlayerIndex) -> None:
        """Initialize player state when a new Hanoi game starts.

        Args:
            rules: Rules instance for the game about to begin.
            player_index: Index assigned to this player in the current arena match.

        Returns:
            None.
        """
        self._rules = rules
        self._player_index = player_index
