"""Tests for the TicTacToe configuration model."""

from __future__ import annotations

import pytest

from iarena.gaming.tictactoe.TicTacToeConfiguration import TicTacToeConfiguration


def test_init_stores_configuration_values() -> None:
    configuration = TicTacToeConfiguration(board_size=4, win_length=3)

    assert configuration.board_size == 4
    assert configuration.win_length == 3


def test_init_rejects_invalid_board_size() -> None:
    with pytest.raises(ValueError, match="at least 1"):
        TicTacToeConfiguration(board_size=0, win_length=1)


def test_init_rejects_invalid_win_length() -> None:
    with pytest.raises(ValueError, match="at least 1"):
        TicTacToeConfiguration(board_size=3, win_length=0)


def test_init_rejects_win_length_above_board_size() -> None:
    with pytest.raises(ValueError, match="less than or equal to board_size"):
        TicTacToeConfiguration(board_size=3, win_length=4)


def test_from_dict_uses_defaults_when_values_are_missing() -> None:
    configuration = TicTacToeConfiguration.from_dict({})

    assert configuration.board_size == 3
    assert configuration.win_length == 3
