from __future__ import annotations

from iarena.grading.DebugLevel import DebugLevel


def test_debug_level_values_follow_expected_order() -> None:
    assert DebugLevel.NONE.value == 0
    assert DebugLevel.ERROR.value == 1
    assert DebugLevel.WARNING.value == 2
    assert DebugLevel.USER.value == 3
    assert DebugLevel.INFO.value == 4
    assert DebugLevel.DEBUG.value == 5


def test_debug_level_members_are_unique() -> None:
    assert len({level.value for level in DebugLevel}) == len(list(DebugLevel))
