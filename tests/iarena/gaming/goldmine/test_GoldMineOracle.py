"""Tests for the GoldMine oracle implementation."""

from __future__ import annotations

import pytest

from iarena.gaming.goldmine.GoldMineConfiguration import GoldMineConfiguration
from iarena.gaming.goldmine.GoldMineOracle import GoldMineOracle
from iarena.gaming.goldmine.GoldMineRules import GoldMineRules
from iarena.gaming.hanoi.HanoiConfiguration import HanoiConfiguration
from iarena.gaming.hanoi.HanoiRules import HanoiRules
from iarena.playing.PlayerIndex import PlayerIndex


def _rules() -> GoldMineRules:
    """Return one deterministic GoldMine ruleset for oracle benchmarks."""
    return GoldMineRules(
        GoldMineConfiguration(
            n_rows=3,
            n_cols=3,
            map_data=[
                [0.0, 1.0, 8.0],
                [1.0, 1.0, 8.0],
                [8.0, 1.0, 1.0],
            ],
            start=None,
            target=None,
            compass_activated=True,
            proximity_activated=True,
            density_activated=False,
            seed=9,
        ),
    )


def test_default_returns_goldmine_oracle_instance() -> None:
    """`default` should provide one ready-to-use GoldMine oracle."""
    oracle = GoldMineOracle.default()

    assert isinstance(oracle, GoldMineOracle)


def test_reckon_solution_score_returns_ordered_score_limits() -> None:
    """`reckon_solution_score` should return scoreboards with ordered limits."""
    best_board, worst_board = GoldMineOracle.reckon_solution_score(_rules())

    best_value = float(best_board._scores[PlayerIndex(0)])
    worst_value = float(worst_board._scores[PlayerIndex(0)])
    assert best_value >= worst_value


def test_reckon_solution_score_rejects_non_goldmine_rules() -> None:
    """`reckon_solution_score` should reject rules from other games."""
    wrong_rules = HanoiRules(HanoiConfiguration(n_pegs=3, disks=[0, 0]))

    with pytest.raises(TypeError, match="GoldMineRules"):
        GoldMineOracle.reckon_solution_score(wrong_rules)


def test_custom_constructor_keeps_configured_ratios_and_repetitions() -> None:
    """Constructor should preserve configured oracle simulation parameters."""
    oracle = GoldMineOracle(repetitions=5, higher_limit_ratio=1.3, lower_limit_ratio=0.7, player_seed=12)

    assert oracle.repetitions == 5
    assert oracle.higher_limit_ratio == 1.3
    assert oracle.lower_limit_ratio == 0.7
