from __future__ import annotations

from typing import get_type_hints

from iarena.grading.MatchReport import MatchReport
from iarena.scoring.Score import Score


def test_match_report_exposes_expected_typed_fields() -> None:
    annotations = get_type_hints(MatchReport)

    assert annotations["moves"] is int
    assert annotations["total_time_s"] is float
    assert annotations["score"] is Score
    assert "messages" in annotations


def test_match_report_allows_runtime_assignment_of_report_data() -> None:
    report = MatchReport()

    report.moves = 12
    report.total_time_s = 1.5
    report.score = Score(8.0)
    report.messages = {"note": "ok"}

    assert report.moves == 12
    assert report.total_time_s == 1.5
    assert report.score == Score(8.0)
    assert report.messages == {"note": "ok"}
