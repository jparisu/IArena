"""Abstract interface that defines game mechanics and state transitions."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterator, Mapping
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    from iarena.interfacing.IMovement import IMovement
    from iarena.interfacing.IPosition import IPosition
    from iarena.interfacing.ScoreBoard import ScoreBoard


class IGameRules(ABC):
    """Defines the lifecycle of a turn-based game.

    Implementations are responsible for:
    - declaring supported number of players,
    - creating the initial game position,
    - applying movements to produce next positions,
    - enumerating legal movements for a position,
    - deciding when a game is finished,
    - and computing the final/intermediate scoreboard.
    """

    @abstractmethod
    def n_players(self) -> int:
        """Return how many players participate in this game."""
        raise NotImplementedError

    @abstractmethod
    def first_position(self) -> IPosition:
        """Build and return the initial position of a new game."""
        raise NotImplementedError

    @abstractmethod
    def next_position(self, movement: IMovement, position: IPosition) -> IPosition:
        """Compute the position reached after applying a movement.

        Args:
            movement: Movement chosen by the active player.
            position: Current position before the movement is applied.

        Returns:
            The resulting position after the movement.
        """
        raise NotImplementedError

    @abstractmethod
    def possible_movements(self, position: IPosition) -> Iterator[IMovement]:
        """Yield legal movements available from a given position."""
        raise NotImplementedError

    @abstractmethod
    def finished(self, position: IPosition) -> bool:
        """Return `True` when the game is terminal for the given position."""
        raise NotImplementedError

    @abstractmethod
    def score(self, position: IPosition) -> ScoreBoard:
        """Evaluate and return the scoreboard for a given position."""
        raise NotImplementedError

    def current_score(self, position: IPosition) -> ScoreBoard:
        """Return the current scoreboard for a given position.

        Default behavior delegates to `score`. Override when games distinguish
        between final-scoring and intermediate-scoring logic.
        """
        return self.score(position)

    def is_movement_possible(self, movement: IMovement, position: IPosition) -> bool:
        """Check whether a movement is legal in a given position.

        This default implementation delegates to `possible_movements`.
        Override only if a faster membership check is available.
        """
        return movement in self.possible_movements(position)


@runtime_checkable
class IGameGenerator(Protocol):
    """Opt-in capability to create a game/rules object from a dictionary."""

    def build_game(self, values: Mapping[str, Any]) -> IGameRules:
        """Create and return game rules configured by `values`."""
        raise NotImplementedError


@runtime_checkable
class IGameSolver(Protocol):
    """Opt-in capability for solving or bounding game outcomes."""

    def score_bounds(self, rules: IGameRules) -> tuple[ScoreBoard, ScoreBoard]:
        """Return minimum and maximum scoreboards reachable by game rules."""
        raise NotImplementedError
