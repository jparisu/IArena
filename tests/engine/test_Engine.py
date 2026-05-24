"""Tests for iarena.engine.Engine."""

from typing import Any
from collections.abc import Iterator

import pytest

from iarena.engine.Engine import Engine
from iarena.game.GameMove import GameMove
from iarena.game.GameRules import GameRules
from iarena.game.GameState import GameState
from iarena.interface.Interface import Interface
from iarena.interface.NullInterface import NullInterface
from iarena.player.Player import Player


# ---------------------------------------------------------------------------
# Minimal stubs
# ---------------------------------------------------------------------------

class _Move(GameMove):
    pass


class _State(GameState):
    def __init__(self, terminal: bool = False) -> None:
        self._terminal = terminal

    def current_player_id(self) -> int:
        return 0


class _OneMoveRules(GameRules):
    """Rules where the game ends after a single legal move."""

    def number_of_players(self) -> int:
        return 1

    def first_position(self) -> GameState:
        return _State(terminal=False)

    def apply_move(self, state: GameState, move: GameMove) -> GameState:
        return _State(terminal=True)

    def is_terminal(self, state: GameState) -> bool:
        assert isinstance(state, _State)
        return state._terminal

    def result(self, state: GameState) -> Any:
        return "done"

    def is_legal(self, state: GameState, move: GameMove) -> bool:
        return True


class _IllegalFirstMoveRules(_OneMoveRules):
    """Rules where the first move is rejected, the second is accepted."""

    def __init__(self) -> None:
        self._call_count = 0

    def is_legal(self, state: GameState, move: GameMove) -> bool:
        self._call_count += 1
        return self._call_count > 1


class _StaticPlayer(Player):
    def __init__(self) -> None:
        self.calls: int = 0

    def choose_move(self, state: GameState) -> GameMove:
        self.calls += 1
        return _Move()


class _TrackingInterface(NullInterface):
    def __init__(self) -> None:
        super().__init__()
        self.events: list[str] = []

    def on_game_start(self, state: GameState) -> None:
        self.events.append("game_start")

    def on_turn_start(self, state: GameState, player: Player) -> None:
        self.events.append("turn_start")

    def on_invalid_move(self, state: GameState, player: Player, move: GameMove) -> None:
        self.events.append("invalid_move")

    def on_turn_end(self, state: GameState, player: Player, move: GameMove) -> None:
        self.events.append("turn_end")

    def on_game_end(self, state: GameState, result: Any) -> None:
        self.events.append("game_end")


class _ConcreteEngine(Engine):
    pass


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestEngine:
    def test_run_returns_result(self) -> None:
        engine = _ConcreteEngine(
            rules=_OneMoveRules(),
            players=[_StaticPlayer()],
            interface=NullInterface(),
        )
        assert engine.run() == "done"

    def test_run_fires_lifecycle_events_in_order(self) -> None:
        iface = _TrackingInterface()
        _ConcreteEngine(
            rules=_OneMoveRules(),
            players=[_StaticPlayer()],
            interface=iface,
        ).run()
        assert iface.events == ["game_start", "turn_start", "turn_end", "game_end"]

    def test_run_retries_on_illegal_move(self) -> None:
        rules = _IllegalFirstMoveRules()
        player = _StaticPlayer()
        iface = _TrackingInterface()
        _ConcreteEngine(rules=rules, players=[player], interface=iface).run()
        assert player.calls == 2
        assert "invalid_move" in iface.events

    def test_run_asks_player_once_per_legal_move(self) -> None:
        player = _StaticPlayer()
        _ConcreteEngine(
            rules=_OneMoveRules(),
            players=[player],
            interface=NullInterface(),
        ).run()
        assert player.calls == 1
