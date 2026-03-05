"""Shared arena data models, protocols, and helper functions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from iarena.interfacing.IGameRules import IGameRules
from iarena.interfacing.IMovement import IMovement
from iarena.interfacing.IPlayer import IPlayer, PlayerIndex
from iarena.interfacing.IPosition import IPosition
from iarena.interfacing.ScoreBoard import ScoreBoard

PENALTY_SCORE = -float("inf")


def clone_score_board(score_board: ScoreBoard) -> ScoreBoard:
    """Clone one scoreboard.

    Args:
        score_board: Source scoreboard.

    Returns:
        Independent copy with same player scores.
    """
    cloned = ScoreBoard(score_board.n_players())
    for player_index in range(score_board.n_players()):
        cloned.define_score(player_index, score_board.get_score(player_index))
    return cloned


def penalty_for_all_players(n_players: int, penalty_score: float = PENALTY_SCORE) -> ScoreBoard:
    """Build a scoreboard with equal penalty for all players.

    Args:
        n_players: Number of players.
        penalty_score: Score assigned to each player.

    Returns:
        Penalty scoreboard.
    """
    score_board = ScoreBoard(n_players)
    for player_index in range(n_players):
        score_board.define_score(player_index, penalty_score)
    return score_board


@dataclass(frozen=True, slots=True)
class ArenaTurnRecord:
    """Store one completed turn."""

    turn_index: int
    player_index: PlayerIndex
    position_before: IPosition
    movement: IMovement
    position_after: IPosition
    elapsed_seconds: float


@dataclass(frozen=True, slots=True)
class ArenaContext:
    """Expose current arena state to behavior plugins."""

    rules: IGameRules
    players: tuple[IPlayer, ...]
    position: IPosition
    turn_count: int
    game_elapsed_seconds: float
    current_score: ScoreBoard


@dataclass(frozen=True, slots=True)
class ArenaStopDecision:
    """Represent an early-stop decision."""

    reason: str
    final_score: ScoreBoard | None = None


@runtime_checkable
class IArenaStopCondition(Protocol):
    """Protocol for composable stop conditions."""

    def check_before_turn(self, context: ArenaContext) -> ArenaStopDecision | None:
        """Check if game must stop before one turn.

        Args:
            context: Current arena context.

        Returns:
            Stop decision or ``None``.
        """
        raise NotImplementedError

    def check_after_turn(self, context: ArenaContext, turn_record: ArenaTurnRecord) -> ArenaStopDecision | None:
        """Check if game must stop after one turn.

        Args:
            context: Current arena context.
            turn_record: Data for the completed turn.

        Returns:
            Stop decision or ``None``.
        """
        raise NotImplementedError


@runtime_checkable
class IArenaObserver(Protocol):
    """Protocol for arena lifecycle observers."""

    def on_game_start(self, initial_position: IPosition) -> None:
        """Receive game-start event.

        Args:
            initial_position: Initial game position.

        Returns:
            None.
        """
        raise NotImplementedError

    def on_turn_end(self, turn_record: ArenaTurnRecord, context: ArenaContext) -> None:
        """Receive turn-end event.

        Args:
            turn_record: Data for the completed turn.
            context: Arena context after the turn.

        Returns:
            None.
        """
        raise NotImplementedError

    def on_game_end(self, final_position: IPosition, final_score: ScoreBoard, reason: str | None) -> None:
        """Receive game-end event.

        Args:
            final_position: Final game position.
            final_score: Final scoreboard.
            reason: Optional reason for early end.

        Returns:
            None.
        """
        raise NotImplementedError


class ArenaStopCondition:
    """No-op base class for stop conditions."""

    def check_before_turn(self, context: ArenaContext) -> ArenaStopDecision | None:
        """Return no decision before turn.

        Args:
            context: Current arena context.

        Returns:
            ``None``.
        """
        del context
        return None

    def check_after_turn(self, context: ArenaContext, turn_record: ArenaTurnRecord) -> ArenaStopDecision | None:
        """Return no decision after turn.

        Args:
            context: Current arena context.
            turn_record: Data for completed turn.

        Returns:
            ``None``.
        """
        del context, turn_record
        return None
