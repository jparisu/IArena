"""Tests for the Hanoi oracle implementation."""

from __future__ import annotations

from iarena.gaming.hanoi.HanoiConfiguration import HanoiConfiguration
from iarena.gaming.hanoi.HanoiOracle import HanoiOracle
from iarena.gaming.hanoi.HanoiRules import HanoiRules
from iarena.playing.PlayerIndex import PlayerIndex


def test_reckon_solution_score_returns_expected_best_and_worst_bounds() -> None:
    rules = HanoiRules(HanoiConfiguration(n_pegs=3, disks=[0, 0, 0]))

    best, worst = HanoiOracle.reckon_solution_score(rules=rules)

    assert float(best._scores[PlayerIndex(0)]) == -7.0
    assert float(worst._scores[PlayerIndex(0)]) == -7.0
