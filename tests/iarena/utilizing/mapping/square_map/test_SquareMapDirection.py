from __future__ import annotations

from iarena.utilizing.mapping.square_map.SquareMapDirection import SquareMapDirection


def test_direction_members_are_defined() -> None:
    assert SquareMapDirection.UP.value == (-1, 0)
    assert SquareMapDirection.RIGHT.value == (0, 1)
    assert SquareMapDirection.DOWN.value == (1, 0)
    assert SquareMapDirection.LEFT.value == (0, -1)


def test_delta_returns_direction_delta_tuple() -> None:
    assert SquareMapDirection.UP.delta == (-1, 0)
    assert SquareMapDirection.RIGHT.delta == (0, 1)


def test_opposite_returns_inverse_direction() -> None:
    assert SquareMapDirection.UP.opposite() is SquareMapDirection.DOWN
    assert SquareMapDirection.LEFT.opposite() is SquareMapDirection.RIGHT
