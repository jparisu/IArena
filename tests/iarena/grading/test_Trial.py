from __future__ import annotations

from typing import get_args, get_origin, get_type_hints

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


def _trial_configuration(
    rules: Rules,
    repetitions: int = 2,
    value: float = 1.0,
    min_score: float = float("-inf"),
    max_score: float = float("inf"),
    description: str = "example trial",
) -> TrialConfiguration:
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
        description=description,
        value=value,
        min_score=min_score,
        max_score=max_score,
    )


def test_trial_runs_repetitions_and_returns_reports() -> None:
    trial = Trial()
    trial.configuration = _trial_configuration(_Rules(), repetitions=2)

    reports = trial.trial(DebugLevel.USER)

    assert len(reports) == 2
    assert all(isinstance(report, MatchReport) for report in reports)
    assert all(float(report.score) == 1.0 for report in reports)


def test_trial_marks_run_as_failed_when_match_execution_raises() -> None:
    trial = Trial()
    trial.configuration = _trial_configuration(_Rules(fail_on_next_position=True), repetitions=1)

    reports = trial.trial(DebugLevel.ERROR)

    assert len(reports) == 1
    assert float(reports[0].score) == 0.0
    assert reports[0].messages["accepted"] is False


def test_trial_adds_warning_when_score_is_outside_configured_limits() -> None:
    trial = Trial()
    trial.configuration = _trial_configuration(_Rules(), repetitions=1, min_score=2.0, max_score=10.0)

    reports = trial.trial(DebugLevel.WARNING)

    assert len(reports) == 1
    assert float(reports[0].score) == 0.0
    assert "warnings" in reports[0].messages
    assert "outside accepted range" in str(reports[0].messages["warnings"][0])
    assert reports[0].messages["accepted"] is False


def test_trial_score_returns_zero_when_one_repetition_fails() -> None:
    trial = Trial()
    trial.configuration = _trial_configuration(_Rules(), repetitions=2, min_score=2.0, max_score=10.0)
    trial.match_reports = trial.trial(DebugLevel.WARNING)

    assert trial.score() == 0.0


def test_trial_error_report_contains_structured_errors_message() -> None:
    trial = Trial()
    trial.configuration = _trial_configuration(_Rules(fail_on_next_position=True), repetitions=1)

    reports = trial.trial(DebugLevel.ERROR)

    assert len(reports) == 1
    assert "errors" in reports[0].messages
    assert "ValueError: forced failure" == reports[0].messages["errors"][0]


def test_score_returns_one_only_when_all_reports_are_accepted() -> None:
    trial = Trial()
    report_a = MatchReport()
    report_a.moves = 1
    report_a.total_time_s = 0.1
    report_a.score = Score(1.0)
    report_a.messages = {}

    report_b = MatchReport()
    report_b.moves = 1
    report_b.total_time_s = 0.1
    report_b.score = Score(0.0)
    report_b.messages = {}

    trial.match_reports = [report_a, report_b]

    assert trial.score() == 0.0


def test_trial_method_declares_expected_return_annotation() -> None:
    annotation = get_type_hints(Trial.trial)["return"]

    assert get_origin(annotation) is list
    assert get_args(annotation) == (MatchReport,)


def test_trial_none_debug_level_emits_no_output(capsys) -> None:  # type: ignore[no-untyped-def]
    trial = Trial()
    trial.configuration = _trial_configuration(_Rules(), repetitions=1, description="none trial")

    _ = trial.trial(DebugLevel.NONE)

    captured = capsys.readouterr()
    assert captured.out == ""


def test_trial_user_debug_level_emits_running_and_repetition_marker(capsys) -> None:  # type: ignore[no-untyped-def]
    trial = Trial()
    trial.configuration = _trial_configuration(_Rules(), repetitions=1, description="user trial")

    _ = trial.trial(DebugLevel.USER)

    captured = capsys.readouterr()
    assert "[TRIAL] Running: user trial" in captured.out
    assert "✓ repetition 1/1 (accepted)" in captured.out


def test_trial_warning_debug_level_emits_warning_line(capsys) -> None:  # type: ignore[no-untyped-def]
    trial = Trial()
    trial.configuration = _trial_configuration(_Rules(), repetitions=1, min_score=2.0, max_score=3.0)

    _ = trial.trial(DebugLevel.WARNING)

    captured = capsys.readouterr()
    assert "WARNING repetition 1" in captured.out
    assert "outside accepted range" in captured.out


def test_trial_info_debug_level_emits_trial_configuration(capsys) -> None:  # type: ignore[no-untyped-def]
    trial = Trial()
    trial.configuration = _trial_configuration(_Rules(), repetitions=1, description="info trial")

    _ = trial.trial(DebugLevel.INFO)

    captured = capsys.readouterr()
    assert "[TRIAL] Info: TrialConfiguration(" in captured.out
    assert "description='info trial'" in captured.out


def test_trial_debug_level_emits_detailed_repetition_information(capsys) -> None:  # type: ignore[no-untyped-def]
    trial = Trial()
    trial.configuration = _trial_configuration(_Rules(), repetitions=1)

    _ = trial.trial(DebugLevel.DEBUG)

    captured = capsys.readouterr()
    assert "[TRIAL] DEBUG repetition 1:" in captured.out
