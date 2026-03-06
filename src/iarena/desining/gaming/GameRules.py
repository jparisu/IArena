"""Abstract interface that defines game mechanics and state transitions."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterator
from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from iarena.desining.gaming.Movement import Movement
    from iarena.desining.gaming.Position import Position
    from iarena.desining.gaming.ScoreBoard import ScoreBoard


class GameRules(ABC):
    """Define the lifecycle of a turn-based game."""

    @abstractmethod
    def n_players(self) -> int:
        """Return how many players participate in this game.

        Args:
            None.

        Returns:
            Number of players in one match.
        """
        raise NotImplementedError

    @abstractmethod
    def first_position(self) -> Position:
        """Build and return the initial position of a new game.

        Args:
            None.

        Returns:
            Initial game position.
        """
        raise NotImplementedError

    @abstractmethod
    def next_position(self, movement: Movement, position: Position) -> Position:
        """Compute the position reached after applying a movement.

        Args:
            movement: Movement chosen by the active player.
            position: Current position before the movement is applied.

        Returns:
            The resulting position after the movement.
        """
        raise NotImplementedError

    @abstractmethod
    def possible_movements(self, position: Position) -> Iterator[Movement]:
        """Yield legal movements available from a given position.

        Args:
            position: Position to evaluate.

        Returns:
            Iterator over legal movements.
        """
        raise NotImplementedError

    @abstractmethod
    def finished(self, position: Position) -> bool:
        """Return whether a game is terminal for the given position.

        Args:
            position: Position to evaluate.

        Returns:
            ``True`` when no more turns should be played.
        """
        raise NotImplementedError

    @abstractmethod
    def score(self, position: Position) -> ScoreBoard:
        """Evaluate and return the scoreboard for a given position.

        Args:
            position: Position to evaluate.

        Returns:
            Scoreboard associated with the provided position.
        """
        raise NotImplementedError

    def current_score(self, position: Position) -> ScoreBoard:
        """Return current scoreboard for a given position.

        Args:
            position: Position to evaluate.

        Returns:
            Current scoreboard.
        """
        return self.score(position)

    def is_movement_possible(self, movement: Movement, position: Position) -> bool:
        """Check whether a movement is legal in a given position.

        Args:
            movement: Movement to validate.
            position: Position to validate against.

        Returns:
            ``True`` when movement is legal.
        """
        return movement in self.possible_movements(position)


@runtime_checkable
class GameSolver(Protocol):
    """Opt-in capability for solving or bounding game outcomes."""

    def score_bounds(self, rules: GameRules) -> tuple[ScoreBoard, ScoreBoard]:
        """Return minimum and maximum scoreboards reachable by rules.

        Args:
            rules: Rules object to analyze.

        Returns:
            Tuple ``(min_score, max_score)``.
        """
        raise NotImplementedError
