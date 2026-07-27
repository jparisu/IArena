"""Tests for iarena.view.View."""

import pytest

from iarena.game.GameMove import GameMove
from iarena.game.GameState import GameState
from iarena.interface.Interface import Interface
from iarena.view.View import View


class _ConcreteState(GameState):
    def current_player_id(self) -> int:
        return 0


class _ConcreteMove(GameMove):
    pass


class _ConcreteInterface(Interface):
    def __init__(self) -> None:
        super().__init__(view=None)
        self.rendered: list[str] = []

    def render(self, content: str) -> None:
        self.rendered.append(content)

    def ask(self, prompt: str) -> str:
        return "input"


class _ConcreteView(View):
    def render_state(self, state: GameState, interface: Interface) -> None:
        interface.render("state")

    def ask(self, interface: Interface) -> GameMove:
        return _ConcreteMove()


class TestView:
    def test_cannot_instantiate_abstract_class(self) -> None:
        with pytest.raises(TypeError):
            View()  # type: ignore[abstract]

    def test_render_state_calls_interface_render(self) -> None:
        iface = _ConcreteInterface()
        _ConcreteView().render_state(_ConcreteState(), iface)
        assert iface.rendered == ["state"]

    def test_ask_returns_game_move(self) -> None:
        iface = _ConcreteInterface()
        move = _ConcreteView().ask(iface)
        assert isinstance(move, GameMove)
