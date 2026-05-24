from __future__ import annotations

import importlib
from pathlib import Path
from typing import TYPE_CHECKING, get_args, get_origin, get_type_hints

import pytest

from iarena.grading.Exam import Exam
from iarena.grading.DebugLevel import DebugLevel
from iarena.grading.Grader import Grader
from iarena.grading.MatchReport import MatchReport
from iarena.playing.LoadPlayer import LoadPlayer

if TYPE_CHECKING:
    from iarena.gaming.Movement import Movement
    from iarena.gaming.Position import Position
    from iarena.gaming.Rules import Rules
    from iarena.playing.PlayerIndex import PlayerIndex


class _Exam:
    def __init__(self) -> None:
        self.grade_calls = 0
        self.score_calls = 0
        self.last_debug_level: DebugLevel | None = None

    def grade(self, debug_level: DebugLevel = DebugLevel.USER) -> list[list[MatchReport]]:
        self.grade_calls += 1
        self.last_debug_level = debug_level
        report = MatchReport()
        report.moves = 1
        report.total_time_s = 0.1
        report.score = 1.0
        report.messages = {}
        return [[report]]

    def score(self) -> float:
        self.score_calls += 1
        return 7.5


class _Player(LoadPlayer):
    def play(self, pos: Position) -> Movement:
        return next(pos.get_rules().possible_movements(pos))

    def authors(self) -> list[str]:
        return ["Tester"]

    def starting_game(self, rules: Rules, player_index: PlayerIndex) -> None:
        _ = (rules, player_index)


def test_grade_delegates_to_exam_grader() -> None:
    grader = Grader()
    exam = _Exam()
    grader.grader = exam  # type: ignore[assignment]

    reports = grader.grade()

    assert exam.grade_calls == 1
    assert exam.last_debug_level == DebugLevel.USER
    assert len(reports) == 1


def test_grade_passes_requested_debug_level_to_exam_grader() -> None:
    grader = Grader()
    exam = _Exam()
    grader.grader = exam  # type: ignore[assignment]

    _ = grader.grade(debug_level=DebugLevel.DEBUG)

    assert exam.last_debug_level == DebugLevel.DEBUG


def test_score_delegates_to_exam_grader() -> None:
    grader = Grader()
    exam = _Exam()
    grader.grader = exam  # type: ignore[assignment]

    value = grader.score()

    assert exam.score_calls == 1
    assert value == 7.5


def test_grade_raises_runtime_error_when_grader_is_missing() -> None:
    grader = Grader()

    with pytest.raises(RuntimeError, match="requires `grader`"):
        _ = grader.grade()


def test_grade_method_declares_expected_return_annotation() -> None:
    annotation = get_type_hints(Grader.grade)["return"]

    assert get_origin(annotation) is list
    nested = get_args(annotation)[0]
    assert get_origin(nested) is list
    assert get_args(nested) == (MatchReport,)


def test_from_file_builds_grader_with_exam_reader(tmp_path: Path) -> None:
    configuration_file = tmp_path / "exam.yaml"
    configuration_file.write_text(
        "\n".join(
            [
                "game: hanoi",
                "trials:",
                "  - args:",
                "      n_pegs: 3",
                "      n_disks: 1",
            ],
        ),
        encoding="utf-8",
    )

    player = _Player()
    grader = Grader.from_file(str(configuration_file), player)

    assert grader.configuration_file == str(configuration_file)
    assert grader.player is player
    assert isinstance(grader.grader, Exam)


def test_from_file_reads_configuration_with_file_loader(monkeypatch: pytest.MonkeyPatch) -> None:
    module = importlib.import_module("iarena.grading.Grader")
    reads: list[tuple[str, bool]] = []

    def _fake_read_file(filename: str, allow_online: bool = True) -> str:
        reads.append((filename, allow_online))
        return "\n".join(
            [
                "game: hanoi",
                "trials:",
                "  - args:",
                "      n_pegs: 3",
                "      n_disks: 1",
            ],
        )

    monkeypatch.setattr(
        module,
        "FileLoader",
        type("FakeFileLoader", (), {"read_file": staticmethod(_fake_read_file)}),
    )

    grader = Grader.from_file("https://example.com/grader.yaml", _Player())

    assert isinstance(grader.grader, Exam)
    assert reads == [("https://example.com/grader.yaml", True)]
