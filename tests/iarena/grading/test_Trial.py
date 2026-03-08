from __future__ import annotations

from typing import get_args, get_origin, get_type_hints

import pytest

from iarena.gaming.Movement import Movement
from iarena.gaming.Position import Position
from iarena.gaming.Rules import Rules
from iarena.grading.DebugLevel import DebugLevel
from iarena.grading.MatchConfiguration import MatchConfiguration
from iarena.grading.MatchReport import MatchReport
from iarena.grading.Trial import Trial
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
    def __init__(self, fail_on_next_position: bool = False) -> None:
        self.fail_on_next_position = fail_on_next_position

    def n_players(self) -> int:
        return 1

    def first_position(self) -> Position:
        return _Position(self, turn=0)

    def next_position(self, pos: Position, mov: Movement) -> Position:
        _ = mov
        if self.fail_on_next_position:
            raise ValueError("forced failure")
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
        position = pos
        assert isinstance(position, _Position)
        return _Board(float(position.turn))


class _Player(Player):
    def name(self) -> str:
        return "trial-player"

    def play(self, pos: Position) -> Movement:
        _ = pos
        return _Move()

    def starting_game(self, rules: Rules, player_index: PlayerIndex) -> None:
        _ = rules
        _ = player_index


def _trial_configuration(rules: Rules, repetitions: int = 2, allow_fails: int = 0) -> TrialConfiguration:
    return TrialConfiguration(
        match_configuration=MatchConfiguration(
            move_timeout_s=0.5,
            total_timeout_s=2.0,
            max_turns=3,
            score_limits=(Score(-10.0), Score(10.0)),
        ),
        trialing_player_index=PlayerIndex(0),
        rules=rules,
        players=[_Player()],
        repetitions=repetitions,
        allow_fails=allow_fails,
    )


def test_trial_runs_repetitions_and_returns_reports() -> None:
    trial = Trial()
    trial.configuration = _trial_configuration(_Rules(), repetitions=2)

    reports = trial.trial(DebugLevel.USER)

    assert len(reports) == 2
    assert all(isinstance(report, MatchReport) for report in reports)
    assert all(float(report.score) == 1.0 for report in reports)


def test_trial_raises_runtime_error_when_failures_exceed_allow_fails() -> None:
    trial = Trial()
    trial.configuration = _trial_configuration(_Rules(fail_on_next_position=True), repetitions=1, allow_fails=0)

    with pytest.raises(RuntimeError, match="allowed number of failed matches"):
        _ = trial.trial(DebugLevel.ERROR)


def test_score_returns_average_report_score() -> None:
    trial = Trial()
    report_a = MatchReport()
    report_a.moves = 1
    report_a.total_time_s = 0.1
    report_a.score = Score(1.0)
    report_a.messages = {}

    report_b = MatchReport()
    report_b.moves = 1
    report_b.total_time_s = 0.1
    report_b.score = Score(3.0)
    report_b.messages = {}

    trial.match_reports = [report_a, report_b]

    assert trial.score() == 2.0


def test_trial_method_declares_expected_return_annotation() -> None:
    annotation = get_type_hints(Trial.trial)["return"]

    assert get_origin(annotation) is list
    assert get_args(annotation) == (MatchReport,)
