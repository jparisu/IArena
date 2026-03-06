"""Shared test doubles for arena-module tests."""

from __future__ import annotations

import time
from collections.abc import Iterator, Sequence
from dataclasses import dataclass

from iarena.desining.gaming.GameRules import GameRules
from iarena.desining.gaming.Movement import Movement
from iarena.desining.playing.Player import Player, PlayerIndex
from iarena.desining.gaming.Position import Position
from iarena.desining.gaming.ScoreBoard import ScoreBoard
from iarena.desining.visualing.TerminalGame import TerminalGame
from iarena.utilizing.protocoling import ITextRenderable


@dataclass(frozen=True, slots=True)
class DummyMovement(Movement, ITextRenderable):
    """Simple movement used for arena tests."""

    label: str
    amount: float

    def to_text(self) -> str:
        """Return terminal-friendly movement text.

        Args:
            None.

        Returns:
            Movement label.
        """
        return self.label


@dataclass(frozen=True, slots=True)
class DummyPosition(Position, ITextRenderable):
    """Simple position with round-robin turns and cumulative per-player scores."""

    scores: tuple[float, ...]
    turn_count: int
    next_player_index: int

    def next_player(self) -> PlayerIndex:
        """Return index for the active player.

        Args:
            None.

        Returns:
            Active player index.
        """
        return self.next_player_index

    def to_text(self) -> str:
        """Return terminal-friendly position text.

        Args:
            None.

        Returns:
            Multi-field textual summary.
        """
        return f"turn={self.turn_count}, next_player={self.next_player_index}, scores={self.scores}"


class DummyRules(GameRules, ITextRenderable, TerminalGame):
    """Minimal deterministic rules for arena tests."""

    def __init__(
        self,
        n_players: int,
        max_turns: int,
        allowed_movements: Sequence[DummyMovement] | None = None,
    ) -> None:
        """Initialize deterministic rules.

        Args:
            n_players: Number of players.
            max_turns: Turn count where game becomes finished.
            allowed_movements: Legal movements for every turn.

        Returns:
            None.
        """
        self._n_players = n_players
        self._max_turns = max_turns
        if allowed_movements is None:
            self._allowed_movements = (DummyMovement(label="inc", amount=1.0),)
        else:
            self._allowed_movements = tuple(allowed_movements)

    def n_players(self) -> int:
        """Return number of players.

        Args:
            None.

        Returns:
            Number of players.
        """
        return self._n_players

    def first_position(self) -> DummyPosition:
        """Return initial position.

        Args:
            None.

        Returns:
            Initial position with zero scores.
        """
        return DummyPosition(scores=tuple(0.0 for _ in range(self._n_players)), turn_count=0, next_player_index=0)

    def next_position(self, movement: Movement, position: Position) -> DummyPosition:
        """Apply movement and return next position.

        Args:
            movement: Movement to apply.
            position: Current position.

        Returns:
            Updated position.
        """
        if not isinstance(position, DummyPosition):
            raise TypeError("position must be DummyPosition")
        if not isinstance(movement, DummyMovement):
            raise TypeError("movement must be DummyMovement")

        scores = list(position.scores)
        active_player = position.next_player()
        scores[active_player] += movement.amount
        return DummyPosition(
            scores=tuple(scores),
            turn_count=position.turn_count + 1,
            next_player_index=(active_player + 1) % self._n_players,
        )

    def possible_movements(self, position: Position) -> Iterator[DummyMovement]:
        """Yield legal movements.

        Args:
            position: Current position.

        Returns:
            Iterator with legal movements.
        """
        del position
        yield from self._allowed_movements

    def finished(self, position: Position) -> bool:
        """Return whether the game reached its turn cap.

        Args:
            position: Current position.

        Returns:
            ``True`` when turn count reached configured cap.
        """
        if not isinstance(position, DummyPosition):
            raise TypeError("position must be DummyPosition")
        return position.turn_count >= self._max_turns

    def score(self, position: Position) -> ScoreBoard:
        """Build score board from position scores.

        Args:
            position: Current position.

        Returns:
            Scoreboard with position values.
        """
        if not isinstance(position, DummyPosition):
            raise TypeError("position must be DummyPosition")
        board = ScoreBoard(self._n_players)
        for player_index, score in enumerate(position.scores):
            board.define_score(player_index, score)
        return board

    def to_text(self) -> str:
        """Return terminal-friendly rules text.

        Args:
            None.

        Returns:
            Short textual summary.
        """
        return (
            f"DummyRules(n_players={self._n_players}, max_turns={self._max_turns}, "
            f"movements={[movement.label for movement in self._allowed_movements]})"
        )

    def terminal_instructions(self) -> str | None:
        """Return terminal instructions for this dummy game.

        Args:
            None.

        Returns:
            Rules description text.
        """
        return self.to_text()

    def position_to_terminal(self, position: Position) -> str:
        """Convert one position into terminal-friendly text.

        Args:
            position: Position to convert.

        Returns:
            Position text representation.
        """
        if not isinstance(position, DummyPosition):
            raise TypeError("position must be DummyPosition")
        return position.to_text()

    def movement_to_terminal(self, movement: Movement) -> str:
        """Convert one movement into terminal-friendly text.

        Args:
            movement: Movement to convert.

        Returns:
            Movement text representation.
        """
        if not isinstance(movement, DummyMovement):
            raise TypeError("movement must be DummyMovement")
        return movement.to_text()


class FixedMovementPlayer(Player):
    """Player that always returns the same movement."""

    def __init__(self, movement: DummyMovement, sleep_seconds: float = 0.0, name: str | None = None) -> None:
        """Initialize fixed-movement player.

        Args:
            movement: Movement returned by every call to ``play``.
            sleep_seconds: Optional delay to simulate slow turns.
            name: Optional display name.

        Returns:
            None.
        """
        super().__init__(name=name)
        self._movement = movement
        self._sleep_seconds = sleep_seconds

    def play(self, position: Position) -> Movement:
        """Return the configured movement.

        Args:
            position: Current position.

        Returns:
            Configured movement.
        """
        del position
        if self._sleep_seconds > 0.0:
            time.sleep(self._sleep_seconds)
        return self._movement


class FailingPlayer(Player):
    """Player that always raises an exception when asked to play."""

    def __init__(self, error_message: str) -> None:
        """Initialize failing player with deterministic error message.

        Args:
            error_message: Message used in raised runtime error.

        Returns:
            None.
        """
        super().__init__(name="FailingPlayer")
        self._error_message = error_message

    def play(self, position: Position) -> Movement:
        """Raise a runtime error when the arena asks for a movement.

        Args:
            position: Current position.

        Returns:
            Never returns.
        """
        del position
        raise RuntimeError(self._error_message)
