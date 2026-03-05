"""Base class with shared runtime helpers for arena loop implementations."""

from __future__ import annotations

from collections.abc import Sequence

from iarena.arening.ArenaBehaviors import (
    ArenaContext,
    ArenaGameRecord,
    GameHistoryObserver,
    IArenaObserver,
    IArenaStopCondition,
)
from iarena.arening.GenericArenaLifecycle import GenericArenaLifecycleMixin
from iarena.interfacing.IArena import IArena
from iarena.interfacing.IGameRules import IGameRules
from iarena.interfacing.IMovement import IMovement
from iarena.interfacing.IPlayer import IPlayer
from iarena.interfacing.IPosition import IPosition
from iarena.interfacing.ScoreBoard import ScoreBoard
from iarena.utilizing.Timer import Timer


class GenericArenaBase(GenericArenaLifecycleMixin, IArena):
    """Provide shared context, hook, and observer helpers for concrete arenas."""

    def __init__(
        self,
        rules: IGameRules,
        players: Sequence[IPlayer],
        position: IPosition | None = None,
        stop_conditions: Sequence[IArenaStopCondition] | None = None,
        observers: Sequence[IArenaObserver] | None = None,
        raise_on_stop: bool = True,
    ) -> None:
        """Initialize arena runtime state.

        Args:
            rules: Rules object that defines transitions and score.
            players: Ordered list of players.
            position: Optional initial position.
            stop_conditions: Optional stop conditions.
            observers: Optional lifecycle observers.
            raise_on_stop: Whether stop conditions raise ``ArenaStoppedError``.

        Returns:
            None.
        """
        super().__init__(rules=rules, players=players, position=position)
        self._stop_conditions = tuple(stop_conditions or ())
        self._observers = tuple(observers or ())
        self._turn_count = 0
        self._game_timer = Timer(start_activated=False)
        self._end_reason: str | None = None
        self._raise_on_stop = raise_on_stop

    def turns_played(self) -> int:
        """Return completed turn count.

        Args:
            None.

        Returns:
            Number of completed turns.
        """
        return self._turn_count

    def end_reason(self) -> str | None:
        """Return stop-condition reason when game ended early.

        Args:
            None.

        Returns:
            Reason string or ``None``.
        """
        return self._end_reason

    def game_elapsed_seconds(self) -> float:
        """Return elapsed game time in seconds.

        Args:
            None.

        Returns:
            Elapsed seconds.
        """
        return self._game_timer.elapsed()

    def raises_on_stop(self) -> bool:
        """Return whether this arena raises when stop conditions trigger.

        Args:
            None.

        Returns:
            ``True`` when stop conditions raise exceptions.
        """
        return self._raise_on_stop

    def game_record(self) -> ArenaGameRecord | None:
        """Return game record if a history observer is attached.

        Args:
            None.

        Returns:
            Stored immutable record or ``None``.
        """
        for observer in self._observers:
            if isinstance(observer, GameHistoryObserver):
                return observer.record()
        return None

    def _build_context(self, current_score: ScoreBoard) -> ArenaContext:
        """Build context snapshot for hooks and stop conditions.

        Args:
            current_score: Current score for current position.

        Returns:
            Context snapshot.
        """
        return ArenaContext(
            rules=self.rules,
            players=self.players,
            position=self.position,
            turn_count=self._turn_count,
            game_elapsed_seconds=self._game_timer.elapsed(),
            current_score=current_score,
        )

    def _request_movement(self, player: IPlayer, player_index: int) -> IMovement:
        """Request one movement from active player.

        Args:
            player: Active player instance.
            player_index: Active player index.

        Returns:
            Movement selected by player.
        """
        del player_index
        return player.play(self.position)
