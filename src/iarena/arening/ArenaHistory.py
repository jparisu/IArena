"""Arena history storage for game analysis and replay."""

from __future__ import annotations

from dataclasses import dataclass

from iarena.arening.ArenaCommon import ArenaContext, ArenaTurnRecord, clone_score_board
from iarena.desining.gaming.Movement import Movement
from iarena.desining.gaming.Position import Position
from iarena.desining.gaming.ScoreBoard import ScoreBoard


@dataclass(frozen=True, slots=True)
class ArenaGameRecord:
    """Store one immutable full-game trace."""

    initial_position: Position
    turn_records: tuple[ArenaTurnRecord, ...]
    final_position: Position
    final_score: ScoreBoard
    end_reason: str | None

    def positions(self) -> tuple[Position, ...]:
        """Return ordered positions from start to end.

        Args:
            None.

        Returns:
            Tuple with initial position and each resulting position.
        """
        sequence = [self.initial_position]
        sequence.extend(turn_record.position_after for turn_record in self.turn_records)
        return tuple(sequence)

    def movements(self) -> tuple[Movement, ...]:
        """Return ordered movements in turn order.

        Args:
            None.

        Returns:
            Tuple of movements.
        """
        return tuple(turn_record.movement for turn_record in self.turn_records)


class GameHistoryObserver:
    """Observer that captures positions and movements for replay."""

    def __init__(self) -> None:
        """Initialize empty history storage.

        Args:
            None.

        Returns:
            None.
        """
        self._initial_position: Position | None = None
        self._turn_records: list[ArenaTurnRecord] = []
        self._final_position: Position | None = None
        self._final_score: ScoreBoard | None = None
        self._end_reason: str | None = None

    def on_game_start(self, initial_position: Position) -> None:
        """Reset storage and store initial position.

        Args:
            initial_position: Initial game position.

        Returns:
            None.
        """
        self._initial_position = initial_position
        self._turn_records = []
        self._final_position = None
        self._final_score = None
        self._end_reason = None

    def on_turn_end(self, turn_record: ArenaTurnRecord, context: ArenaContext) -> None:
        """Append one completed turn.

        Args:
            turn_record: Data for completed turn.
            context: Arena context after turn.

        Returns:
            None.
        """
        del context
        self._turn_records.append(turn_record)

    def on_game_end(self, final_position: Position, final_score: ScoreBoard, reason: str | None) -> None:
        """Store final game data.

        Args:
            final_position: Final game position.
            final_score: Final scoreboard.
            reason: Optional reason for early end.

        Returns:
            None.
        """
        self._final_position = final_position
        self._final_score = clone_score_board(final_score)
        self._end_reason = reason

    def record(self) -> ArenaGameRecord | None:
        """Build immutable record when game data is complete.

        Args:
            None.

        Returns:
            Immutable game record or ``None``.
        """
        if self._initial_position is None or self._final_position is None or self._final_score is None:
            return None
        return ArenaGameRecord(
            initial_position=self._initial_position,
            turn_records=tuple(self._turn_records),
            final_position=self._final_position,
            final_score=clone_score_board(self._final_score),
            end_reason=self._end_reason,
        )
