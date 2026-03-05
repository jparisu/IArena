"""Arena stop-condition implementations for time, turn, and score limits."""

from __future__ import annotations

from iarena.arening.ArenaCommon import (
    PENALTY_SCORE,
    ArenaContext,
    ArenaStopCondition,
    ArenaStopDecision,
    ArenaTurnRecord,
    clone_score_board,
    penalty_for_all_players,
)


class PerTurnTimeLimitCondition(ArenaStopCondition):
    """Stop when one player exceeds per-turn time budget."""

    def __init__(self, max_seconds_per_turn: float, penalty_score: float = PENALTY_SCORE) -> None:
        """Initialize per-turn time limit.
        Args:
            max_seconds_per_turn: Allowed seconds per turn.
            penalty_score: Score assigned to the offending player.
        Returns:
            None.
        """
        if max_seconds_per_turn <= 0.0:
            raise ValueError("max_seconds_per_turn must be > 0")
        self._max_seconds_per_turn = max_seconds_per_turn
        self._penalty_score = penalty_score

    def check_after_turn(self, context: ArenaContext, turn_record: ArenaTurnRecord) -> ArenaStopDecision | None:
        """Stop when one turn exceeds limit.
        Args:
            context: Arena context after turn.
            turn_record: Data for the completed turn.
        Returns:
            Stop decision or ``None``.
        """
        if turn_record.elapsed_seconds <= self._max_seconds_per_turn:
            return None
        return self.decision_for_timeout(
            context=context,
            player_index=turn_record.player_index,
            elapsed_seconds=turn_record.elapsed_seconds,
        )

    def max_seconds_per_turn(self) -> float:
        """Return configured timeout threshold for one player turn.

        Args:
            None.

        Returns:
            Maximum allowed seconds for one turn.
        """
        return self._max_seconds_per_turn

    def decision_for_timeout(
        self,
        context: ArenaContext,
        player_index: int,
        elapsed_seconds: float,
    ) -> ArenaStopDecision:
        """Build stop decision for one detected turn-time overflow.

        Args:
            context: Current arena context.
            player_index: Index of player that exceeded timeout.
            elapsed_seconds: Elapsed turn time measured for player call.

        Returns:
            Stop decision with offender penalty.
        """
        final_score = clone_score_board(context.current_score)
        final_score.define_score(player_index, self._penalty_score)
        return ArenaStopDecision(
            reason=(
                "per-turn time limit exceeded by player "
                f"{player_index}: {elapsed_seconds:.6f}s > {self._max_seconds_per_turn:.6f}s"
            ),
            final_score=final_score,
        )


class GameTimeLimitCondition(ArenaStopCondition):
    """Stop when total game time exceeds budget."""

    def __init__(self, max_game_seconds: float, penalty_score: float = PENALTY_SCORE) -> None:
        """Initialize whole-game time limit.
        Args:
            max_game_seconds: Allowed seconds for full game.
            penalty_score: Score assigned to every player on timeout.
        Returns:
            None.
        """
        if max_game_seconds <= 0.0:
            raise ValueError("max_game_seconds must be > 0")
        self._max_game_seconds = max_game_seconds
        self._penalty_score = penalty_score

    def _check(self, context: ArenaContext) -> ArenaStopDecision | None:
        """Evaluate whole-game elapsed time.
        Args:
            context: Current arena context.
        Returns:
            Stop decision or ``None``.
        """
        if context.game_elapsed_seconds <= self._max_game_seconds:
            return None
        return ArenaStopDecision(
            reason=(f"game time limit exceeded: {context.game_elapsed_seconds:.6f}s > {self._max_game_seconds:.6f}s"),
            final_score=penalty_for_all_players(context.rules.n_players(), self._penalty_score),
        )

    def check_before_turn(self, context: ArenaContext) -> ArenaStopDecision | None:
        """Evaluate limit before requesting movement.
        Args:
            context: Current arena context.
        Returns:
            Stop decision or ``None``.
        """
        return self._check(context)

    def check_after_turn(self, context: ArenaContext, turn_record: ArenaTurnRecord) -> ArenaStopDecision | None:
        """Evaluate limit after applying movement.
        Args:
            context: Current arena context.
            turn_record: Data for completed turn.
        Returns:
            Stop decision or ``None``.
        """
        del turn_record
        return self._check(context)


class TurnLimitCondition(ArenaStopCondition):
    """Stop when a new turn would exceed max turns."""

    def __init__(self, max_turns: int, penalty_score: float = PENALTY_SCORE) -> None:
        """Initialize turn limit.
        Args:
            max_turns: Maximum allowed turns.
            penalty_score: Score assigned to all players after overflow.
        Returns:
            None.
        """
        if max_turns <= 0:
            raise ValueError("max_turns must be > 0")
        self._max_turns = max_turns
        self._penalty_score = penalty_score

    def check_before_turn(self, context: ArenaContext) -> ArenaStopDecision | None:
        """Evaluate turn count before new movement.
        Args:
            context: Current arena context.
        Returns:
            Stop decision or ``None``.
        """
        if context.turn_count < self._max_turns:
            return None
        return ArenaStopDecision(
            reason=f"turn limit exceeded: attempted turn {context.turn_count + 1} with max_turns={self._max_turns}",
            final_score=penalty_for_all_players(context.rules.n_players(), self._penalty_score),
        )


class ScoreLimitCondition(ArenaStopCondition):
    """Stop when any player reaches a minimum score."""

    def __init__(self, min_score: float) -> None:
        """Initialize score threshold.
        Args:
            min_score: Minimum score that triggers game end.
        Returns:
            None.
        """
        self._min_score = min_score

    def _check(self, context: ArenaContext) -> ArenaStopDecision | None:
        """Evaluate current scores.
        Args:
            context: Current arena context.
        Returns:
            Stop decision or ``None``.
        """
        for player_index in range(context.current_score.n_players()):
            current_value = context.current_score.get_score(player_index)
            if current_value >= self._min_score:
                return ArenaStopDecision(
                    reason=f"score limit reached by player {player_index}: {current_value} >= {self._min_score}"
                )
        return None

    def check_before_turn(self, context: ArenaContext) -> ArenaStopDecision | None:
        """Evaluate score threshold before requesting movement.
        Args:
            context: Current arena context.
        Returns:
            Stop decision or ``None``.
        """
        return self._check(context)

    def check_after_turn(self, context: ArenaContext, turn_record: ArenaTurnRecord) -> ArenaStopDecision | None:
        """Evaluate score threshold after applying movement.
        Args:
            context: Current arena context.
            turn_record: Data for completed turn.
        Returns:
            Stop decision or ``None``.
        """
        del turn_record
        return self._check(context)
