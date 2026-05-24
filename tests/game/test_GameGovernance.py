"""Tests for iarena.game.GameGovernance."""

from typing import Any

import pytest

from iarena.game.GameConfig import GameConfig
from iarena.game.GameGovernance import GameGovernance
from iarena.game.GameMove import GameMove
from iarena.game.GameRules import GameRules
from iarena.game.GameState import GameState


class _ConcreteConfig(GameConfig):
    pass


class _ConcreteState(GameState):
    def current_player_id(self) -> int:
        return 0


class _ConcreteRules(GameRules):
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


class _ConcreteGovernance(GameGovernance):
    def create_rules(self, config: GameConfig) -> GameRules:
        return _ConcreteRules()

    def supported_configs(self) -> list[type[GameConfig]]:
        return [_ConcreteConfig]


class TestGameGovernance:
    def test_cannot_instantiate_abstract_class(self) -> None:
        with pytest.raises(TypeError):
            GameGovernance()  # type: ignore[abstract]

    def test_concrete_subclass_is_instantiable(self) -> None:
        assert isinstance(_ConcreteGovernance(), GameGovernance)

    def test_supported_configs_returns_list(self) -> None:
        assert isinstance(_ConcreteGovernance().supported_configs(), list)

    def test_supported_configs_contains_game_config_types(self) -> None:
        for entry in _ConcreteGovernance().supported_configs():
            assert isinstance(entry, type)
            assert issubclass(entry, GameConfig)

    def test_create_rules_returns_game_rules(self) -> None:
        gov = _ConcreteGovernance()
        assert isinstance(gov.create_rules(_ConcreteConfig()), GameRules)
