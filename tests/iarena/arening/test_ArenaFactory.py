from __future__ import annotations

import time
from typing import TYPE_CHECKING
from collections.abc import Iterator

import pytest

from iarena.arening.ArenaFactory import ArenaFactory
from iarena.gaming.Movement import Movement
from iarena.gaming.Position import Position
from iarena.gaming.Rules import Rules
from iarena.playing.Player import Player
from iarena.playing.PlayerIndex import PlayerIndex
from iarena.scoring.Score import Score
from iarena.scoring.ScoreBoard import ScoreBoard
from iarena.visualizing.View import View

if TYPE_CHECKING:
    from iarena.visualizing.Canvas import Canvas


class _Move(Movement):
    pass


class _Board(ScoreBoard):
    def __init__(self, score: float) -> None:
        self._scores = {PlayerIndex(0): Score(score)}

    def get_score(self, index: PlayerIndex) -> Score:
        return self._scores[index]


class _Position(Position):
    def __init__(self, rules: Rules, turn: int = 0) -> None:
        self._rules = rules
        self.turn = turn

    def hash(self) -> int:
        return self.turn

    def next_player(self) -> PlayerIndex:
        return PlayerIndex(0)

    def get_rules(self) -> Rules:
        return self._rules


class _Rules(Rules):
    def n_players(self) -> int:
        return 1

    def first_position(self) -> Position:
        return _Position(self, turn=0)

    def next_position(self, pos: Position, mov: Movement) -> Position:
        _ = mov
        position = pos
        assert isinstance(position, _Position)
        return _Position(self, turn=position.turn + 1)

    def possible_movements(self, pos: Position) -> Iterator[Movement]:
        _ = pos
        return iter([_Move()])

    def is_finished(self, pos: Position) -> bool:
        position = pos
        assert isinstance(position, _Position)
        return position.turn >= 3

    def get_score(self, pos: Position) -> ScoreBoard:
        position = pos
        assert isinstance(position, _Position)
        return _Board(score=float(position.turn))


class _Player(Player):
    def name(self) -> str:
        return "dummy-player"

    def play(self, pos: Position) -> Movement:
        _ = pos
        return _Move()

    def starting_game(self, rules: Rules, player_index: PlayerIndex) -> None:
        _ = rules
        _ = player_index


class _SlowPlayer(Player):
    def __init__(self, sleep_s: float) -> None:
        self._sleep_s = sleep_s

    def name(self) -> str:
        return "slow-player"

    def play(self, pos: Position) -> Movement:
        _ = pos
        time.sleep(self._sleep_s)
        return _Move()

    def starting_game(self, rules: Rules, player_index: PlayerIndex) -> None:
        _ = rules
        _ = player_index


class _View(View):
    def render_info(self, rules: Rules, canvas: Canvas) -> None:
        _ = rules
        _ = canvas

    def render_state(self, pos: Position, canvas: Canvas) -> None:
        _ = pos
        _ = canvas

    def capture_input(self, *args: object) -> Movement:
        _ = args
        return _Move()


def test_create_arena_returns_playable_arena_instance() -> None:
    rules = _Rules()
    view = _View()
    players: list[Player] = [_Player()]

    arena = ArenaFactory.create_arena(
        max_turns=10,
        max_turn_time_s=1.0,
        max_total_time_s=5.0,
        score_limits=(Score(-100.0), Score(100.0)),
        store_logs=True,
    )

    scoreboard = arena.play(rules=rules, players=players, view=view)

    assert isinstance(scoreboard, ScoreBoard)
    assert scoreboard.get_score(PlayerIndex(0)) == Score(3.0)


def test_create_arena_raises_value_error_for_invalid_max_turns() -> None:
    with pytest.raises(ValueError):
        ArenaFactory.create_arena(
            max_turns=0,
            max_turn_time_s=1.0,
            max_total_time_s=10.0,
            score_limits=(Score(-1.0), Score(1.0)),
            store_logs=False,
        )


def test_create_arena_allows_default_none_limits() -> None:
    rules = _Rules()
    view = _View()
    players: list[Player] = [_Player()]

    arena = ArenaFactory.create_arena()

    scoreboard = arena.play(rules=rules, players=players, view=view)

    assert isinstance(scoreboard, ScoreBoard)
    assert scoreboard.get_score(PlayerIndex(0)) == Score(3.0)


def test_create_arena_without_turn_timeout_allows_slow_turns() -> None:
    rules = _Rules()
    view = _View()
    players: list[Player] = [_SlowPlayer(sleep_s=0.02)]

    arena = ArenaFactory.create_arena(
        max_turns=10,
        max_turn_time_s=None,
        max_total_time_s=None,
        score_limits=None,
        store_logs=False,
    )

    scoreboard = arena.play(rules=rules, players=players, view=view)

    assert isinstance(scoreboard, ScoreBoard)
    assert scoreboard.get_score(PlayerIndex(0)) == Score(3.0)


def test_create_arena_keeps_turn_timeout_when_total_timeout_is_none() -> None:
    rules = _Rules()
    view = _View()
    players: list[Player] = [_SlowPlayer(sleep_s=0.05)]

    arena = ArenaFactory.create_arena(
        max_turns=10,
        max_turn_time_s=0.001,
        max_total_time_s=None,
        score_limits=None,
        store_logs=False,
    )

    scoreboard = arena.play(rules=rules, players=players, view=view)

    assert isinstance(scoreboard, ScoreBoard)
    assert scoreboard.get_score(PlayerIndex(0)) == Score(0.0)


def test_play_defaults_to_empty_view_when_no_view_is_provided() -> None:
    rules = _Rules()
    players: list[Player] = [_Player()]

    arena = ArenaFactory.create_arena()

    scoreboard = arena.play(rules=rules, players=players)

    assert isinstance(scoreboard, ScoreBoard)
    assert scoreboard.get_score(PlayerIndex(0)) == Score(3.0)
