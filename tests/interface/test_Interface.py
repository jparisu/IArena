"""Tests for iarena.interface.Interface."""

from typing import Any

import pytest

from iarena.game.GameMove import GameMove
from iarena.game.GameState import GameState
from iarena.interface.Interface import Interface
from iarena.player.Player import Player
from iarena.view.View import View


class _ConcreteState(GameState):
    def current_player_id(self) -> int:
        return 0


class _ConcreteMove(GameMove):
    pass


class _ConcreteView(View):
    def __init__(self) -> None:
        self.render_calls: int = 0

    def render_state(self, state: GameState, interface: Interface) -> None:
        self.render_calls += 1

    def ask(self, interface: Interface) -> GameMove:
        return _ConcreteMove()


class _ConcretePlayer(Player):
    def choose_move(self, state: GameState) -> GameMove:
        return _ConcreteMove()


class _ConcreteInterface(Interface):
    def __init__(self, view: View | None = None) -> None:
        super().__init__(view=view)
        self.rendered: list[str] = []

    def render(self, content: str) -> None:
        self.rendered.append(content)

    def ask(self, prompt: str) -> str:
        return "input"


class TestInterface:
    def test_cannot_instantiate_abstract_class(self) -> None:
        with pytest.raises(TypeError):
            Interface()  # type: ignore[abstract]

    def test_on_turn_start_calls_view_render_state_when_view_set(self) -> None:
        view = _ConcreteView()
        iface = _ConcreteInterface(view=view)
        iface.on_turn_start(_ConcreteState(), _ConcretePlayer())
        assert view.render_calls == 1

    def test_on_turn_start_does_not_raise_when_view_is_none(self) -> None:
        iface = _ConcreteInterface(view=None)
        iface.on_turn_start(_ConcreteState(), _ConcretePlayer())  # must not raise

    def test_on_game_start_does_not_raise(self) -> None:
        _ConcreteInterface().on_game_start(_ConcreteState())

    def test_on_game_end_does_not_raise(self) -> None:
        _ConcreteInterface().on_game_end(_ConcreteState(), result=None)

    def test_on_invalid_move_does_not_raise(self) -> None:
        _ConcreteInterface().on_invalid_move(_ConcreteState(), _ConcretePlayer(), _ConcreteMove())

    def test_on_turn_end_does_not_raise(self) -> None:
        _ConcreteInterface().on_turn_end(_ConcreteState(), _ConcretePlayer(), _ConcreteMove())

    def test_render_stores_output(self) -> None:
        iface = _ConcreteInterface()
        iface.render("hello")
        assert "hello" in iface.rendered

    def test_ask_returns_string(self) -> None:
        assert isinstance(_ConcreteInterface().ask("prompt"), str)
