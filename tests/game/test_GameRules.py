"""Tests for iarena.game.GameRules and FullGameRules."""

from collections.abc import Iterator
from typing import Any

import pytest

from iarena.game.GameMove import GameMove
from iarena.game.GameRules import FullGameRules, GameRules
from iarena.game.GameState import GameState


class _ConcreteMove(GameMove):
    pass


class _ConcreteState(GameState):
    def current_player_id(self) -> int:
        return 0


class _ConcreteGameRules(GameRules):
    def number_of_players(self) -> int:
        return 2

    def first_position(self) -> GameState:
        return _ConcreteState()

    def apply_move(self, state: GameState, move: GameMove) -> GameState:
        return state

    def is_terminal(self, state: GameState) -> bool:
        return False

    def result(self, state: GameState) -> Any:
        return None

    def is_legal(self, state: GameState, move: GameMove) -> bool:
        return True


class _ConcreteFullGameRules(FullGameRules):
    def number_of_players(self) -> int:
        return 2

    def first_position(self) -> GameState:
        return _ConcreteState()

    def apply_move(self, state: GameState, move: GameMove) -> GameState:
        return state

    def is_terminal(self, state: GameState) -> bool:
        return False

    def result(self, state: GameState) -> Any:
        return None

    def legal_moves(self, state: GameState) -> Iterator[GameMove]:
        return iter([_ConcreteMove()])

    def is_legal(self, state: GameState, move: GameMove) -> bool:
        return True


class TestGameRules:
    def test_cannot_instantiate_abstract_class(self) -> None:
        with pytest.raises(TypeError):
            GameRules()  # type: ignore[abstract]

    def test_number_of_players_returns_int(self) -> None:
        assert isinstance(_ConcreteGameRules().number_of_players(), int)

    def test_number_of_players_is_positive(self) -> None:
        assert _ConcreteGameRules().number_of_players() >= 1

    def test_first_position_returns_game_state(self) -> None:
        assert isinstance(_ConcreteGameRules().first_position(), GameState)

    def test_apply_move_returns_game_state(self) -> None:
        rules = _ConcreteGameRules()
        state = rules.first_position()
        assert isinstance(rules.apply_move(state, _ConcreteMove()), GameState)

    def test_is_terminal_returns_bool(self) -> None:
        rules = _ConcreteGameRules()
        assert isinstance(rules.is_terminal(rules.first_position()), bool)

    def test_result_is_callable(self) -> None:
        rules = _ConcreteGameRules()
        rules.result(rules.first_position())  # must not raise


class TestFullGameRules:
    def test_cannot_instantiate_abstract_class(self) -> None:
        with pytest.raises(TypeError):
            FullGameRules()  # type: ignore[abstract]

    def test_is_subclass_of_game_rules(self) -> None:
        assert issubclass(FullGameRules, GameRules)

    def test_legal_moves_yields_game_moves(self) -> None:
        rules = _ConcreteFullGameRules()
        for move in rules.legal_moves(rules.first_position()):
            assert isinstance(move, GameMove)

    def test_is_legal_returns_bool(self) -> None:
        rules = _ConcreteFullGameRules()
        assert isinstance(rules.is_legal(rules.first_position(), _ConcreteMove()), bool)
