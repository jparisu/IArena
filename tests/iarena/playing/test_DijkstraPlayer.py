"""Tests for the generic Dijkstra player implementation."""

from __future__ import annotations

from collections.abc import Iterator

import pytest

from iarena.gaming.Movement import Movement
from iarena.gaming.Position import Position
from iarena.gaming.Rules import Rules
from iarena.playing.DijkstraPlayer import DijkstraPlayer
from iarena.playing.PlayerIndex import PlayerIndex
from iarena.scoring.Score import Score
from iarena.scoring.ScoreBoard import ScoreBoard


class _GraphMovement(Movement):
    def __init__(self, target: str) -> None:
        self.target = target


class _GraphPosition(Position):
    def __init__(self, node: str, rules: _GraphRules) -> None:
        self.node = node
        self._rules = rules

    def hash(self) -> int:
        return hash(self.node)

    def next_player(self) -> PlayerIndex:
        return PlayerIndex(0)

    def get_rules(self) -> Rules:
        return self._rules


class _GraphRules(Rules):
    def __init__(
        self,
        start: str,
        graph: dict[str, list[str]],
        costs: dict[str, float],
        goals: set[str],
        n_players: int = 1,
    ) -> None:
        self._start = start
        self._graph = graph
        self._costs = costs
        self._goals = goals
        self._n_players = n_players

    def n_players(self) -> int:
        return self._n_players

    def first_position(self) -> Position:
        return _GraphPosition(self._start, self)

    def next_position(self, pos: Position, mov: Movement) -> Position:
        if not isinstance(pos, _GraphPosition):
            raise TypeError("pos must be _GraphPosition")
        if not isinstance(mov, _GraphMovement):
            raise TypeError("mov must be _GraphMovement")
        if mov.target not in self._graph.get(pos.node, []):
            raise ValueError("Illegal graph movement.")
        return _GraphPosition(mov.target, self)

    def possible_movements(self, pos: Position) -> Iterator[Movement]:
        if not isinstance(pos, _GraphPosition):
            raise TypeError("pos must be _GraphPosition")
        for target in self._graph.get(pos.node, []):
            yield _GraphMovement(target)

    def is_finished(self, pos: Position) -> bool:
        if not isinstance(pos, _GraphPosition):
            raise TypeError("pos must be _GraphPosition")
        return pos.node in self._goals

    def get_score(self, pos: Position) -> ScoreBoard:
        if not isinstance(pos, _GraphPosition):
            raise TypeError("pos must be _GraphPosition")
        board = ScoreBoard()
        board._scores = {PlayerIndex(0): Score(-self.current_cost(pos.node))}
        return board

    def current_cost(self, node: str) -> float:
        return self._costs[node]


class _GraphDijkstraPlayer(DijkstraPlayer):
    def current_cost(self, pos: Position) -> float:
        if not isinstance(pos, _GraphPosition):
            raise TypeError("pos must be an instance of _GraphPosition.")
        graph_rules = pos.get_rules()
        if not isinstance(graph_rules, _GraphRules):
            raise TypeError("rules must be an instance of _GraphRules.")
        return graph_rules.current_cost(pos.node)


def test_name_returns_stable_identifier() -> None:
    assert _GraphDijkstraPlayer().name() == "dijkstra-player"


def test_play_selects_path_with_lowest_finished_cost() -> None:
    rules = _GraphRules(
        start="start",
        graph={
            "start": ["expensive-goal", "via"],
            "via": ["cheap-goal"],
            "expensive-goal": [],
            "cheap-goal": [],
        },
        costs={
            "start": 0.0,
            "via": 1.0,
            "cheap-goal": 2.0,
            "expensive-goal": 5.0,
        },
        goals={"cheap-goal", "expensive-goal"},
    )
    player = _GraphDijkstraPlayer()

    movement = player.play(rules.first_position())

    assert isinstance(movement, _GraphMovement)
    assert movement.target == "via"


def test_play_rejects_finished_positions() -> None:
    rules = _GraphRules(
        start="goal",
        graph={"goal": []},
        costs={"goal": 0.0},
        goals={"goal"},
    )
    player = _GraphDijkstraPlayer()

    with pytest.raises(ValueError, match="already solved"):
        player.play(rules.first_position())


def test_play_rejects_decreasing_cost_transitions() -> None:
    rules = _GraphRules(
        start="start",
        graph={"start": ["goal"], "goal": []},
        costs={"start": 1.0, "goal": 0.0},
        goals={"goal"},
    )
    player = _GraphDijkstraPlayer()

    with pytest.raises(ValueError, match="non-decreasing"):
        player.play(rules.first_position())


def test_starting_game_requires_one_player_rules() -> None:
    rules = _GraphRules(
        start="start",
        graph={"start": []},
        costs={"start": 0.0},
        goals={"start"},
        n_players=2,
    )
    player = _GraphDijkstraPlayer()

    with pytest.raises(ValueError, match="one-player"):
        player.starting_game(rules=rules, player_index=PlayerIndex(0))
