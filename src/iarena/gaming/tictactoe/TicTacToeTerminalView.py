"""Declares the terminal visualization contract for the TicTacToe game."""

from __future__ import annotations

from typing import TYPE_CHECKING

from iarena.visualizing.terminal_frontend.TerminalView import TerminalView

if TYPE_CHECKING:
    from iarena.gaming.Movement import Movement
    from iarena.gaming.Position import Position
    from iarena.gaming.Rules import Rules

from iarena.gaming.tictactoe.TicTacToeMovement import TicTacToeMovement
from iarena.gaming.tictactoe.TicTacToePosition import TicTacToePosition
from iarena.gaming.tictactoe.TicTacToeRules import TicTacToeRules


class TicTacToeTerminalView(TerminalView):
    """Concrete terminal view implementation for the TicTacToe game.

    Purpose:
        Provides text-based rendering and input parsing for TicTacToe in terminal executions.
    How it works:
        Converts TicTacToe domain objects into formatted strings and user commands into movements.
    Used for:
        Command-line gameplay and debugging-oriented textual visualization.
    Public Attributes:
        Inherits terminal I/O callables from `TerminalView`.
    """

    def _symbol(self, value: int | None) -> str:
        """Return the terminal symbol used for one board cell value.

        Args:
            value: Cell value (`0`, `1`, or `None`).

        Returns:
            str: One-character terminal symbol.
        """
        if value == 0:
            return "X"
        if value == 1:
            return "O"
        return "."

    def get_str_info(self, rules: Rules) -> str:
        """Return formatted static information for the current TicTacToe match.

        Args:
            rules: Rules instance used to derive user-facing game metadata.

        Returns:
            str: Text block rendered in the terminal information area.
        """
        if not isinstance(rules, TicTacToeRules):
            raise TypeError("rules must be an instance of TicTacToeRules.")

        conf = rules.configuration
        return (
            "=== Tic Tac Toe ===\n"
            f"Board size: {conf.board_size}x{conf.board_size}\n"
            f"Win length: {conf.win_length}\n"
            "Players:\n"
            "  - Player 0: X\n"
            "  - Player 1: O\n"
            "Input format: 'row col' (zero-based), e.g. '1 2'."
        )

    def get_str_state(self, position: Position) -> str:
        """Return formatted text representation of the current TicTacToe position.

        Args:
            position: Position to transform into a terminal-friendly state string.

        Returns:
            str: Text block describing the board state.
        """
        if not isinstance(position, TicTacToePosition):
            raise TypeError("position must be an instance of TicTacToePosition.")

        size = position.board_size
        rows: list[str] = []
        for row in range(size):
            start = row * size
            end = start + size
            row_values = [self._symbol(value) for value in position.cells[start:end]]
            rows.append(f"{row}: " + " | ".join(row_values))

        header = "    " + "   ".join(str(col) for col in range(size))
        separator = "  " + ("----" * size)

        possible_movements = list(position.get_rules().possible_movements(position))
        movement_lines = [f"  [{move_index}] {movement}" for move_index, movement in enumerate(possible_movements)]
        if not movement_lines:
            movement_lines = ["  No legal movements available."]

        current_symbol = "X" if position.current_player == 0 else "O"
        return "\n".join(
            [
                f"Turn: {position.turn}",
                f"Current player: {int(position.current_player)} ({current_symbol})",
                header,
                separator,
                *rows,
                "Possible movements:",
                *movement_lines,
            ],
        )

    def capture_input(self, input: str) -> Movement:
        """Convert a terminal input line into a TicTacToe movement instance.

        Args:
            input: Raw text entered by the terminal user.

        Returns:
            Movement: Parsed movement represented by the input text.
        """
        parts = input.replace(",", " ").split()
        if len(parts) != 2:
            raise ValueError("Expected exactly two integers, e.g. '1 2'.")

        row, col = int(parts[0]), int(parts[1])
        return TicTacToeMovement(row=row, col=col)
