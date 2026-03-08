"""Tests for the TicTacToe movement model."""

from __future__ import annotations

import pytest

from iarena.gaming.tictactoe.TicTacToeMovement import TicTacToeMovement


def test_init_stores_row_and_col() -> None:
    movement = TicTacToeMovement(row=1, col=2)

    assert movement.row == 1
    assert movement.col == 2


def test_init_rejects_negative_coordinates() -> None:
    with pytest.raises(ValueError, match="non-negative"):
        TicTacToeMovement(row=-1, col=0)


def test_str_and_repr_are_user_friendly() -> None:
    movement = TicTacToeMovement(row=1, col=2)

    assert str(movement) == "(1, 2)"
    assert "row=1" in repr(movement)
