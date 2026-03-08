"""Declares the concrete rules contract for the Hanoi game."""
# pylint: disable=too-many-lines  # TODO: review

from __future__ import annotations

from collections.abc import Iterator
from typing import TYPE_CHECKING

from iarena.gaming.Rules import Rules
from iarena.playing.PlayerIndex import PlayerIndex
from iarena.scoring.Score import Score
from iarena.scoring.ScoreBoard import ScoreBoard

if TYPE_CHECKING:
    from iarena.gaming.hanoi.HanoiConfiguration import HanoiConfiguration
    from iarena.gaming.Movement import Movement
    from iarena.gaming.Position import Position

from iarena.gaming.hanoi.HanoiMovement import HanoiMovement
from iarena.gaming.hanoi.HanoiPosition import HanoiPosition


class HanoiRules(Rules):
    """Concrete rules implementation for the Hanoi game.

    Purpose:
        Defines legal moves, turn progression, terminal conditions, and scoring for Hanoi.
    How it works:
        Applies Tower of Hanoi constraints to transform one position into the next.
    Used for:
        Match execution, move validation, and benchmark scoring workflows.
    Public Attributes:
        configuration (HanoiConfiguration): Configuration instance used to initialize the ruleset.
    """

    configuration: HanoiConfiguration

    def __init__(self, configuration: HanoiConfiguration) -> None:
        """Create one Hanoi rules engine bound to a concrete configuration.

        Args:
            configuration: Static setup used to derive initial and terminal states.

        Returns:
            None.
        """
        self.configuration = configuration

    def _require_position(self, pos: Position) -> HanoiPosition:
        """Return the validated Hanoi position used by rule operations.

        Args:
            pos: Candidate position object received by the public rules API.

        Returns:
            Validated `HanoiPosition` instance.

        Raises:
            TypeError: If `pos` is not a `HanoiPosition`.
            ValueError: If position peg count differs from rule configuration.
        """
        if not isinstance(pos, HanoiPosition):
            raise TypeError("pos must be an instance of HanoiPosition.")
        if pos.n_pegs != self.configuration.n_pegs:
            raise ValueError("Position peg count must match rule configuration.")
        return pos

    def _require_movement(self, mov: Movement) -> HanoiMovement:
        """Return the validated Hanoi movement used by rule transitions.

        Args:
            mov: Candidate movement object received by the public rules API.

        Returns:
            Validated `HanoiMovement` instance.

        Raises:
            TypeError: If `mov` is not a `HanoiMovement`.
        """
        if not isinstance(mov, HanoiMovement):
            raise TypeError("mov must be an instance of HanoiMovement.")
        return mov

    def _top_disk_index(self, disks: list[int], peg: int) -> int | None:
        """Return the movable top disk index for one peg.

        Args:
            disks: Current per-disk peg assignment list.
            peg: Peg index whose top disk should be queried.

        Returns:
            Index of the smallest disk currently on the peg, or `None` if peg is empty.
        """
        top: int | None = None
        for disk_index, disk_peg in enumerate(disks):
            if disk_peg == peg:
                top = disk_index
        return top

    def n_players(self) -> int:
        """Return the number of players supported by this ruleset.

        Args:
            None.

        Returns:
            int: Number of participating players.
        """
        return 1

    def first_position(self) -> Position:
        """Return the initial position for a newly started Hanoi match.

        Args:
            None.

        Returns:
            Position: Initial state derived from the configured puzzle layout.
        """
        position = HanoiPosition(
            n_pegs=self.configuration.n_pegs,
            disks=self.configuration.disks,
            steps=0,
        )
        position._rules = self
        return position

    def next_position(self, pos: Position, mov: Movement) -> Position:
        """Return the position produced after applying one movement.

        Args:
            pos: Source position where the movement is applied.
            mov: Candidate movement to evaluate and execute.

        Returns:
            Position: Position generated after the movement is applied.
        """
        hanoi_pos = self._require_position(pos)
        hanoi_mov = self._require_movement(mov)

        if hanoi_mov.from_peg >= hanoi_pos.n_pegs or hanoi_mov.to_peg >= hanoi_pos.n_pegs:
            raise ValueError("Movement peg indices must be within [0, n_pegs).")

        moving_disk = self._top_disk_index(hanoi_pos.disks, hanoi_mov.from_peg)
        if moving_disk is None:
            raise ValueError("Cannot move a disk from an empty peg.")

        target_top = self._top_disk_index(hanoi_pos.disks, hanoi_mov.to_peg)
        if target_top is not None and moving_disk < target_top:
            raise ValueError("Cannot place a larger disk on top of a smaller disk.")

        next_disks = list(hanoi_pos.disks)
        next_disks[moving_disk] = hanoi_mov.to_peg

        next_position = HanoiPosition(
            n_pegs=hanoi_pos.n_pegs,
            disks=next_disks,
            steps=hanoi_pos.steps + 1,
        )
        next_position._rules = self
        return next_position

    def possible_movements(self, pos: Position) -> Iterator[Movement]:
        """Yield all legal movements available from the provided position.

        Args:
            pos: Position whose legal outgoing moves must be enumerated.

        Returns:
            Iterator[Movement]: Lazy iterator over legal movements.
        """
        hanoi_pos = self._require_position(pos)

        for from_peg in range(hanoi_pos.n_pegs):
            moving_disk = self._top_disk_index(hanoi_pos.disks, from_peg)
            if moving_disk is None:
                continue

            for to_peg in range(hanoi_pos.n_pegs):
                if to_peg == from_peg:
                    continue
                target_top = self._top_disk_index(hanoi_pos.disks, to_peg)
                if target_top is None or moving_disk > target_top:
                    yield HanoiMovement(from_peg=from_peg, to_peg=to_peg)

    def is_finished(self, pos: Position) -> bool:
        """Return whether the provided position is terminal.

        Args:
            pos: Position to evaluate against Hanoi completion conditions.

        Returns:
            bool: `True` when the puzzle is solved, else `False`.
        """
        hanoi_pos = self._require_position(pos)
        if not hanoi_pos.disks:
            return True
        target_peg = hanoi_pos.n_pegs - 1
        return all(peg == target_peg for peg in hanoi_pos.disks)

    def get_score(self, pos: Position) -> ScoreBoard:
        """Return the scoreboard representation associated with a position.

        Args:
            pos: Position whose score must be derived.

        Returns:
            ScoreBoard: Scoreboard object representing the current match result.
        """
        hanoi_pos = self._require_position(pos)
        board = ScoreBoard()
        board._scores = {PlayerIndex(0): Score(float(-hanoi_pos.steps))}
        return board
