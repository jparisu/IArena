from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass

import pytest

from iarena.interfacing.IArena import IArena
from iarena.interfacing.IGameRules import IGameRules
from iarena.interfacing.IMovement import IMovement
from iarena.interfacing.IPlayer import IPlayer, PlayerIndex
from iarena.interfacing.IPosition import IPosition
from iarena.interfacing.ScoreBoard import ScoreBoard


@dataclass(frozen=True)
class Move(IMovement):
    value: int


@dataclass(frozen=True)
class Position(IPosition):
    turn: int
    current_player: int
    points_p0: int
    points_p1: int

    def next_player(self) -> PlayerIndex:
        return self.current_player


class TwoTurnRules(IGameRules):
    def n_players(self) -> int:
        return 2

    def first_position(self) -> IPosition:
        return Position(turn=0, current_player=0, points_p0=0, points_p1=0)

    def next_position(self, movement: IMovement, position: IPosition) -> IPosition:
        assert isinstance(movement, Move)
        assert isinstance(position, Position)
        if position.current_player == 0:
            return Position(
                turn=position.turn + 1,
                current_player=1,
                points_p0=position.points_p0 + movement.value,
                points_p1=position.points_p1,
            )
        return Position(
            turn=position.turn + 1,
            current_player=0,
            points_p0=position.points_p0,
            points_p1=position.points_p1 + movement.value,
        )

    def possible_movements(self, position: IPosition) -> Iterator[IMovement]:
        del position
        return iter([Move(1), Move(2)])

    def finished(self, position: IPosition) -> bool:
        assert isinstance(position, Position)
        return position.turn >= 2

    def score(self, position: IPosition) -> ScoreBoard:
        assert isinstance(position, Position)
        board = ScoreBoard(2)
        board.define_score(0, float(position.points_p0))
        board.define_score(1, float(position.points_p1))
        return board


class TwoTurnRulesWithCurrentScore(TwoTurnRules):
    def score(self, position: IPosition) -> ScoreBoard:
        del position
        board = ScoreBoard(2)
        board.define_score(0, -1.0)
        board.define_score(1, -1.0)
        return board

    def current_score(self, position: IPosition) -> ScoreBoard:
        return super().score(position)


class FixedPlayer(IPlayer):
    def __init__(self, movement: Move) -> None:
        super().__init__()
        self._movement = movement
        self.started_as: PlayerIndex | None = None

    def play(self, position: IPosition) -> IMovement:
        del position
        return self._movement

    def starting_game(self, rules: IGameRules, player_index: PlayerIndex) -> None:
        del rules
        self.started_as = player_index


class ConcreteArena(IArena):
    def play(self) -> ScoreBoard:
        return self._play_loop()


def test_arena_play_runs_full_loop_and_returns_scoreboard() -> None:
    rules = TwoTurnRules()
    p0 = FixedPlayer(Move(1))
    p1 = FixedPlayer(Move(2))
    arena = ConcreteArena(rules=rules, players=[p0, p1])

    board = arena.play()

    assert p0.started_as == 0
    assert p1.started_as == 1
    assert board.score == [1.0, 2.0]


def test_arena_rejects_wrong_player_count() -> None:
    rules = TwoTurnRules()
    p0 = FixedPlayer(Move(1))

    with pytest.raises(ValueError):
        ConcreteArena(rules=rules, players=[p0])


def test_arena_rejects_illegal_movement() -> None:
    rules = TwoTurnRules()
    p0 = FixedPlayer(Move(99))
    p1 = FixedPlayer(Move(1))
    arena = ConcreteArena(rules=rules, players=[p0, p1])

    with pytest.raises(ValueError):
        arena.play()


def test_iarena_is_abstract() -> None:
    rules = TwoTurnRules()
    p0 = FixedPlayer(Move(1))
    p1 = FixedPlayer(Move(1))

    with pytest.raises(TypeError):
        IArena(rules=rules, players=[p0, p1])


def test_arena_uses_current_score_method() -> None:
    rules = TwoTurnRulesWithCurrentScore()
    p0 = FixedPlayer(Move(1))
    p1 = FixedPlayer(Move(2))
    arena = ConcreteArena(rules=rules, players=[p0, p1])

    board = arena.play()

    assert board.score == [1.0, 2.0]
