"""ASCII terminal view for TicTacToe."""

from iarena.game.GameMove import GameMove
from iarena.game.GameState import GameState
from iarena.games.tictactoe.TicTacToeMove import TicTacToeMove
from iarena.games.tictactoe.TicTacToeState import PLAYER_O, PLAYER_X, TicTacToeState
from iarena.interface.Interface import Interface
from iarena.view.View import View


class TicTacToeASCIIView(View):
    """Renders TicTacToe state as ASCII art and parses move input.

    The board is displayed as a 3x3 grid with rows and columns labelled
    0–2.  The user enters a move as ``"row,col"`` (e.g. ``"1,2"``).

    Example output::

        TicTacToe Board:
         X | O | .
        -----------
         . | X | .
        -----------
         . | . | O

    """

    # Cell display symbols
    _SYMBOLS: dict[int, str] = {0: ".", PLAYER_X: "X", PLAYER_O: "O"}

    def render_state(self, state: GameState, interface: Interface) -> None:
        """Render the board and whose turn it is through interface.

        Parameters
        ----------
        state:
            Current TicTacToeState.
        interface:
            Medium for output.
        """
        assert isinstance(state, TicTacToeState)
        interface.render("TicTacToe Board:")
        separator = "-----------"
        for row_idx in range(3):
            cells = [self._SYMBOLS[state.get_cell(row_idx, col)] for col in range(3)]
            interface.render(" " + " | ".join(cells))
            if row_idx < 2:
                interface.render(separator)
        player_name = "X" if state.current_player_id() == 0 else "O"
        interface.render(f"Player {player_name}'s turn.")

    def ask(self, interface: Interface) -> GameMove:
        """Prompt the user for a move and return a TicTacToeMove.

        Prompts with ``"Enter move as row,col (e.g. 1,2): "`` and
        parses the response into a TicTacToeMove.

        Parameters
        ----------
        interface:
            Medium for I/O.

        Returns
        -------
        TicTacToeMove
            The parsed move.

        Raises
        ------
        ValueError
            If the raw input is not a valid move string.
        """
        raw = interface.ask("Enter move as row,col (e.g. 1,2): ")
        return TicTacToeMove.from_string(raw)
