from __future__ import annotations

import numpy as np
import pytest

from iarena.utilizing.mapping.square_map.SquareMap import SquareMap
from iarena.utilizing.mapping.square_map.SquareMapCoordinate import SquareMapCoordinate
from iarena.utilizing.mapping.square_map.SquareMapDirection import SquareMapDirection


def _coord(x: int, y: int) -> SquareMapCoordinate:
    c = SquareMapCoordinate()
    c.x = x
    c.y = y
    return c


def _sample_map() -> SquareMap[int]:
    return SquareMap([[1, 2, 3], [4, 5, 6]])


def test_init_accepts_rectangular_rows() -> None:
    smap = SquareMap([[1, 2], [3, 4]])
    assert isinstance(smap, SquareMap)


def test_str_returns_map_text() -> None:
    assert "1" in str(_sample_map())


def test_pretty_text_renders_aligned_multiline_text() -> None:
    txt = _sample_map().pretty_text()
    assert "\n" in txt


def test_size_returns_rows_and_cols() -> None:
    assert _sample_map().size() == (2, 3)


def test_n_rows_returns_number_of_rows() -> None:
    assert _sample_map().n_rows() == 2


def test_n_cols_returns_number_of_columns() -> None:
    assert _sample_map().n_cols() == 3


def test_len_returns_row_count() -> None:
    assert len(_sample_map()) == 2


def test_iter_returns_rows_in_row_major_order() -> None:
    rows = list(iter(_sample_map()))
    assert rows == [[1, 2, 3], [4, 5, 6]]


def test_getitem_returns_value_at_coordinate() -> None:
    assert _sample_map()[_coord(1, 2)] == 6


def test_setitem_updates_value_at_coordinate() -> None:
    smap = _sample_map()
    smap[_coord(0, 1)] = 99
    assert smap[_coord(0, 1)] == 99


def test_in_bounds_validates_coordinate_inside_shape() -> None:
    smap = _sample_map()
    assert smap.in_bounds(_coord(1, 2)) is True
    assert smap.in_bounds(_coord(2, 0)) is False


def test_require_in_bounds_raises_for_out_of_bounds_coordinate() -> None:
    smap = _sample_map()
    with pytest.raises((ValueError, IndexError)):
        smap.require_in_bounds(_coord(2, 0), name="target")


def test_get_returns_default_when_out_of_bounds() -> None:
    smap = _sample_map()
    assert smap.get(_coord(5, 5), default=-1) == -1


def test_possible_direction_neighbors_returns_in_bounds_direction_pairs() -> None:
    smap = _sample_map()
    neighbors = list(smap.possible_direction_neighbors(_coord(0, 1)))
    assert {d for d, _ in neighbors} == {
        SquareMapDirection.LEFT,
        SquareMapDirection.RIGHT,
        SquareMapDirection.DOWN,
    }


def test_possible_directions_returns_valid_move_directions() -> None:
    smap = _sample_map()
    assert set(smap.possible_directions(_coord(0, 1))) == {
        SquareMapDirection.LEFT,
        SquareMapDirection.RIGHT,
        SquareMapDirection.DOWN,
    }


def test_possible_neighbors_returns_valid_neighbor_coordinates() -> None:
    smap = _sample_map()
    coords = {c.as_tuple() for c in smap.possible_neighbors(_coord(0, 1))}
    assert coords == {(0, 0), (0, 2), (1, 1)}


def test_iter_coordinates_yields_all_coordinates_row_major() -> None:
    smap = _sample_map()
    assert [c.as_tuple() for c in smap.iter_coordinates()] == [
        (0, 0),
        (0, 1),
        (0, 2),
        (1, 0),
        (1, 1),
        (1, 2),
    ]


def test_iter_values_yields_values_row_major() -> None:
    assert list(_sample_map().iter_values()) == [1, 2, 3, 4, 5, 6]


def test_check_rejects_negative_values_and_allows_zero_by_flag() -> None:
    ok = SquareMap([[0, 1]])
    ok.check(allow_zero=True)
    with pytest.raises(ValueError):
        ok.check(allow_zero=False)
    with pytest.raises(ValueError):
        SquareMap([[1, -1]]).check()


def test_full_creates_constant_map() -> None:
    smap = SquareMap.full(2, 3, 7)
    assert smap.size() == (2, 3)
    assert list(smap.iter_values()) == [7, 7, 7, 7, 7, 7]


def test_zeros_creates_float_zero_map() -> None:
    smap = SquareMap.zeros(2, 2)
    assert smap.size() == (2, 2)
    assert list(smap.iter_values()) == [0.0, 0.0, 0.0, 0.0]


def test_zeros_like_creates_zero_map_with_same_shape() -> None:
    template = SquareMap([[1, 2, 3], [4, 5, 6]])
    smap = SquareMap.zeros_like(template)
    assert smap.size() == template.size()
    assert list(smap.iter_values()) == [0.0] * 6


def test_from_numpy_builds_map_from_2d_array() -> None:
    arr = np.array([[1.0, 2.0], [3.0, 4.0]])
    smap = SquareMap.from_numpy(arr)
    assert smap.size() == (2, 2)
    assert smap[_coord(1, 0)] == 3.0


def test_to_numpy_exports_values_to_array_with_dtype() -> None:
    arr = _sample_map().to_numpy(dtype=float)
    assert arr.shape == (2, 3)
    assert arr.dtype == float
    assert arr[1, 2] == 6.0


def test_copy_returns_deep_copy() -> None:
    original = _sample_map()
    copied = original.copy()
    copied[_coord(0, 0)] = 100
    assert original[_coord(0, 0)] == 1
    assert copied[_coord(0, 0)] == 100


def test_compass_direction_returns_dominant_direction_between_coordinates() -> None:
    smap = _sample_map()
    assert smap.compass_direction(_coord(0, 0), _coord(0, 2)) is SquareMapDirection.RIGHT
    assert smap.compass_direction(_coord(1, 2), _coord(0, 2)) is SquareMapDirection.UP


def test_min_returns_smallest_numeric_value() -> None:
    assert _sample_map().min() == 1.0


def test_max_returns_largest_numeric_value() -> None:
    assert _sample_map().max() == 6.0


def test_sum_returns_sum_of_numeric_values() -> None:
    assert _sample_map().sum() == 21.0
