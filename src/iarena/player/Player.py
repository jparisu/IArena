"""Abstract base class for game players."""

from abc import ABC, abstractmethod

from iarena.game.GameMove import GameMove
from iarena.game.GameState import GameState


class Player(ABC):
    """Contract for any participant in a game session.

    A player receives the current game state and must return a move.
    Concrete subclasses decide how that move is chosen — by asking a
    human, running an algorithm, or querying a remote service.
    """

    @abstractmethod
    def choose_move(self, state: GameState) -> GameMove:
        """Select and return a move for the current game state.

        Parameters
        ----------
        state:
            The current game state.  The active player is
            state.current_player_id().

        Returns
        -------
        GameMove
            The move chosen by this player.
        """
