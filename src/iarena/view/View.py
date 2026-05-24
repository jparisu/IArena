"""Abstract base class for game views."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from iarena.game.GameMove import GameMove
from iarena.game.GameState import GameState

if TYPE_CHECKING:
    from iarena.interface.Interface import Interface


class View(ABC):
    """Game- and interface-aware rendering and move-input contract.

    A View is specialised for one (game × interface) combination.
    It knows how to represent a game state as output for a specific
    medium, and how to turn raw user input into a GameMove.

    The Interface is passed at call time, not held as an attribute,
    so the same View instance can be reused across different sessions.
    """

    @abstractmethod
    def render_state(self, state: GameState, interface: Interface) -> None:
        """Render the current game state through the given interface.

        Parameters
        ----------
        state:
            The game state to display.
        interface:
            The medium through which output is emitted (calls interface.render).
        """

    @abstractmethod
    def ask(self, interface: Interface) -> GameMove:
        """Wait for the user to enter a move and return it as a GameMove.

        Uses interface.ask to obtain raw input, then parses it into a move.

        Parameters
        ----------
        interface:
            The medium through which the prompt is shown and input is read.

        Returns
        -------
        GameMove
            The move parsed from the user's raw input.

        Raises
        ------
        ValueError
            If the raw input cannot be parsed into a valid GameMove.
        """
