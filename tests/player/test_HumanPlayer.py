"""Tests for iarena.player.HumanPlayer."""

from iarena.game.GameMove import GameMove
from iarena.game.GameState import GameState
from iarena.interface.Interface import Interface
from iarena.player.HumanPlayer import HumanPlayer
from iarena.player.Player import Player
from iarena.view.View import View


class _ConcreteState(GameState):
    def current_player_id(self) -> int:
        return 0


class _ConcreteMove(GameMove):
    pass


class _ConcreteInterface(Interface):
    def __init__(self) -> None:
        super().__init__(view=None)

    def render(self, content: str) -> None:
        pass

    def ask(self, prompt: str) -> str:
        return "input"


class _ConcreteView(View):
    def __init__(self, move: GameMove) -> None:
        self._move = move
        self.ask_calls: int = 0

    def render_state(self, state: GameState, interface: Interface) -> None:
        pass

    def ask(self, interface: Interface) -> GameMove:
        self.ask_calls += 1
        return self._move


class TestHumanPlayer:
    def test_is_subclass_of_player(self) -> None:
        assert issubclass(HumanPlayer, Player)

    def test_choose_move_delegates_to_view_ask(self) -> None:
        expected = _ConcreteMove()
        view = _ConcreteView(expected)
        player = HumanPlayer(view=view, interface=_ConcreteInterface())
        result = player.choose_move(_ConcreteState())
        assert result is expected
        assert view.ask_calls == 1

    def test_choose_move_returns_game_move(self) -> None:
        player = HumanPlayer(view=_ConcreteView(_ConcreteMove()), interface=_ConcreteInterface())
        assert isinstance(player.choose_move(_ConcreteState()), GameMove)
