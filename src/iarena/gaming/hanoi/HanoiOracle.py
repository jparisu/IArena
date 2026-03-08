"""Declares the concrete benchmark oracle for the Hanoi game."""

from __future__ import annotations

from collections import deque
from typing import TYPE_CHECKING

from iarena.gaming.Oracle import Oracle
from iarena.playing.PlayerIndex import PlayerIndex
from iarena.scoring.Score import Score
from iarena.scoring.ScoreBoard import ScoreBoard

if TYPE_CHECKING:
    from iarena.gaming.Rules import Rules

from iarena.gaming.hanoi.HanoiRules import HanoiRules


class HanoiOracle(Oracle):
    """Concrete benchmark oracle implementation for Hanoi.

    Purpose:
        Computes reference best/worst score bounds for configured Hanoi games.
    How it works:
        Analyzes the puzzle definition and derives expected benchmark outcomes.
    Used for:
        Match evaluation, grading, and performance comparison against optimal play.
    Public Attributes:
        None declared at class level in this base definition.
    """

    @classmethod
    def _top_disk_index(cls, state: tuple[int, ...], peg: int) -> int | None:
        """Return the top movable disk index from one peg in a raw state tuple.

        Args:
            state: Per-disk peg assignment tuple.
            peg: Peg index whose top disk should be queried.

        Returns:
            int | None: Top disk index for the peg, or `None` when empty.
        """
        _ = cls
        top: int | None = None
        for disk_index, disk_peg in enumerate(state):
            if disk_peg == peg:
                top = disk_index
        return top

    @classmethod
    def _optimal_steps(cls, n_pegs: int, start: tuple[int, ...], goal: tuple[int, ...]) -> int:
        """Return the shortest number of moves to reach goal from start.

        Args:
            n_pegs: Number of available pegs.
            start: Initial per-disk peg assignment.
            goal: Goal per-disk peg assignment.

        Returns:
            int: Optimal number of required moves.
        """
        if start == goal:
            return 0

        queue: deque[tuple[tuple[int, ...], int]] = deque([(start, 0)])
        visited: set[tuple[int, ...]] = {start}

        while queue:
            state, steps = queue.popleft()
            if state == goal:
                return steps

            for from_peg in range(n_pegs):
                moving_disk = cls._top_disk_index(state, from_peg)
                if moving_disk is None:
                    continue

                for to_peg in range(n_pegs):
                    if to_peg == from_peg:
                        continue

                    target_top = cls._top_disk_index(state, to_peg)
                    if target_top is not None and moving_disk < target_top:
                        continue

                    next_state = list(state)
                    next_state[moving_disk] = to_peg
                    next_state_tuple = tuple(next_state)
                    if next_state_tuple in visited:
                        continue

                    visited.add(next_state_tuple)
                    queue.append((next_state_tuple, steps + 1))

        raise ValueError("Could not derive an optimal Hanoi path for the provided configuration.")

    @classmethod
    def reckon_solution_score(cls, rules: Rules) -> tuple[ScoreBoard, ScoreBoard]:
        """Compute benchmark scoreboards for the provided Hanoi ruleset.

        Args:
            rules: Rules instance to evaluate for benchmark score bounds.

        Returns:
            tuple[ScoreBoard, ScoreBoard]: Pair with best-case and worst-case scoreboards.
        """
        _ = cls

        if not isinstance(rules, HanoiRules):
            raise TypeError("rules must be an instance of HanoiRules.")

        start_position = rules.first_position()
        start_state = tuple(start_position.disks)
        goal_state = tuple([start_position.n_pegs - 1] * len(start_position.disks))

        optimal_steps = cls._optimal_steps(start_position.n_pegs, start_state, goal_state)
        optimal_score = Score(float(-optimal_steps))

        best_board = ScoreBoard()
        worst_board = ScoreBoard()
        best_board._scores = {PlayerIndex(0): optimal_score}
        worst_board._scores = {PlayerIndex(0): optimal_score}
        return best_board, worst_board
