"""Tests for iarena.game.GameState."""

import pytest

from iarena.game.GameState import GameState


class _ConcreteGameState(GameState):
    def current_player_id(self) -> int:
        return 0


class TestGameState:
    def test_cannot_instantiate_abstract_class(self) -> None:
        with pytest.raises(TypeError):
            GameState()  # type: ignore[abstract]

    def test_concrete_subclass_is_instantiable(self) -> None:
        state = _ConcreteGameState()
        assert isinstance(state, GameState)

    def test_current_player_id_returns_int(self) -> None:
        state = _ConcreteGameState()
        assert isinstance(state.current_player_id(), int)

    def test_current_player_id_is_non_negative(self) -> None:
        state = _ConcreteGameState()
        assert state.current_player_id() >= 0
