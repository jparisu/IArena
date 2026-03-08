from __future__ import annotations

from iarena.utilizing.mapping.square_map.SquareMapCoordinate import SquareMapCoordinate
from iarena.utilizing.mapping.square_map.SquareMapDirection import SquareMapDirection


def _coord(x: int, y: int) -> SquareMapCoordinate:
    c = SquareMapCoordinate()
    c.x = x
    c.y = y
    return c


def test_from_tuple_builds_coordinate_from_pair() -> None:
    c = SquareMapCoordinate.from_tuple((3, 5))
    assert isinstance(c, SquareMapCoordinate)
    assert c.x == 3
    assert c.y == 5


def test_up_returns_coordinate_with_previous_row() -> None:
    c = _coord(4, 6)
    moved = c.up()
    assert moved.x == 3 and moved.y == 6


def test_down_returns_coordinate_with_next_row() -> None:
    c = _coord(4, 6)
    moved = c.down()
    assert moved.x == 5 and moved.y == 6


def test_left_returns_coordinate_with_previous_col() -> None:
    c = _coord(4, 6)
    moved = c.left()
    assert moved.x == 4 and moved.y == 5


def test_right_returns_coordinate_with_next_col() -> None:
    c = _coord(4, 6)
    moved = c.right()
    assert moved.x == 4 and moved.y == 7


def test_moved_returns_coordinate_for_given_direction() -> None:
    c = _coord(10, 10)
    moved = c.moved(SquareMapDirection.LEFT)
    assert moved.x == 10 and moved.y == 9


def test_from_direction_is_alias_of_moved() -> None:
    c = _coord(1, 1)
    assert c.from_direction(SquareMapDirection.DOWN).as_tuple() == c.moved(SquareMapDirection.DOWN).as_tuple()


def test_manhattan_distance_returns_absolute_grid_distance() -> None:
    a = _coord(1, 2)
    b = _coord(4, 8)
    assert a.manhattan_distance(b) == 9


def test_as_tuple_returns_row_col_pair() -> None:
    c = _coord(7, 9)
    assert c.as_tuple() == (7, 9)


def test_iter_iterates_in_xy_order() -> None:
    c = _coord(2, 3)
    assert tuple(iter(c)) == (2, 3)


def test_len_returns_two_for_tuple_like_semantics() -> None:
    c = _coord(2, 3)
    assert len(c) == 2


def test_getitem_accesses_coordinate_components() -> None:
    c = _coord(11, 12)
    assert c[0] == 11
    assert c[1] == 12


def test_neighbors_returns_all_four_direction_coordinate_pairs() -> None:
    c = _coord(5, 5)
    neighbors = list(c.neighbors())
    assert len(neighbors) == 4
    deltas = {d for d, _ in neighbors}
    assert deltas == {
        SquareMapDirection.UP,
        SquareMapDirection.RIGHT,
        SquareMapDirection.DOWN,
        SquareMapDirection.LEFT,
    }
