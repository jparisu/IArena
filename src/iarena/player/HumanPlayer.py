"""Human player that delegates move selection to a View and Interface."""

from iarena.game.GameMove import GameMove
from iarena.game.GameState import GameState
from iarena.interface.Interface import Interface
from iarena.player.Player import Player
from iarena.view.View import View


class HumanPlayer(Player):
    """Player driven by a human via a View and Interface pair.

    The View is responsible for prompting and parsing input; the
    Interface provides the I/O medium.  The same HumanPlayer can be
    reused across turns — it holds no mutable state between calls.

    Parameters
    ----------
    view:
        Game-specific view that renders prompts and parses raw input.
    interface:
        Medium through which output is shown and input is read.
    """

    def __init__(self, view: View, interface: Interface) -> None:
        self._view = view
        self._interface = interface

    def choose_move(self, state: GameState) -> GameMove:
        """Ask the human for a move via the view and return it.

        Parameters
        ----------
        state:
            The current game state shown to the human.

        Returns
        -------
        GameMove
            The move parsed from the human's raw input.
        """
        return self._view.ask(self._interface)
