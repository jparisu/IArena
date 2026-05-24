"""End-to-end integration tests for the full game session flow.

Uses a minimal countdown game (state holds an integer counter; each
turn the player decrements it by 1) to exercise the complete path
from Engine through Interface, View, and Player.
"""

from typing import Any

from iarena import (
    AutomaticPlayer,
    Engine,
    GameMove,
    GameRules,
    GameState,
    HumanPlayer,
    Interface,
    NullInterface,
    Player,
    View,
)


# ---------------------------------------------------------------------------
# Countdown game
# ---------------------------------------------------------------------------

class _DecrMove(GameMove):
    pass


class _CountState(GameState):
    def __init__(self, n: int, turns: int = 0) -> None:
        self.n = n
        self.turns = turns

    def current_player_id(self) -> int:
        return 0


class _CountRules(GameRules):
    def __init__(self, start: int) -> None:
        self._start = start

    def number_of_players(self) -> int:
        return 1

    def first_position(self) -> GameState:
        return _CountState(self._start)

    def apply_move(self, state: GameState, move: GameMove) -> GameState:
        assert isinstance(state, _CountState)
        return _CountState(state.n - 1, state.turns + 1)

    def is_terminal(self, state: GameState) -> bool:
        assert isinstance(state, _CountState)
        return state.n <= 0

    def result(self, state: GameState) -> Any:
        assert isinstance(state, _CountState)
        return state.turns

    def is_legal(self, state: GameState, move: GameMove) -> bool:
        return isinstance(move, _DecrMove)


class _CountView(View):
    def __init__(self) -> None:
        self.render_calls: int = 0
        self.ask_calls: int = 0

    def render_state(self, state: GameState, interface: Interface) -> None:
        self.render_calls += 1
        assert isinstance(state, _CountState)
        interface.render(f"counter={state.n}")

    def ask(self, interface: Interface) -> GameMove:
        self.ask_calls += 1
        interface.ask("decrement?")
        return _DecrMove()


class _DecrPlayer(AutomaticPlayer):
    def choose_move(self, state: GameState) -> GameMove:
        return _DecrMove()


class _TrackingInterface(Interface):
    def __init__(self, view: View | None = None) -> None:
        super().__init__(view=view)
        self.events: list[str] = []
        self.rendered: list[str] = []

    def render(self, content: str) -> None:
        self.rendered.append(content)

    def ask(self, prompt: str) -> str:
        self.events.append(f"ask:{prompt}")
        return ""

    def on_game_start(self, state: GameState) -> None:
        self.events.append("game_start")

    def on_turn_start(self, state: GameState, player: Player) -> None:
        self.events.append("turn_start")
        super().on_turn_start(state, player)

    def on_turn_end(self, state: GameState, player: Player, move: GameMove) -> None:
        self.events.append("turn_end")

    def on_invalid_move(self, state: GameState, player: Player, move: GameMove) -> None:
        self.events.append("invalid_move")

    def on_game_end(self, state: GameState, result: Any) -> None:
        self.events.append(f"game_end:{result}")


# ---------------------------------------------------------------------------
# Integration tests
# ---------------------------------------------------------------------------

class TestEngineWithAutomaticPlayer:
    def test_result_equals_number_of_turns(self) -> None:
        result = Engine(
            rules=_CountRules(3),
            players=[_DecrPlayer()],
            interface=NullInterface(),
        ).run()
        assert result == 3

    def test_lifecycle_events_fire_in_order(self) -> None:
        iface = _TrackingInterface()
        Engine(rules=_CountRules(2), players=[_DecrPlayer()], interface=iface).run()
        assert iface.events == [
            "game_start",
            "turn_start", "turn_end",
            "turn_start", "turn_end",
            "game_end:2",
        ]

    def test_view_render_state_called_on_turn_start(self) -> None:
        view = _CountView()
        iface = _TrackingInterface(view=view)
        Engine(rules=_CountRules(2), players=[_DecrPlayer()], interface=iface).run()
        assert view.render_calls == 2

    def test_view_render_state_calls_interface_render(self) -> None:
        view = _CountView()
        iface = _TrackingInterface(view=view)
        Engine(rules=_CountRules(1), players=[_DecrPlayer()], interface=iface).run()
        assert any("counter=" in r for r in iface.rendered)


class TestEngineWithHumanPlayer:
    def test_human_player_delegates_to_view_ask(self) -> None:
        view = _CountView()
        iface = _TrackingInterface(view=view)
        human = HumanPlayer(view=view, interface=iface)
        Engine(rules=_CountRules(2), players=[human], interface=iface).run()
        assert view.ask_calls == 2

    def test_human_player_ask_uses_interface(self) -> None:
        view = _CountView()
        iface = _TrackingInterface(view=view)
        human = HumanPlayer(view=view, interface=iface)
        Engine(rules=_CountRules(1), players=[human], interface=iface).run()
        assert any("ask:" in e for e in iface.events)

    def test_human_player_result_correct(self) -> None:
        view = _CountView()
        iface = _TrackingInterface(view=view)
        human = HumanPlayer(view=view, interface=iface)
        result = Engine(rules=_CountRules(3), players=[human], interface=iface).run()
        assert result == 3


class TestEngineIllegalMovePath:
    def test_invalid_move_fires_on_invalid_move_and_retries(self) -> None:
        class _BadThenGoodPlayer(AutomaticPlayer):
            def __init__(self) -> None:
                self.calls = 0

            def choose_move(self, state: GameState) -> GameMove:
                self.calls += 1
                if self.calls == 1:
                    return object()  # type: ignore[return-value]
                return _DecrMove()

        iface = _TrackingInterface()
        player = _BadThenGoodPlayer()
        Engine(rules=_CountRules(1), players=[player], interface=iface).run()
        assert "invalid_move" in iface.events
        assert player.calls == 2

    def test_game_completes_after_illegal_move_retry(self) -> None:
        class _OnceIllegalPlayer(AutomaticPlayer):
            def __init__(self) -> None:
                self._calls = 0

            def choose_move(self, state: GameState) -> GameMove:
                self._calls += 1
                return object() if self._calls == 1 else _DecrMove()  # type: ignore[return-value]

        result = Engine(
            rules=_CountRules(1),
            players=[_OnceIllegalPlayer()],
            interface=NullInterface(),
        ).run()
        assert result == 1
