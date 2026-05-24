"""Tests for iarena.player.AutomaticPlayer."""

import pytest

from iarena.game.GameMove import GameMove
from iarena.game.GameState import GameState
from iarena.player.AutomaticPlayer import AutomaticPlayer
from iarena.player.Player import Player


class _ConcreteState(GameState):
    def current_player_id(self) -> int:
        return 0


class _ConcreteMove(GameMove):
    pass


class _ConcreteAutoPlayer(AutomaticPlayer):
    def choose_move(self, state: GameState) -> GameMove:
        return _ConcreteMove()


class TestAutomaticPlayer:
    def test_is_subclass_of_player(self) -> None:
        assert issubclass(AutomaticPlayer, Player)

    def test_cannot_instantiate_without_choose_move(self) -> None:
        with pytest.raises(TypeError):
            AutomaticPlayer()  # type: ignore[abstract]

    def test_choose_move_returns_game_move(self) -> None:
        move = _ConcreteAutoPlayer().choose_move(_ConcreteState())
        assert isinstance(move, GameMove)
