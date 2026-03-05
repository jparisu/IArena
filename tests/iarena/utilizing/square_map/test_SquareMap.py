"""Tests for square-map data structures and navigation helpers."""

from __future__ import annotations

import numpy as np
import pytest

from iarena.utilizing.square_map.SquareMap import Coordinate, Direction, SquareMap


def test_direction_and_coordinate_helpers() -> None:
    """Direction and coordinate helpers should move consistently."""
    assert Direction.Up.delta == (-1, 0)
    assert Direction.Left.opposite() is Direction.Right

    coord = Coordinate(2, 3)
    assert coord.up() == Coordinate(1, 3)
    assert coord.down() == Coordinate(3, 3)
    assert coord.left() == Coordinate(2, 2)
    assert coord.right() == Coordinate(2, 4)
    assert coord.moved(Direction.Up) == Coordinate(1, 3)
    assert coord.from_direction(Direction.Right) == Coordinate(2, 4)
    assert coord.manhattan_distance(Coordinate(5, 1)) == 5
    assert coord.as_tuple() == (2, 3)
    assert tuple(coord) == (2, 3)

    neighbors = list(coord.neighbors())
    assert neighbors == [
        (Direction.Up, Coordinate(1, 3)),
        (Direction.Down, Coordinate(3, 3)),
        (Direction.Left, Coordinate(2, 2)),
        (Direction.Right, Coordinate(2, 4)),
    ]


def test_square_map_construction_and_indexing() -> None:
    """SquareMap should support tuple/coordinate indexing and size helpers."""
    with pytest.raises(ValueError):
        SquareMap([])
    with pytest.raises(ValueError):
        SquareMap([[]])
    with pytest.raises(ValueError):
        SquareMap([[1, 2], [3]])

    smap = SquareMap([[1.0, 2.0], [3.0, 4.0]])
    assert smap.size() == (2, 2)
    assert smap.n_rows() == 2
    assert smap.n_cols() == 2
    assert len(smap) == 2
    assert list(iter(smap)) == [[1.0, 2.0], [3.0, 4.0]]

    assert smap[Coordinate(0, 1)] == 2.0
    assert smap[(1, 0)] == 3.0
    smap[(1, 1)] = 7.0
    assert smap[Coordinate(1, 1)] == 7.0
    assert smap._to_coordinate((1, 0)) == Coordinate(1, 0)


def test_square_map_text_bounds_and_neighbor_accessors() -> None:
    """Text rendering and neighbor iterators should expose valid cells only."""
    smap = SquareMap([[10, 2], [3, 40]])
    rendered = smap.to_text()
    assert str(smap) == rendered
    assert "10" in rendered

    assert smap.in_bounds(Coordinate(1, 1)) is True
    assert smap.in_bounds(Coordinate(2, 0)) is False
    smap.require_in_bounds(Coordinate(0, 1))
    with pytest.raises(IndexError):
        smap.require_in_bounds(Coordinate(3, 0), name="start")

    assert smap.get(Coordinate(9, 9), default=-1) == -1

    pairs = list(smap.possible_direction_neighbor(Coordinate(0, 0)))
    assert pairs == [(Direction.Down, Coordinate(1, 0)), (Direction.Right, Coordinate(0, 1))]
    assert list(smap.possible_direction_neighbors(Coordinate(0, 0))) == pairs
    assert list(smap.possible_directions(Coordinate(0, 0))) == [Direction.Down, Direction.Right]
    assert list(smap.possible_neighbors(Coordinate(0, 0))) == [Coordinate(1, 0), Coordinate(0, 1)]


def test_square_map_iteration_validation_and_factories() -> None:
    """Coordinate/value iteration and factory constructors should behave correctly."""
    smap = SquareMap([[1.0, 0.0], [3.0, 4.0]])
    assert list(smap.iter_coordinates()) == [
        Coordinate(0, 0),
        Coordinate(0, 1),
        Coordinate(1, 0),
        Coordinate(1, 1),
    ]
    assert list(smap.iter_values()) == [1.0, 0.0, 3.0, 4.0]

    smap.check(allow_zero=True)
    with pytest.raises(ValueError):
        smap.check(allow_zero=False)
    smap.check(allow_zero=False, skip_coordinate_validation=[Coordinate(0, 1)])

    filled = SquareMap.full(2, 3, "x")
    assert filled.size() == (2, 3)
    assert all(value == "x" for value in filled.iter_values())
    with pytest.raises(ValueError):
        SquareMap.full(0, 2, 1)

    zeros = SquareMap.zeros(2, 2)
    assert list(zeros.iter_values()) == [0.0, 0.0, 0.0, 0.0]
    with pytest.raises(ValueError):
        SquareMap.zeros(2, 0)

    zeros_like = SquareMap.zeros_like(filled)
    assert zeros_like.size() == (2, 3)


def test_square_map_numpy_copy_compass_and_reductions() -> None:
    """NumPy conversion, copy, compass and reductions should be correct."""
    source = np.array([[1.0, 2.0], [3.0, 4.0]])
    smap = SquareMap.from_numpy(source)
    with pytest.raises(ValueError):
        SquareMap.from_numpy(np.array([1.0, 2.0]))

    out = smap.to_numpy(dtype=int)
    assert out.dtype == np.int64
    assert np.array_equal(out, np.array([[1, 2], [3, 4]]))

    smap_copy = smap.copy()
    smap_copy[(0, 0)] = 99.0
    assert smap[(0, 0)] == 1.0

    assert smap.compass_direction(Coordinate(0, 0), Coordinate(0, 2)) is Direction.Right
    assert smap.compass_direction(Coordinate(0, 0), Coordinate(2, 1)) is Direction.Down
    assert smap.compass_direction(Coordinate(0, 0), Coordinate(-2, -2)) is Direction.Up
    with pytest.raises(ValueError):
        smap.compass_direction(Coordinate(0, 0), Coordinate(0, 0))

    assert smap.min() == 1.0
    assert smap.max() == 4.0
    assert smap.sum() == 10.0
