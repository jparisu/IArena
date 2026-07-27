"""Abstract base class for game interfaces."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from iarena.game.GameMove import GameMove
from iarena.game.GameState import GameState
from iarena.view.View import View

if TYPE_CHECKING:
    from iarena.player.Player import Player


class Interface(ABC):
    """Contract for the medium through which a game session is played.

    An Interface handles all I/O for a session: low-level output and
    input primitives, plus lifecycle hooks called by the engine at key
    moments in the game loop.

    The optional view is used by the default hook implementations to
    render the game state.  Pass None for interfaces that serve only
    automatic players and need no rendering.

    Parameters
    ----------
    view:
        Game-specific view used by on_turn_start to render state.
        May be None when no rendering is needed.
    """

    def __init__(self, view: View | None = None) -> None:
        self._view = view

    # ------------------------------------------------------------------
    # Low-level I/O — abstract, medium-specific
    # ------------------------------------------------------------------

    @abstractmethod
    def render(self, content: str) -> None:
        """Emit content to the output medium.

        Parameters
        ----------
        content:
            The string to display (terminal line, HTML fragment, widget, …).
        """

    @abstractmethod
    def ask(self, prompt: str) -> str:
        """Display prompt and return the raw string entered by the user.

        Parameters
        ----------
        prompt:
            The message shown to the user before waiting for input.

        Returns
        -------
        str
            The raw input string provided by the user.

        Raises
        ------
        NotImplementedError
            On interfaces that do not support interactive input.
        """

    # ------------------------------------------------------------------
    # Lifecycle hooks — concrete defaults, overridable
    # ------------------------------------------------------------------

    def on_game_start(self, state: GameState) -> None:
        """Called by the engine once before the first turn.

        Parameters
        ----------
        state:
            The initial game state.
        """

    def on_turn_start(self, state: GameState, player: Player) -> None:
        """Called by the engine at the beginning of each turn.

        Delegates to view.render_state when a view is configured.

        Parameters
        ----------
        state:
            The game state at the start of the turn.
        player:
            The player who must move.
        """
        if self._view is not None:
            self._view.render_state(state, self)

    def on_invalid_move(self, state: GameState, player: Player, move: GameMove) -> None:
        """Called by the engine when a player submits an illegal move.

        Parameters
        ----------
        state:
            The current game state (unchanged).
        player:
            The player who submitted the invalid move.
        move:
            The move that was rejected.
        """

    def on_turn_end(self, state: GameState, player: Player, move: GameMove) -> None:
        """Called by the engine after a legal move has been applied.

        Parameters
        ----------
        state:
            The game state after the move.
        player:
            The player who made the move.
        move:
            The move that was applied.
        """

    def on_game_end(self, state: GameState, result: Any) -> None:
        """Called by the engine when the game reaches a terminal state.

        Parameters
        ----------
        state:
            The terminal game state.
        result:
            The game result as returned by GameRules.result.
        """
