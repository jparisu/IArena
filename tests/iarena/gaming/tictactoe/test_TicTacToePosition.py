"""Tests for the TicTacToe position model."""

from __future__ import annotations

from iarena.gaming.tictactoe.TicTacToePosition import TicTacToePosition
from iarena.gaming.tictactoe.TicTacToeRules import TicTacToeRules
from iarena.playing.PlayerIndex import PlayerIndex


def test_init_stores_position_values() -> None:
    position = TicTacToePosition(
        board_size=3,
        win_length=3,
        cells=[0, None, 1, None, None, None, None, None, None],
        turn=2,
        current_player=PlayerIndex(0),
    )

    assert position.board_size == 3
    assert position.win_length == 3
    assert position.cells[0] == 0
    assert position.cells[2] == 1
    assert position.turn == 2
    assert position.current_player == PlayerIndex(0)


def test_hash_changes_with_position_state() -> None:
    first = TicTacToePosition(board_size=3, win_length=3)
    second = TicTacToePosition(
        board_size=3,
        win_length=3,
        cells=[0, None, None, None, None, None, None, None, None],
        turn=1,
        current_player=PlayerIndex(1),
    )

    assert first.hash() != second.hash()


def test_next_player_returns_current_player_index() -> None:
    position = TicTacToePosition(board_size=3, win_length=3, current_player=PlayerIndex(1))

    assert position.next_player() == PlayerIndex(1)


def test_get_rules_returns_tictactoe_rules() -> None:
    position = TicTacToePosition(board_size=3, win_length=3)

    rules = position.get_rules()

    assert isinstance(rules, TicTacToeRules)
    assert rules.configuration.board_size == 3
    assert rules.configuration.win_length == 3
