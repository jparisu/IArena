"""Tests for the TicTacToe rules implementation."""

from __future__ import annotations

import pytest

from iarena.gaming.tictactoe.TicTacToeConfiguration import TicTacToeConfiguration
from iarena.gaming.tictactoe.TicTacToeMovement import TicTacToeMovement
from iarena.gaming.tictactoe.TicTacToePosition import TicTacToePosition
from iarena.gaming.tictactoe.TicTacToeRules import TicTacToeRules
from iarena.playing.PlayerIndex import PlayerIndex


def _rules() -> TicTacToeRules:
    return TicTacToeRules(TicTacToeConfiguration(board_size=3, win_length=3))


def test_init_stores_configuration() -> None:
    configuration = TicTacToeConfiguration(board_size=4, win_length=3)

    rules = TicTacToeRules(configuration)

    assert rules.configuration is configuration


def test_n_players_returns_two() -> None:
    assert _rules().n_players() == 2


def test_first_position_uses_configuration_defaults() -> None:
    position = _rules().first_position()

    assert isinstance(position, TicTacToePosition)
    assert position.board_size == 3
    assert position.win_length == 3
    assert position.turn == 0
    assert position.current_player == PlayerIndex(0)
    assert all(cell is None for cell in position.cells)


def test_next_position_applies_legal_move_and_switches_player() -> None:
    rules = _rules()
    position = rules.first_position()

    next_position = rules.next_position(position, TicTacToeMovement(row=1, col=1))

    assert next_position.cells[4] == 0
    assert next_position.turn == 1
    assert next_position.current_player == PlayerIndex(1)


def test_next_position_rejects_playing_on_occupied_cell() -> None:
    rules = _rules()
    position = TicTacToePosition(
        board_size=3,
        win_length=3,
        cells=[0, None, None, None, None, None, None, None, None],
        turn=1,
        current_player=PlayerIndex(1),
    )

    with pytest.raises(ValueError, match="occupied"):
        rules.next_position(position, TicTacToeMovement(row=0, col=0))


def test_possible_movements_yields_empty_cells_only() -> None:
    rules = _rules()
    position = TicTacToePosition(
        board_size=3,
        win_length=3,
        cells=[0, 1, 0, 1, None, None, None, None, None],
        turn=4,
        current_player=PlayerIndex(0),
    )

    movements = list(rules.possible_movements(position))

    assert {(m.row, m.col) for m in movements} == {(1, 1), (1, 2), (2, 0), (2, 1), (2, 2)}


def test_is_finished_detects_winner_and_draw() -> None:
    rules = _rules()

    winning = TicTacToePosition(
        board_size=3,
        win_length=3,
        cells=[0, 0, 0, 1, 1, None, None, None, None],
        turn=5,
        current_player=PlayerIndex(1),
    )
    draw = TicTacToePosition(
        board_size=3,
        win_length=3,
        cells=[0, 1, 0, 0, 1, 1, 1, 0, 0],
        turn=9,
        current_player=PlayerIndex(1),
    )
    unfinished = rules.first_position()

    assert rules.is_finished(winning) is True
    assert rules.is_finished(draw) is True
    assert rules.is_finished(unfinished) is False


def test_get_score_returns_expected_scores_for_win_draw_and_ongoing() -> None:
    rules = _rules()

    winning = TicTacToePosition(
        board_size=3,
        win_length=3,
        cells=[0, 0, 0, 1, 1, None, None, None, None],
        turn=5,
        current_player=PlayerIndex(1),
    )
    draw = TicTacToePosition(
        board_size=3,
        win_length=3,
        cells=[0, 1, 0, 0, 1, 1, 1, 0, 0],
        turn=9,
        current_player=PlayerIndex(1),
    )
    ongoing = rules.first_position()

    winning_scores = rules.get_score(winning)
    draw_scores = rules.get_score(draw)
    ongoing_scores = rules.get_score(ongoing)

    assert float(winning_scores._scores[PlayerIndex(0)]) == 1.0
    assert float(winning_scores._scores[PlayerIndex(1)]) == -1.0
    assert float(draw_scores._scores[PlayerIndex(0)]) == 0.0
    assert float(draw_scores._scores[PlayerIndex(1)]) == 0.0
    assert float(ongoing_scores._scores[PlayerIndex(0)]) == 0.0
    assert float(ongoing_scores._scores[PlayerIndex(1)]) == 0.0
