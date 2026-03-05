"""Tests for square-map plotting utility."""

from __future__ import annotations

import pytest

from iarena.utilizing.square_map.SquareMap import Coordinate, SquareMap
from iarena.utilizing.square_map.draw_square_map import plot_square_map


class FakeFigure:
    """Tiny figure stub capturing colorbar calls."""

    def __init__(self) -> None:
        self.colorbar_calls = 0

    def colorbar(self, image, ax, fraction, pad) -> None:
        del image, ax, fraction, pad
        self.colorbar_calls += 1


class FakeAxis:
    """Tiny axis stub supporting calls used by `plot_square_map`."""

    def __init__(self, figure: FakeFigure | None) -> None:
        self.figure = figure
        self.scatter_calls: list[tuple[list[int], list[int], str]] = []
        self.text_calls: list[tuple[float, float, str]] = []
        self.title: str | None = None

    def imshow(self, data, cmap, origin, interpolation):
        del data, cmap, origin, interpolation
        return object()

    def set_xticks(self, *_args, **_kwargs) -> None:
        return None

    def set_yticks(self, *_args, **_kwargs) -> None:
        return None

    def grid(self, *_args, **_kwargs) -> None:
        return None

    def tick_params(self, *_args, **_kwargs) -> None:
        return None

    def scatter(self, x, y, **kwargs) -> None:
        self.scatter_calls.append((x, y, kwargs.get("marker", "")))

    def text(self, x, y, value, **_kwargs) -> None:
        self.text_calls.append((x, y, value))

    def set_title(self, title: str) -> None:
        self.title = title

    def get_figure(self):
        return self.figure

    def set_xlim(self, *_args, **_kwargs) -> None:
        return None

    def set_ylim(self, *_args, **_kwargs) -> None:
        return None


def test_plot_square_map_basic_rendering_with_markers_and_colorbar() -> None:
    """Plot helper should draw markers, text labels, title and colorbar."""
    figure = FakeFigure()
    axis = FakeAxis(figure)
    smap = SquareMap([[1.0, 2.0], [3.0, 4.0]])

    returned = plot_square_map(
        axis,
        smap,
        start=Coordinate(0, 0),
        target=Coordinate(1, 1),
        colorbar=True,
        cost=5.5,
        numtiles=True,
        empty_tiles={Coordinate(0, 1)},
    )

    assert returned is axis
    assert len(axis.scatter_calls) == 2
    assert axis.title == "Cost: 5.5000"
    assert figure.colorbar_calls == 1

    # One tile is empty and two are markers, so only one text annotation remains.
    assert len(axis.text_calls) == 1


def test_plot_square_map_validates_bounds_and_figure_for_colorbar() -> None:
    """Plot helper should validate marker coordinates and colorbar requirements."""
    axis = FakeAxis(FakeFigure())
    smap = SquareMap([[1.0, 2.0], [3.0, 4.0]])

    with pytest.raises(ValueError):
        plot_square_map(axis, smap, start=Coordinate(8, 8))
    with pytest.raises(ValueError):
        plot_square_map(axis, smap, target=Coordinate(-1, 0))

    with pytest.raises(RuntimeError):
        plot_square_map(FakeAxis(None), smap, colorbar=True)
