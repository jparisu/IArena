"""Tests for GoldMine hint mode parsing."""

from __future__ import annotations

import pytest

from iarena.gaming.GoldMine.GoldMineHintMode import GoldMineHintMode


def test_hint_mode_from_value_accepts_none_and_case_insensitive_names() -> None:
    """`from_value` should parse known hint modes and default `None`.

    Args:
        None.

    Returns:
        None.
    """
    assert GoldMineHintMode.from_value(None) is GoldMineHintMode.NONE
    assert GoldMineHintMode.from_value("compass") is GoldMineHintMode.COMPASS
    assert GoldMineHintMode.from_value("PROXIMITY") is GoldMineHintMode.PROXIMITY
    assert GoldMineHintMode.from_value("Density") is GoldMineHintMode.DENSITY


def test_hint_mode_from_value_rejects_unknown_values() -> None:
    """`from_value` should raise for unsupported modes.

    Args:
        None.

    Returns:
        None.
    """
    with pytest.raises(ValueError):
        GoldMineHintMode.from_value("unknown-mode")
