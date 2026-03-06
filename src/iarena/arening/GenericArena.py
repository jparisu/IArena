"""Concrete arena loop implementation using shared base helpers."""

from __future__ import annotations

import time

from iarena.arening.ArenaBehaviors import ArenaContext, ArenaStopDecision, ArenaTurnRecord, PerTurnTimeLimitCondition
from iarena.arening.ArenaExceptions import ArenaStoppedError
from iarena.arening.GenericArenaBase import GenericArenaBase
from iarena.desining.gaming.Movement import Movement
from iarena.desining.gaming.ScoreBoard import ScoreBoard
from iarena.desining.playing.Player import Player
from iarena.utilizing.threadinging import ThreadCallTimeoutError, run_callable_in_worker_thread


class GenericArena(GenericArenaBase):
    """Run game turns until rules finish or one stop condition triggers."""

    def _first_stop_decision(
        self,
        context: ArenaContext,
        turn_record: ArenaTurnRecord | None,
    ) -> ArenaStopDecision | None:
        """Evaluate stop conditions in declaration order.

        Args:
            context: Current arena context.
            turn_record: Completed turn data or ``None`` before turn.

        Returns:
            First stop decision that triggers, otherwise ``None``.
        """
        for condition in self._stop_conditions:
            decision = (
                condition.check_before_turn(context)
                if turn_record is None
                else condition.check_after_turn(context, turn_record)
            )
            if decision is not None:
                return decision
        return None

    def _per_turn_conditions(self) -> tuple[PerTurnTimeLimitCondition, ...]:
        """Return all per-turn timeout conditions configured for this arena.

        Args:
            None.

        Returns:
            Tuple with per-turn timeout conditions.
        """
        return tuple(
            condition for condition in self._stop_conditions if isinstance(condition, PerTurnTimeLimitCondition)
        )

    def _request_movement_timed(self, player: Player, player_index: int) -> tuple[Movement, float]:
        """Request one movement, enforcing thread timeout when configured.

        Args:
            player: Active player instance.
            player_index: Active player index.

        Returns:
            Tuple ``(movement, elapsed_seconds)``.

        Raises:
            ThreadCallTimeoutError: If one per-turn timeout threshold is exceeded.
            BaseException: Re-raises any exception from player call.
        """
        turn_start = time.perf_counter()
        per_turn_conditions = self._per_turn_conditions()
        if not per_turn_conditions:
            movement = self._request_movement(player, player_index)
            return movement, time.perf_counter() - turn_start

        min_timeout = min(condition.max_seconds_per_turn() for condition in per_turn_conditions)
        movement = run_callable_in_worker_thread(
            callable_function=lambda: self._request_movement(player, player_index),
            timeout_seconds=min_timeout,
        )
        return movement, time.perf_counter() - turn_start

    def _decision_for_thread_timeout(
        self,
        context: ArenaContext,
        player_index: int,
        timeout_error: ThreadCallTimeoutError,
    ) -> ArenaStopDecision:
        """Build the stop decision triggered by a timeout in the worker thread.

        Args:
            context: Current arena context before movement application.
            player_index: Active player index.
            timeout_error: Captured worker-thread timeout error.

        Returns:
            Stop decision for the strictest exceeded per-turn condition.
        """
        timeout_conditions = sorted(
            self._per_turn_conditions(),
            key=lambda condition: condition.max_seconds_per_turn(),
        )
        if not timeout_conditions:
            raise RuntimeError("thread timeout occurred without per-turn timeout condition")
        return timeout_conditions[0].decision_for_timeout(
            context=context,
            player_index=player_index,
            elapsed_seconds=timeout_error.elapsed_seconds,
        )

    def _finish(self, final_score: ScoreBoard, reason: str | None) -> ScoreBoard:
        """Finalize game metadata and notifications.

        Args:
            final_score: Final scoreboard.
            reason: Early-stop reason or ``None``.

        Returns:
            Final scoreboard.

        Raises:
            ArenaStoppedError: When ``reason`` is present and raising is enabled.
        """
        self._end_reason = reason
        self._game_timer.pause()
        self._notify_game_end(final_score)
        if reason is not None and self._raise_on_stop:
            raise ArenaStoppedError(reason=reason, final_score=final_score)
        return final_score

    def play(self) -> ScoreBoard:
        """Execute the arena loop.

        Args:
            None.

        Returns:
            Final scoreboard.
        """
        self._turn_count = 0
        self._end_reason = None
        self._game_timer.reset()
        self._game_timer.start()
        self._notify_game_start()

        while True:
            current_score = self.rules.current_score(self.position)
            context = self._build_context(current_score)
            decision = self._first_stop_decision(context, turn_record=None)
            if decision is not None:
                return self._finish(decision.final_score or current_score, decision.reason)
            if self.rules.finished(self.position):
                return self._finish(current_score, None)

            player_index = self.position.next_player()
            if player_index < 0 or player_index >= len(self.players):
                raise IndexError(
                    f"position returned next_player={player_index}, out of range [0, {len(self.players) - 1}]"
                )
            self._on_turn_start(context, player_index)

            player = self.players[player_index]
            position_before = self.position
            try:
                movement, elapsed_seconds = self._request_movement_timed(player, player_index)
            except ThreadCallTimeoutError as timeout_error:
                decision = self._decision_for_thread_timeout(context, player_index, timeout_error)
                return self._finish(decision.final_score or current_score, decision.reason)

            if not self.rules.is_movement_possible(movement, position_before):
                raise ValueError(f"illegal movement {movement!r} for player index {player_index}")

            self.position = self.rules.next_position(movement, position_before)
            self._turn_count += 1
            turn_record = ArenaTurnRecord(
                turn_index=self._turn_count,
                player_index=player_index,
                position_before=position_before,
                movement=movement,
                position_after=self.position,
                elapsed_seconds=elapsed_seconds,
            )
            current_score = self.rules.current_score(self.position)
            context = self._build_context(current_score)
            self._notify_turn_end(turn_record, context)
            decision = self._first_stop_decision(context, turn_record=turn_record)
            if decision is not None:
                return self._finish(decision.final_score or current_score, decision.reason)
