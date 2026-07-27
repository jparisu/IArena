"""Tests for TicTacToeMove."""

import pytest

from iarena.game.GameMove import ParseableStringifiableGameMove
from iarena.games.tictactoe.TicTacToeMove import TicTacToeMove


class TestTicTacToeMove:
    # --- Happy path ---

    def test_instantiation(self) -> None:
        move = TicTacToeMove(0, 0)
        assert isinstance(move, TicTacToeMove)

    def test_is_parseable_stringifiable(self) -> None:
        assert issubclass(TicTacToeMove, ParseableStringifiableGameMove)

    def test_row_property(self) -> None:
        assert TicTacToeMove(1, 2).row == 1

    def test_col_property(self) -> None:
        assert TicTacToeMove(1, 2).col == 2

    def test_to_string_format(self) -> None:
        assert TicTacToeMove(0, 0).to_string() == "0,0"
        assert TicTacToeMove(2, 1).to_string() == "2,1"

    def test_str_delegates_to_to_string(self) -> None:
        assert str(TicTacToeMove(1, 0)) == "1,0"

    def test_is_valid_string_valid(self) -> None:
        assert TicTacToeMove.is_valid_string("0,0") is True
        assert TicTacToeMove.is_valid_string("2,2") is True
        assert TicTacToeMove.is_valid_string("1,1") is True

    def test_from_string_roundtrip(self) -> None:
        move = TicTacToeMove.from_string("1,2")
        assert move.row == 1
        assert move.col == 2

    def test_equality(self) -> None:
        assert TicTacToeMove(1, 2) == TicTacToeMove(1, 2)

    def test_inequality(self) -> None:
        assert TicTacToeMove(0, 0) != TicTacToeMove(1, 1)

    def test_hash_consistent_with_equality(self) -> None:
        assert hash(TicTacToeMove(1, 2)) == hash(TicTacToeMove(1, 2))

    # --- Corner cases ---

    def test_all_nine_cells_valid(self) -> None:
        for row in range(3):
            for col in range(3):
                move = TicTacToeMove(row, col)
                assert move.row == row
                assert move.col == col

    def test_from_string_all_valid_cells(self) -> None:
        for row in range(3):
            for col in range(3):
                move = TicTacToeMove.from_string(f"{row},{col}")
                assert move.row == row
                assert move.col == col

    # --- Failure cases ---

    def test_row_out_of_range_raises(self) -> None:
        with pytest.raises(ValueError):
            TicTacToeMove(3, 0)

    def test_col_out_of_range_raises(self) -> None:
        with pytest.raises(ValueError):
            TicTacToeMove(0, 3)

    def test_negative_row_raises(self) -> None:
        with pytest.raises(ValueError):
            TicTacToeMove(-1, 0)

    def test_negative_col_raises(self) -> None:
        with pytest.raises(ValueError):
            TicTacToeMove(0, -1)

    def test_is_valid_string_bad_format(self) -> None:
        assert TicTacToeMove.is_valid_string("abc") is False
        assert TicTacToeMove.is_valid_string("1") is False
        assert TicTacToeMove.is_valid_string("3,0") is False
        assert TicTacToeMove.is_valid_string("0,3") is False
        assert TicTacToeMove.is_valid_string("") is False

    def test_from_string_invalid_raises(self) -> None:
        with pytest.raises(ValueError):
            TicTacToeMove.from_string("abc")

    def test_from_string_out_of_bounds_raises(self) -> None:
        with pytest.raises(ValueError):
            TicTacToeMove.from_string("3,0")
