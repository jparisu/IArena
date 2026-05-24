from __future__ import annotations

from iarena.scoring.Score import Score


def test_score_behaves_as_float_value() -> None:
    score = Score(3.5)

    assert isinstance(score, float)
    assert float(score) == 3.5


def test_score_supports_float_ordering_semantics() -> None:
    low = Score(1.0)
    high = Score(2.0)

    assert high > low
