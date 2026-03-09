from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from typing import get_args, get_origin, get_type_hints

from iarena.gaming.Configuration import Configuration
from iarena.gaming.ConfigurationSuite import ConfigurationSuite
from iarena.gaming.Game import Game
from iarena.gaming.Movement import Movement
from iarena.gaming.Position import Position
from iarena.gaming.Rules import Rules
from iarena.grading.DebugLevel import DebugLevel
from iarena.grading.Exam import Exam
from iarena.grading.MatchConfiguration import MatchConfiguration
from iarena.grading.MatchReport import MatchReport
from iarena.grading.TrialConfiguration import TrialConfiguration
from iarena.playing.Player import Player
from iarena.playing.PlayerIndex import PlayerIndex
from iarena.scoring.Score import Score
from iarena.scoring.ScoreBoard import ScoreBoard


class _Move(Movement):
    pass


class _Board(ScoreBoard):
    def __init__(self, value: float) -> None:
        self._scores = {PlayerIndex(0): Score(value)}

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
    def __init__(self, value: float) -> None:
        self.value = value

    def n_players(self) -> int:
        return 1

    def first_position(self) -> Position:
        return _Position(self, turn=0)

    def next_position(self, pos: Position, mov: Movement) -> Position:
        _ = mov
        position = pos
        assert isinstance(position, _Position)
        return _Position(self, turn=position.turn + 1)

    def possible_movements(self, pos: Position):  # type: ignore[override]
        _ = pos
        return iter([_Move()])

    def is_finished(self, pos: Position) -> bool:
        position = pos
        assert isinstance(position, _Position)
        return position.turn >= 1

    def get_score(self, pos: Position) -> ScoreBoard:
        _ = pos
        return _Board(self.value)


@dataclass
class _Config(Configuration):
    value: float


class _Suite(ConfigurationSuite):
    def __init__(self, configurations: list[_Config]) -> None:
        self._configurations = configurations

    def generate_configurations(self) -> Iterator[Configuration]:
        return iter(self._configurations)

    def length(self) -> int:
        return len(self._configurations)


class _Player(Player):
    def name(self) -> str:
        return "exam-player"

    def play(self, pos: Position) -> Movement:
        _ = pos
        return _Move()

    def starting_game(self, rules: Rules, player_index: PlayerIndex) -> None:
        _ = rules
        _ = player_index


class _Game(Game):
    def name(self) -> str:
        return "exam-game"

    def generate_rules(self, conf: Configuration) -> Rules:
        typed = conf
        assert isinstance(typed, _Config)
        return _Rules(typed.value)


def test_grade_runs_trials_for_every_configuration() -> None:
    exam = Exam()
    exam.game = _Game()
    exam.player = _Player()
    exam.suite_configuration = _Suite([_Config(1.0), _Config(3.0)])

    reports = exam.grade(DebugLevel.USER)

    assert len(reports) == 2
    assert len(exam.trials) == 2
    assert exam.trial_results == [1.0, 1.0]
    assert exam.trial_value == [1.0, 1.0]


def test_score_returns_weighted_sum_from_trial_results_and_values() -> None:
    exam = Exam()
    exam.trial_results = [1.0, 0.0, 1.0]
    exam.trial_value = [2.0, 4.0, 6.0]
    exam.trials = []

    assert exam.score() == 8.0


def test_grade_uses_explicit_trial_configurations_when_provided() -> None:
    exam = Exam()
    exam.player = _Player()
    exam.trial_configurations = [
        TrialConfiguration(
            match_configuration=MatchConfiguration(
                move_timeout_s=0.2,
                total_timeout_s=1.0,
                max_turns=5,
                score_limits=(Score(-10.0), Score(10.0)),
            ),
            trialing_player_index=PlayerIndex(0),
            rules=_Rules(2.0),
            players=[exam.player],
            repetitions=1,
            value=3.0,
        ),
    ]

    reports = exam.grade(DebugLevel.USER)

    assert len(reports) == 1
    assert exam.trial_results == [1.0]
    assert exam.trial_value == [3.0]


def test_grade_method_declares_expected_return_annotation() -> None:
    annotation = get_type_hints(Exam.grade)["return"]

    assert get_origin(annotation) is list
    nested = get_args(annotation)[0]
    assert get_origin(nested) is list
    assert get_args(nested) == (MatchReport,)
