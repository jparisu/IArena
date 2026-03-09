from __future__ import annotations

from typing import TYPE_CHECKING

from iarena.arening.GenericArena import GenericArena
from iarena.gaming.Movement import Movement
from iarena.playing.PlayerIndex import PlayerIndex
from iarena.scoring.Score import Score
from iarena.scoring.ScoreBoard import ScoreBoard

if TYPE_CHECKING:
    from iarena.gaming.Position import Position
    from iarena.gaming.Rules import Rules
    from iarena.playing.Player import Player
    from iarena.visualizing.View import View


class _DummyMovement(Movement):
    pass


class _DummyBoard(ScoreBoard):
    def __init__(self, score: float) -> None:
        self._scores = {PlayerIndex(0): Score(score)}

    def get_score(self, index: PlayerIndex) -> Score:
        return self._scores[index]


class _DummyRules:
    def get_score(self, pos: Position) -> ScoreBoard:
        _ = pos
        return _DummyBoard(score=0.5)


class _ArenaWithHooks(GenericArena):
    def __init__(self) -> None:
        self._rules = _DummyRules()
        self._position = object()
        self._turn_count = 0
        self._last_movement: Movement | None = None
        self._should_store_logs = True
        self.logged_movements: list[Movement] = []

    def play(self, rules: Rules, players: list[Player], view: View | None = None) -> ScoreBoard:
        _ = rules
        _ = players
        _ = view
        return self._game_loop()

    def _execute_turn(self) -> None:
        self._turn_count += 1
        self._last_movement = _DummyMovement()

    def _check_timeout(self) -> bool:
        return False

    def _check_score_limit(self) -> bool:
        return self._turn_count >= 2

    def _check_max_turns(self) -> bool:
        return False

    def _store_logs(self, last_movement: Movement) -> None:
        self.logged_movements.append(last_movement)


def test_game_loop_executes_turns_until_termination_and_returns_scoreboard() -> None:
    arena = _ArenaWithHooks()

    scoreboard = arena._game_loop()

    assert isinstance(scoreboard, ScoreBoard)
    assert scoreboard.get_score(PlayerIndex(0)) == Score(0.5)
    assert arena._turn_count == 2
    assert len(arena.logged_movements) == 2
