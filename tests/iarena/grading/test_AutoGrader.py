from __future__ import annotations

from typing import get_args, get_origin, get_type_hints

import pytest

from iarena.grading.AutoGrader import AutoGrader
from iarena.grading.MatchReport import MatchReport


class _Exam:
    def __init__(self) -> None:
        self.grade_calls = 0
        self.score_calls = 0

    def grade(self) -> list[list[MatchReport]]:
        self.grade_calls += 1
        report = MatchReport()
        report.moves = 1
        report.total_time_s = 0.1
        report.score = 1.0
        report.messages = {}
        return [[report]]

    def score(self) -> float:
        self.score_calls += 1
        return 7.5


def test_grade_delegates_to_exam_grader() -> None:
    auto = AutoGrader()
    exam = _Exam()
    auto.grader = exam  # type: ignore[assignment]

    reports = auto.grade()

    assert exam.grade_calls == 1
    assert len(reports) == 1


def test_score_delegates_to_exam_grader() -> None:
    auto = AutoGrader()
    exam = _Exam()
    auto.grader = exam  # type: ignore[assignment]

    value = auto.score()

    assert exam.score_calls == 1
    assert value == 7.5


def test_grade_raises_runtime_error_when_grader_is_missing() -> None:
    auto = AutoGrader()

    with pytest.raises(RuntimeError, match="requires `grader`"):
        _ = auto.grade()


def test_grade_method_declares_expected_return_annotation() -> None:
    annotation = get_type_hints(AutoGrader.grade)["return"]

    assert get_origin(annotation) is list
    nested = get_args(annotation)[0]
    assert get_origin(nested) is list
    assert get_args(nested) == (MatchReport,)
