"""Lifecycle hooks and observer notifications used by generic arena implementations."""

from __future__ import annotations

from typing import Protocol

from iarena.arening.ArenaBehaviors import ArenaContext, ArenaTurnRecord
from iarena.arening.ArenaCommon import IArenaObserver
from iarena.interfacing.IGameRules import IGameRules
from iarena.interfacing.IPosition import IPosition
from iarena.interfacing.ScoreBoard import ScoreBoard


class _ArenaLifecycleHost(Protocol):
    """Protocol describing runtime attributes required by lifecycle mixin."""

    rules: IGameRules
    position: IPosition
    _observers: tuple[IArenaObserver, ...]
    _end_reason: str | None

    def _build_context(self, current_score: ScoreBoard) -> ArenaContext:
        """Build context snapshot from current score.

        Args:
            current_score: Current score for current position.

        Returns:
            Context snapshot.
        """
        raise NotImplementedError

    def _on_game_start(self, context: ArenaContext) -> None:
        """Hook called when game starts.

        Args:
            context: Initial arena context.

        Returns:
            None.
        """
        raise NotImplementedError

    def _on_turn_end(self, turn_record: ArenaTurnRecord, context: ArenaContext) -> None:
        """Hook called after one movement.

        Args:
            turn_record: Completed turn data.
            context: Context after completed turn.

        Returns:
            None.
        """
        raise NotImplementedError

    def _on_game_end(self, final_position: IPosition, final_score: ScoreBoard, reason: str | None) -> None:
        """Hook called when game ends.

        Args:
            final_position: Final game position.
            final_score: Final scoreboard.
            reason: Optional early-stop reason.

        Returns:
            None.
        """
        raise NotImplementedError


class GenericArenaLifecycleMixin:
    """Provide default hook methods and observer notifications."""

    def _on_game_start(self, context: ArenaContext) -> None:
        """Hook called when game starts.

        Args:
            context: Initial arena context.

        Returns:
            None.
        """
        del context

    def _on_turn_start(self, context: ArenaContext, player_index: int) -> None:
        """Hook called before requesting movement.

        Args:
            context: Current arena context.
            player_index: Active player index.

        Returns:
            None.
        """
        del context, player_index

    def _on_turn_end(self, turn_record: ArenaTurnRecord, context: ArenaContext) -> None:
        """Hook called after applying one movement.

        Args:
            turn_record: Completed turn data.
            context: Context after completed turn.

        Returns:
            None.
        """
        del turn_record, context

    def _on_game_end(self, final_position: IPosition, final_score: ScoreBoard, reason: str | None) -> None:
        """Hook called when game ends.

        Args:
            final_position: Final game position.
            final_score: Final scoreboard.
            reason: Early-stop reason if any.

        Returns:
            None.
        """
        del final_position, final_score, reason

    def _notify_game_start(self: _ArenaLifecycleHost) -> None:
        """Notify game-start hook and observers.

        Args:
            None.

        Returns:
            None.
        """
        context = self._build_context(self.rules.current_score(self.position))
        self._on_game_start(context)
        for observer in self._observers:
            observer.on_game_start(self.position)

    def _notify_turn_end(self: _ArenaLifecycleHost, turn_record: ArenaTurnRecord, context: ArenaContext) -> None:
        """Notify turn-end hook and observers.

        Args:
            turn_record: Completed turn data.
            context: Context after completed turn.

        Returns:
            None.
        """
        self._on_turn_end(turn_record, context)
        for observer in self._observers:
            observer.on_turn_end(turn_record, context)

    def _notify_game_end(self: _ArenaLifecycleHost, final_score: ScoreBoard) -> None:
        """Notify game-end hook and observers.

        Args:
            final_score: Final scoreboard.

        Returns:
            None.
        """
        self._on_game_end(self.position, final_score, self._end_reason)
        for observer in self._observers:
            observer.on_game_end(self.position, final_score, self._end_reason)
