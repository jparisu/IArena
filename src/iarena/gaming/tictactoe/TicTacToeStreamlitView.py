"""Declares the streamlit visualization contract for the TicTacToe game."""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING

from iarena.visualizing.streamlit_frontend.StreamlitView import StreamlitView

if TYPE_CHECKING:
    from iarena.gaming.Movement import Movement
    from iarena.gaming.Position import Position
    from iarena.gaming.Rules import Rules
    from iarena.visualizing.Canvas import Canvas
    from iarena.visualizing.streamlit_frontend.StreamlitContainer import StreamlitContainer
    from iarena.visualizing.streamlit_frontend.StreamlitSession import StreamlitSession

from iarena.gaming.tictactoe.TicTacToeMovement import TicTacToeMovement
from iarena.gaming.tictactoe.TicTacToePosition import TicTacToePosition
from iarena.gaming.tictactoe.TicTacToeRules import TicTacToeRules


class TicTacToeStreamlitView(StreamlitView):
    """Concrete streamlit view implementation for the TicTacToe game.

    Purpose:
        Provides web UI rendering and interaction bindings for TicTacToe in streamlit apps.
    How it works:
        Maps TicTacToe rules/position data to streamlit widgets and parses user interactions.
    Used for:
        Browser-based TicTacToe gameplay with clickable board controls.
    Public Attributes:
        Inherits common view behavior from `StreamlitView`.
    """

    def _emit_markdown(self, canvas: object, text: str) -> None:
        """Write markdown content to a streamlit-like container when supported.

        Args:
            canvas: Candidate streamlit container object.
            text: Markdown payload to display.

        Returns:
            None.
        """
        markdown = getattr(canvas, "markdown", None)
        if callable(markdown):
            markdown(text)
            return

        writer = getattr(canvas, "write", None)
        if callable(writer):
            writer(text)

    def _cell_symbol(self, value: int | None) -> str:
        """Return display symbol for one board cell value.

        Args:
            value: Cell value (`0`, `1`, or `None`).

        Returns:
            str: Human-readable symbol.
        """
        if value == 0:
            return "X"
        if value == 1:
            return "O"
        return ""

    def _index(self, size: int, row: int, col: int) -> int:
        """Return row-major flat index for one cell coordinate.

        Args:
            size: Board side size.
            row: Zero-based row.
            col: Zero-based column.

        Returns:
            int: Flat list index.
        """
        return (row * size) + col

    def render_info(self, rules: Rules, canvas: Canvas) -> None:
        """Render static TicTacToe information into the streamlit canvas.

        Args:
            rules: Rules object used to compute info text and metadata.
            canvas: Target canvas abstraction where info widgets are rendered.

        Returns:
            None.
        """
        if not isinstance(rules, TicTacToeRules):
            raise TypeError("rules must be an instance of TicTacToeRules.")

        conf = rules.configuration
        info = (
            "### Tic-Tac-Toe\n"
            f"- **Board size:** `{conf.board_size}x{conf.board_size}`\n"
            f"- **Win length:** `{conf.win_length}`\n"
            "- **Players:** `Player 0 = X`, `Player 1 = O`"
        )
        self._emit_markdown(canvas, info)

    def render_position(self, position: Position, canvas: StreamlitContainer) -> None:
        """Render the current TicTacToe board position into the position section.

        Args:
            position: Current game position to display.
            canvas: Streamlit container for the position section.

        Returns:
            None.
        """
        if not isinstance(position, TicTacToePosition):
            raise TypeError("position must be an instance of TicTacToePosition.")

        current_symbol = "X" if int(position.current_player) == 0 else "O"
        self._emit_markdown(
            canvas,
            (f"### Turn `{position.turn}`\nCurrent player: `Player {int(position.current_player)} ({current_symbol})`"),
        )

        import streamlit as st

        native_canvas = canvas.container if canvas.container is not None else st.container()
        size = position.board_size
        with native_canvas:
            for row in range(size):
                cols = st.columns(size)
                for col in range(size):
                    cell_value = position.cells[self._index(size, row, col)]
                    label = self._cell_symbol(cell_value)
                    if label == "":
                        label = "·"
                    cols[col].button(
                        label,
                        key=f"tictactoe_board_cell_{position.turn}_{row}_{col}",
                        disabled=True,
                        use_container_width=True,
                    )

    def render_movements(self, position: Position, canvas: StreamlitContainer) -> None:
        """Render available TicTacToe movements into the movement controls section.

        Args:
            position: Current game position used to derive legal movements.
            canvas: Streamlit container for movement controls.

        Returns:
            None.
        """
        if not isinstance(position, TicTacToePosition):
            raise TypeError("position must be an instance of TicTacToePosition.")

        rules = position.get_rules()
        if not isinstance(rules, TicTacToeRules):
            raise TypeError("Position rules must be an instance of TicTacToeRules.")

        legal_moves = {
            (movement.row, movement.col)
            for movement in rules.possible_movements(position)
            if isinstance(movement, TicTacToeMovement)
        }

        import streamlit as st

        native_canvas = canvas.container if canvas.container is not None else st.container()
        with native_canvas:
            size = position.board_size
            for row in range(size):
                cols = st.columns(size)
                for col in range(size):
                    cell_value = position.cells[self._index(size, row, col)]
                    is_legal = (row, col) in legal_moves and cell_value is None
                    label = self._cell_symbol(cell_value)
                    if label == "":
                        label = f"{row},{col}"
                    clicked = cols[col].button(
                        label,
                        key=f"tictactoe_move_cell_{position.turn}_{row}_{col}",
                        disabled=not is_legal,
                        use_container_width=True,
                    )
                    if clicked:
                        st.session_state["selected_movement"] = TicTacToeMovement(row=row, col=col)

    def render_score(self, position: Position, canvas: StreamlitContainer) -> None:
        """Render current TicTacToe score information into the score section.

        Args:
            position: Current game position used to compute score data.
            canvas: Streamlit container for score output.

        Returns:
            None.
        """
        if not isinstance(position, TicTacToePosition):
            raise TypeError("position must be an instance of TicTacToePosition.")

        rules = position.get_rules()
        if not isinstance(rules, TicTacToeRules):
            raise TypeError("Position rules must be an instance of TicTacToeRules.")

        scoreboard = rules.get_score(position)
        p0 = float(scoreboard.get_score(0))
        p1 = float(scoreboard.get_score(1))
        status = "Finished" if rules.is_finished(position) else "In progress"

        self._emit_markdown(
            canvas,
            (
                "### Position Score\n"
                f"- **Status:** `{status}`\n"
                f"- **Player 0 (X):** `{p0:.1f}`\n"
                f"- **Player 1 (O):** `{p1:.1f}`"
            ),
        )

    def capture_input(self, state: StreamlitSession) -> Movement:
        """Capture streamlit session interaction state and return one movement.

        Args:
            state: Streamlit session state containing latest user interaction values.

        Returns:
            Movement: Movement extracted from current streamlit UI state.
        """
        row: int | None = None
        col: int | None = None

        if isinstance(state, Mapping):
            raw_row = state.get("tictactoe_row")
            raw_col = state.get("tictactoe_col")
            if raw_row is not None and raw_col is not None:
                row = int(raw_row)
                col = int(raw_col)
        else:
            raw_row = getattr(state, "tictactoe_row", None)
            raw_col = getattr(state, "tictactoe_col", None)
            if raw_row is not None and raw_col is not None:
                row = int(raw_row)
                col = int(raw_col)

        if row is None or col is None:
            raise ValueError("state must contain integer-like 'tictactoe_row' and 'tictactoe_col' values.")

        return TicTacToeMovement(row=row, col=col)
