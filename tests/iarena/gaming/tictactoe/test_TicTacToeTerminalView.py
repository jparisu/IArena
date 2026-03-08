"""Tests for the TicTacToe terminal view textual rendering behavior."""

from __future__ import annotations

from iarena.gaming.tictactoe.TicTacToeConfiguration import TicTacToeConfiguration
from iarena.gaming.tictactoe.TicTacToeMovement import TicTacToeMovement
from iarena.gaming.tictactoe.TicTacToeRules import TicTacToeRules
from iarena.gaming.tictactoe.TicTacToeTerminalView import TicTacToeTerminalView


def test_get_str_info_includes_instructions_and_dimensions() -> None:
    rules = TicTacToeRules(TicTacToeConfiguration(board_size=3, win_length=3))
    view = TicTacToeTerminalView()

    text = view.get_str_info(rules)

    assert "Tic Tac Toe" in text
    assert "Board size" in text
    assert "Win length" in text
    assert "Input format" in text


def test_get_str_state_includes_board_and_possible_movements() -> None:
    rules = TicTacToeRules(TicTacToeConfiguration(board_size=3, win_length=3))
    position = rules.first_position()
    view = TicTacToeTerminalView()

    text = view.get_str_state(position)

    assert "Current player" in text
    assert "Possible movements:" in text
    assert "." in text
    assert "[0]" in text


def test_capture_input_parses_row_and_column() -> None:
    view = TicTacToeTerminalView()

    movement = view.capture_input("1,2")

    assert isinstance(movement, TicTacToeMovement)
    assert movement.row == 1
    assert movement.col == 2
