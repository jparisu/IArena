"""Tests for iarena.player.Player."""

import pytest

from iarena.game.GameMove import GameMove
from iarena.game.GameState import GameState
from iarena.player.Player import Player


class _ConcreteState(GameState):
    def current_player_id(self) -> int:
        return 0


class _ConcreteMove(GameMove):
    pass


class _ConcretePlayer(Player):
    def choose_move(self, state: GameState) -> GameMove:
        return _ConcreteMove()


class TestPlayer:
    def test_cannot_instantiate_abstract_class(self) -> None:
        with pytest.raises(TypeError):
            Player()  # type: ignore[abstract]

    def test_choose_move_returns_game_move(self) -> None:
        move = _ConcretePlayer().choose_move(_ConcreteState())
        assert isinstance(move, GameMove)
