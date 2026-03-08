"""Tests for the Hanoi position model."""

from __future__ import annotations

from iarena.playing.PlayerIndex import PlayerIndex
from iarena.gaming.hanoi.HanoiPosition import HanoiPosition
from iarena.gaming.hanoi.HanoiRules import HanoiRules


def test_init_stores_position_values() -> None:
    position = HanoiPosition(n_pegs=3, disks=[0, 1, 2], steps=4)

    assert position.n_pegs == 3
    assert position.disks == [0, 1, 2]
    assert position.steps == 4


def test_hash_changes_with_position_state() -> None:
    first = HanoiPosition(n_pegs=3, disks=[0, 0], steps=0)
    second = HanoiPosition(n_pegs=3, disks=[0, 1], steps=0)

    assert first.hash() != second.hash()


def test_next_player_returns_single_player_index_zero() -> None:
    position = HanoiPosition(n_pegs=3, disks=[0, 0], steps=0)

    assert position.next_player() == PlayerIndex(0)


def test_get_rules_returns_hanoi_rules() -> None:
    position = HanoiPosition(n_pegs=3, disks=[0, 0], steps=0)

    rules = position.get_rules()

    assert isinstance(rules, HanoiRules)
    assert rules.configuration.n_pegs == 3
    assert rules.configuration.disks == [0, 0]
