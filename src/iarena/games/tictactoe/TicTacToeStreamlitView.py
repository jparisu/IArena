"""Streamlit view for TicTacToe."""

from __future__ import annotations

import streamlit as st

from iarena.game.GameMove import GameMove
from iarena.game.GameState import GameState
from iarena.games.tictactoe.TicTacToeMove import TicTacToeMove
from iarena.games.tictactoe.TicTacToeState import PLAYER_O, PLAYER_X, TicTacToeState
from iarena.interface.Interface import Interface
from iarena.view.StreamlitView import StreamlitView

_MOVE_KEY = "ttt_pending_move"

_SYMBOLS: dict[int, str] = {0: "·", PLAYER_X: "X", PLAYER_O: "O"}

# Button styling injected once per page load.
_BOARD_CSS = """
<style>
div[data-testid="column"] button {
    font-size: 2rem;
    font-weight: bold;
    height: 5rem;
}
</style>
"""


class TicTacToeStreamlitView(StreamlitView):
    """Renders a TicTacToe board as a 3x3 grid of Streamlit buttons.

    Empty cells are rendered as clickable buttons.  Clicking one stores
    the chosen move in ``st.session_state`` under a private key, which
    ``pop_pending_move`` retrieves on the next call.

    Occupied cells are displayed as disabled buttons showing X or O.
    """

    def render_state(self, state: GameState, interface: Interface) -> None:
        """Render the 3x3 board grid through Streamlit widgets.

        Empty cells are clickable; occupied and post-game cells are
        disabled.  Clicking an empty cell stores ``"row,col"`` in
        ``st.session_state``.

        Parameters
        ----------
        state:
            Current TicTacToeState to display.
        interface:
            Unused directly; present for interface compliance.
        """
        assert isinstance(state, TicTacToeState)
        st.markdown(_BOARD_CSS, unsafe_allow_html=True)
        game_over = st.session_state.get("game_over", False)

        for row in range(3):
            cols = st.columns(3)
            for col in range(3):
                cell = state.get_cell(row, col)
                label = _SYMBOLS[cell]
                disabled = (cell != 0) or game_over
                if cols[col].button(
                    label,
                    key=f"ttt_{row}_{col}",
                    disabled=disabled,
                    use_container_width=True,
                ):
                    st.session_state[_MOVE_KEY] = f"{row},{col}"

    def pop_pending_move(self) -> GameMove | None:
        """Return and clear the pending move from session state.

        Returns
        -------
        TicTacToeMove | None
            The move from the last button click, or None.
        """
        move_str: str | None = st.session_state.pop(_MOVE_KEY, None)
        if move_str and TicTacToeMove.is_valid_string(move_str):
            return TicTacToeMove.from_string(move_str)
        return None

    def ask(self, interface: Interface) -> GameMove:
        """Return a pending move or halt until the user clicks a cell.

        Parameters
        ----------
        interface:
            Unused; present for interface compliance.

        Returns
        -------
        TicTacToeMove
            The move chosen by the user.
        """
        move = self.pop_pending_move()
        if move is not None:
            return move
        st.stop()
