"""Tests for TicTacToeState."""

import pytest

from iarena.game.GameState import GameState
from iarena.games.tictactoe.TicTacToeState import EMPTY, PLAYER_O, PLAYER_X, TicTacToeState


class TestTicTacToeState:
    # --- Happy path ---

    def test_instantiation_defaults(self) -> None:
        state = TicTacToeState()
        assert isinstance(state, TicTacToeState)

    def test_is_game_state_subclass(self) -> None:
        assert issubclass(TicTacToeState, GameState)

    def test_default_board_is_empty(self) -> None:
        state = TicTacToeState()
        for row in range(3):
            for col in range(3):
                assert state.get_cell(row, col) == EMPTY

    def test_default_current_player_is_zero(self) -> None:
        state = TicTacToeState()
        assert state.current_player_id() == 0

    def test_board_property_returns_3x3(self) -> None:
        state = TicTacToeState()
        board = state.board
        assert len(board) == 3
        assert all(len(row) == 3 for row in board)

    def test_board_property_is_a_copy(self) -> None:
        state = TicTacToeState()
        board1 = state.board
        board2 = state.board
        assert board1 is not board2

    def test_custom_board_and_player(self) -> None:
        board = [[PLAYER_X, EMPTY, EMPTY], [EMPTY, EMPTY, EMPTY], [EMPTY, EMPTY, EMPTY]]
        state = TicTacToeState(board=board, current_player=1)
        assert state.get_cell(0, 0) == PLAYER_X
        assert state.current_player_id() == 1

    def test_get_cell_player_o(self) -> None:
        board = [[EMPTY, EMPTY, EMPTY], [EMPTY, PLAYER_O, EMPTY], [EMPTY, EMPTY, EMPTY]]
        state = TicTacToeState(board=board)
        assert state.get_cell(1, 1) == PLAYER_O

    # --- Corner cases ---

    def test_full_board_get_cell(self) -> None:
        board = [
            [PLAYER_X, PLAYER_O, PLAYER_X],
            [PLAYER_O, PLAYER_X, PLAYER_O],
            [PLAYER_O, PLAYER_X, PLAYER_O],
        ]
        state = TicTacToeState(board=board)
        assert state.get_cell(0, 0) == PLAYER_X
        assert state.get_cell(0, 1) == PLAYER_O
        assert state.get_cell(2, 2) == PLAYER_O

    def test_current_player_one(self) -> None:
        state = TicTacToeState(current_player=1)
        assert state.current_player_id() == 1

    # --- Failure cases ---

    def test_invalid_current_player_raises(self) -> None:
        with pytest.raises(ValueError):
            TicTacToeState(current_player=2)

    def test_invalid_board_dimensions_raises(self) -> None:
        with pytest.raises(ValueError):
            TicTacToeState(board=[[0, 0], [0, 0], [0, 0]])

    def test_invalid_cell_value_raises(self) -> None:
        bad_board = [[9, 0, 0], [0, 0, 0], [0, 0, 0]]
        with pytest.raises(ValueError):
            TicTacToeState(board=bad_board)
