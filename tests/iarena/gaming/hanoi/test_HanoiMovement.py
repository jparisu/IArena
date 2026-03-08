"""Tests for the Hanoi movement model."""

from __future__ import annotations

import pytest

from iarena.gaming.hanoi.HanoiMovement import HanoiMovement


def test_init_stores_from_and_to_pegs() -> None:
    movement = HanoiMovement(from_peg=0, to_peg=2)

    assert movement.from_peg == 0
    assert movement.to_peg == 2


def test_init_rejects_negative_peg_indices() -> None:
    with pytest.raises(ValueError, match="non-negative"):
        HanoiMovement(from_peg=-1, to_peg=0)


def test_init_rejects_equal_from_and_to_pegs() -> None:
    with pytest.raises(ValueError, match="must be different"):
        HanoiMovement(from_peg=1, to_peg=1)


def test_str_and_repr_are_user_friendly() -> None:
    movement = HanoiMovement(from_peg=0, to_peg=2)

    assert str(movement) == "0 -> 2"
    assert "from_peg=0" in repr(movement)
