"""Tests for TicTacToeRules."""

import pytest

from iarena.game.GameRules import FullGameRules
from iarena.game.GameState import GameState
from iarena.games.tictactoe.TicTacToeConfig import TicTacToeConfig
from iarena.games.tictactoe.TicTacToeMove import TicTacToeMove
from iarena.games.tictactoe.TicTacToeRules import TicTacToeRules
from iarena.games.tictactoe.TicTacToeState import EMPTY, PLAYER_O, PLAYER_X, TicTacToeState


@pytest.fixture()
def rules() -> TicTacToeRules:
    return TicTacToeRules(TicTacToeConfig())


class TestTicTacToeRulesInit:
    def test_is_full_game_rules_subclass(self) -> None:
        assert issubclass(TicTacToeRules, FullGameRules)

    def test_wrong_config_type_raises(self) -> None:
        class _BadConfig:
            pass

        with pytest.raises(TypeError):
            TicTacToeRules(_BadConfig())  # type: ignore[arg-type]


class TestTicTacToeRulesBasics:
    def test_number_of_players(self, rules: TicTacToeRules) -> None:
        assert rules.number_of_players() == 2

    def test_first_position_is_tictactoe_state(self, rules: TicTacToeRules) -> None:
        state = rules.first_position()
        assert isinstance(state, TicTacToeState)

    def test_first_position_board_is_empty(self, rules: TicTacToeRules) -> None:
        state = rules.first_position()
        for row in range(3):
            for col in range(3):
                assert state.get_cell(row, col) == EMPTY

    def test_first_position_player_is_zero(self, rules: TicTacToeRules) -> None:
        assert rules.first_position().current_player_id() == 0


class TestTicTacToeRulesApplyMove:
    def test_apply_move_marks_cell(self, rules: TicTacToeRules) -> None:
        state = rules.first_position()
        new_state = rules.apply_move(state, TicTacToeMove(0, 0))
        assert new_state.get_cell(0, 0) == PLAYER_X

    def test_apply_move_advances_player(self, rules: TicTacToeRules) -> None:
        state = rules.first_position()
        new_state = rules.apply_move(state, TicTacToeMove(0, 0))
        assert new_state.current_player_id() == 1

    def test_apply_move_second_player_marks_o(self, rules: TicTacToeRules) -> None:
        state = rules.first_position()
        state = rules.apply_move(state, TicTacToeMove(0, 0))
        state = rules.apply_move(state, TicTacToeMove(1, 1))
        assert state.get_cell(1, 1) == PLAYER_O

    def test_apply_move_does_not_mutate_original(self, rules: TicTacToeRules) -> None:
        state = rules.first_position()
        _ = rules.apply_move(state, TicTacToeMove(0, 0))
        assert state.get_cell(0, 0) == EMPTY

    def test_apply_move_returns_game_state(self, rules: TicTacToeRules) -> None:
        state = rules.first_position()
        result = rules.apply_move(state, TicTacToeMove(0, 0))
        assert isinstance(result, GameState)


class TestTicTacToeRulesIsLegal:
    def test_empty_cell_is_legal(self, rules: TicTacToeRules) -> None:
        state = rules.first_position()
        assert rules.is_legal(state, TicTacToeMove(0, 0)) is True

    def test_occupied_cell_is_illegal(self, rules: TicTacToeRules) -> None:
        state = rules.first_position()
        state = rules.apply_move(state, TicTacToeMove(0, 0))
        assert rules.is_legal(state, TicTacToeMove(0, 0)) is False

    def test_all_empty_cells_legal_on_start(self, rules: TicTacToeRules) -> None:
        state = rules.first_position()
        for row in range(3):
            for col in range(3):
                assert rules.is_legal(state, TicTacToeMove(row, col)) is True


class TestTicTacToeRulesIsTerminal:
    def test_empty_board_not_terminal(self, rules: TicTacToeRules) -> None:
        assert rules.is_terminal(rules.first_position()) is False

    def test_row_win_is_terminal(self, rules: TicTacToeRules) -> None:
        board = [
            [PLAYER_X, PLAYER_X, PLAYER_X],
            [PLAYER_O, PLAYER_O, EMPTY],
            [EMPTY, EMPTY, EMPTY],
        ]
        assert rules.is_terminal(TicTacToeState(board=board)) is True

    def test_col_win_is_terminal(self, rules: TicTacToeRules) -> None:
        board = [
            [PLAYER_O, EMPTY, EMPTY],
            [PLAYER_O, PLAYER_X, EMPTY],
            [PLAYER_O, PLAYER_X, EMPTY],
        ]
        assert rules.is_terminal(TicTacToeState(board=board)) is True

    def test_diagonal_win_is_terminal(self, rules: TicTacToeRules) -> None:
        board = [
            [PLAYER_X, PLAYER_O, EMPTY],
            [PLAYER_O, PLAYER_X, EMPTY],
            [EMPTY, EMPTY, PLAYER_X],
        ]
        assert rules.is_terminal(TicTacToeState(board=board)) is True

    def test_antidiagonal_win_is_terminal(self, rules: TicTacToeRules) -> None:
        board = [
            [EMPTY, PLAYER_O, PLAYER_X],
            [EMPTY, PLAYER_X, EMPTY],
            [PLAYER_X, EMPTY, PLAYER_O],
        ]
        assert rules.is_terminal(TicTacToeState(board=board)) is True

    def test_full_board_draw_is_terminal(self, rules: TicTacToeRules) -> None:
        # No winner, board full
        board = [
            [PLAYER_X, PLAYER_O, PLAYER_X],
            [PLAYER_X, PLAYER_O, PLAYER_O],
            [PLAYER_O, PLAYER_X, PLAYER_X],
        ]
        assert rules.is_terminal(TicTacToeState(board=board)) is True

    def test_in_progress_board_not_terminal(self, rules: TicTacToeRules) -> None:
        board = [
            [PLAYER_X, EMPTY, EMPTY],
            [EMPTY, PLAYER_O, EMPTY],
            [EMPTY, EMPTY, EMPTY],
        ]
        assert rules.is_terminal(TicTacToeState(board=board)) is False


class TestTicTacToeRulesResult:
    def test_result_player_x_wins_row(self, rules: TicTacToeRules) -> None:
        board = [
            [PLAYER_X, PLAYER_X, PLAYER_X],
            [PLAYER_O, PLAYER_O, EMPTY],
            [EMPTY, EMPTY, EMPTY],
        ]
        assert rules.result(TicTacToeState(board=board)) == 0

    def test_result_player_o_wins_col(self, rules: TicTacToeRules) -> None:
        board = [
            [PLAYER_O, PLAYER_X, EMPTY],
            [PLAYER_O, PLAYER_X, EMPTY],
            [PLAYER_O, EMPTY, EMPTY],
        ]
        assert rules.result(TicTacToeState(board=board)) == 1

    def test_result_draw_is_none(self, rules: TicTacToeRules) -> None:
        board = [
            [PLAYER_X, PLAYER_O, PLAYER_X],
            [PLAYER_X, PLAYER_O, PLAYER_O],
            [PLAYER_O, PLAYER_X, PLAYER_X],
        ]
        assert rules.result(TicTacToeState(board=board)) is None

    def test_result_diagonal_win(self, rules: TicTacToeRules) -> None:
        board = [
            [PLAYER_X, PLAYER_O, EMPTY],
            [PLAYER_O, PLAYER_X, EMPTY],
            [EMPTY, EMPTY, PLAYER_X],
        ]
        assert rules.result(TicTacToeState(board=board)) == 0


class TestTicTacToeRulesLegalMoves:
    def test_legal_moves_count_on_empty_board(self, rules: TicTacToeRules) -> None:
        moves = list(rules.legal_moves(rules.first_position()))
        assert len(moves) == 9

    def test_legal_moves_are_tictactoe_moves(self, rules: TicTacToeRules) -> None:
        for move in rules.legal_moves(rules.first_position()):
            assert isinstance(move, TicTacToeMove)

    def test_legal_moves_count_after_one_move(self, rules: TicTacToeRules) -> None:
        state = rules.apply_move(rules.first_position(), TicTacToeMove(0, 0))
        moves = list(rules.legal_moves(state))
        assert len(moves) == 8

    def test_legal_moves_empty_when_terminal(self, rules: TicTacToeRules) -> None:
        board = [
            [PLAYER_X, PLAYER_X, PLAYER_X],
            [PLAYER_O, PLAYER_O, EMPTY],
            [EMPTY, EMPTY, EMPTY],
        ]
        moves = list(rules.legal_moves(TicTacToeState(board=board)))
        assert len(moves) == 0


class TestTicTacToeFullGame:
    def test_engine_runs_x_wins(self, rules: TicTacToeRules) -> None:
        """X wins by filling the top row."""
        state = rules.first_position()
        # X: 0,0  O: 1,0  X: 0,1  O: 1,1  X: 0,2
        for move in [
            TicTacToeMove(0, 0),
            TicTacToeMove(1, 0),
            TicTacToeMove(0, 1),
            TicTacToeMove(1, 1),
            TicTacToeMove(0, 2),
        ]:
            assert not rules.is_terminal(state)
            state = rules.apply_move(state, move)
        assert rules.is_terminal(state)
        assert rules.result(state) == 0

    def test_engine_runs_draw(self, rules: TicTacToeRules) -> None:
        """Full board with no winner.

        Final board::

            X | O | X
            O | X | X
            O | X | O
        """
        state = rules.first_position()
        # Sequence producing a known draw
        # X(0,0) O(0,1) X(1,1) O(1,0) X(0,2) O(2,0) X(1,2) O(2,2) X(2,1)
        moves = [
            TicTacToeMove(0, 0),
            TicTacToeMove(0, 1),
            TicTacToeMove(1, 1),
            TicTacToeMove(1, 0),
            TicTacToeMove(0, 2),
            TicTacToeMove(2, 0),
            TicTacToeMove(1, 2),
            TicTacToeMove(2, 2),
            TicTacToeMove(2, 1),
        ]
        for move in moves:
            state = rules.apply_move(state, move)
        assert rules.is_terminal(state)
        assert rules.result(state) is None
