"""Tests for the Hanoi oracle implementation."""

from __future__ import annotations

import pytest

from iarena.gaming.hanoi.HanoiConfiguration import HanoiConfiguration
from iarena.gaming.hanoi.HanoiOracle import HanoiOracle
from iarena.gaming.hanoi.HanoiRules import HanoiRules
from iarena.playing.PlayerIndex import PlayerIndex
from iarena.utilizing.timing.Worker import Worker


def test_reckon_solution_score_returns_optimal_limits_for_multiple_disk_counts() -> None:
    for n_disks in range(1, 6):
        rules = HanoiRules(HanoiConfiguration(n_pegs=3, disks=[0] * n_disks))

        best, worst = HanoiOracle.reckon_solution_score(rules=rules)
        expected_score = float(-(2**n_disks - 1))

        assert float(best._scores[PlayerIndex(0)]) == expected_score
        assert float(worst._scores[PlayerIndex(0)]) == expected_score


def test_reckon_solution_score_uses_non_threaded_oracle_arena(monkeypatch: pytest.MonkeyPatch) -> None:
    rules = HanoiRules(HanoiConfiguration(n_pegs=3, disks=[0, 0, 0]))

    def _unexpected_worker_call(*args: object) -> object:
        _ = args
        raise AssertionError("Worker.limited_time_call should not be used by HanoiOracle.")

    monkeypatch.setattr(Worker, "limited_time_call", _unexpected_worker_call)

    best, worst = HanoiOracle.reckon_solution_score(rules=rules)

    assert float(best._scores[PlayerIndex(0)]) == -7.0
    assert float(worst._scores[PlayerIndex(0)]) == -7.0
