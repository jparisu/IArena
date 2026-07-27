"""Abstract base classes for game rules."""

from abc import ABC, abstractmethod
from collections.abc import Iterator
from typing import Any

from iarena.game.GameMove import GameMove
from iarena.game.GameState import GameState


class GameRules(ABC):
    """Minimal abstract contract for the rules of a turn-based game.

    Defines the essential operations the engine needs to run the game
    loop: computing initial position, applying moves, detecting
    termination, and calculating results.

    The rules must not depend on any concrete user interface.
    """

    @abstractmethod
    def number_of_players(self) -> int:
        """Return the total number of players in the game.

        Returns
        -------
        int
            Number of players (>= 1).
        """

    @abstractmethod
    def first_position(self) -> GameState:
        """Return the initial game state for a new game.

        Returns
        -------
        GameState
            The starting position constructed from the game configuration.
        """

    @abstractmethod
    def apply_move(self, state: GameState, move: GameMove) -> GameState:
        """Apply move to state and return the resulting game state.

        Parameters
        ----------
        state:
            The current game position.
        move:
            The action selected by the active player.

        Returns
        -------
        GameState
            The new game state after the move has been applied.
        """

    @abstractmethod
    def is_terminal(self, state: GameState) -> bool:
        """Return True if state is a terminal (end-of-game) position.

        Parameters
        ----------
        state:
            The game state to evaluate.

        Returns
        -------
        bool
            True when the game is over; False otherwise.
        """

    @abstractmethod
    def result(self, state: GameState) -> Any:
        """Return the outcome of the game for a terminal state.

        The exact type of the return value is game-specific (e.g. a
        winner identifier, a score mapping, or a float reward vector).

        Parameters
        ----------
        state:
            A terminal game state.

        Returns
        -------
        Any
            The game result in whatever representation the concrete
            game defines.
        """

    @abstractmethod
    def is_legal(self, state: GameState, move: GameMove) -> bool:
        """Return True if move is legal in state.

        Parameters
        ----------
        state:
            The current game position.
        move:
            The candidate move to validate.

        Returns
        -------
        bool
            True if the move is legal; False otherwise.
        """


class FullGameRules(GameRules):
    """Extended game-rules contract that also exposes legal-move enumeration.

    Builds on GameRules by requiring implementations to provide both a
    generator over legal moves and a single-move legality check. These
    additional methods enable human interfaces, move validators, and
    search algorithms that must enumerate or test individual actions.
    """

    @abstractmethod
    def legal_moves(self, state: GameState) -> Iterator[GameMove]:
        """Yield every legal move available in state.

        Parameters
        ----------
        state:
            The current game position.

        Yields
        ------
        GameMove
            Each move that is legal for the active player in state.
        """
