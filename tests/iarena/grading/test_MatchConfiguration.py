from __future__ import annotations

from iarena.grading.MatchConfiguration import MatchConfiguration
from iarena.scoring.Score import Score


def test_match_configuration_stores_expected_limits() -> None:
    configuration = MatchConfiguration(
        move_timeout_s=1.0,
        total_timeout_s=10.0,
        max_turns=20,
        score_limits=(Score(0.0), Score(100.0)),
    )

    assert configuration.move_timeout_s == 1.0
    assert configuration.total_timeout_s == 10.0
    assert configuration.max_turns == 20
    assert configuration.score_limits == (Score(0.0), Score(100.0))
