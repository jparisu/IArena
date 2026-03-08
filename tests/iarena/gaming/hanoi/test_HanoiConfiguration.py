"""Tests for the Hanoi configuration model."""

from __future__ import annotations

import pytest

from iarena.gaming.hanoi.HanoiConfiguration import HanoiConfiguration


def test_init_stores_configuration_values() -> None:
    configuration = HanoiConfiguration(n_pegs=3, disks=[0, 0, 1])

    assert configuration.n_pegs == 3
    assert configuration.disks == [0, 0, 1]


def test_init_rejects_invalid_peg_count() -> None:
    with pytest.raises(ValueError, match="at least 2"):
        HanoiConfiguration(n_pegs=1, disks=[0])


def test_init_rejects_out_of_range_disk_peg_indices() -> None:
    with pytest.raises(ValueError, match=r"within \[0, n_pegs\)"):
        HanoiConfiguration(n_pegs=3, disks=[0, 3])


def test_from_dict_uses_defaults_when_values_are_missing() -> None:
    configuration = HanoiConfiguration.from_dict({})

    assert configuration.n_pegs == 3
    assert configuration.disks == [0, 0, 0]


def test_from_dict_allows_using_n_disks_shortcut() -> None:
    configuration = HanoiConfiguration.from_dict({"n_pegs": 4, "n_disks": 2})

    assert configuration.n_pegs == 4
    assert configuration.disks == [0, 0]
