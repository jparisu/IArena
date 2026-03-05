"""Matplotlib rendering helpers for :mod:`iarena` square maps."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from iarena.utilizing.square_map.SquareMap import Coordinate, SquareMap

if TYPE_CHECKING:
    from matplotlib.axes import Axes


# pylint: disable=too-complex
def plot_square_map(
    axis: Axes,
    square_map: SquareMap[float],
    *,
    start: Coordinate | None = None,
    target: Coordinate | None = None,
    colorbar: bool = False,
    cost: float | None = None,
    numtiles: bool = True,
    empty_tiles: set[Coordinate] | None = None,
    colortheme: str = "viridis",
) -> Axes:
    """Render a numeric square map onto an existing matplotlib axis.

    Args:
        axis: Axis where rendering is performed.
        square_map: Source grid with numeric values.
        start: Optional start coordinate, shown with a green circle.
        target: Optional target coordinate, shown with a red cross.
        colorbar: Whether to attach a colorbar to the axis.
        cost: Optional total cost displayed in title.
        numtiles: Whether to write cell values on each tile.
        empty_tiles: Optional set of coordinates rendered as zero.
        colortheme: Matplotlib colormap name.

    Returns:
        The same axis after drawing.

    Raises:
        ValueError: If `start` or `target` are outside map bounds.
        RuntimeError: If colorbar is requested and axis has no figure.
    """

    n_rows, n_cols = square_map.size()
    data = square_map.to_numpy(dtype=float)

    if empty_tiles:
        for coordinate in empty_tiles:
            row, col = coordinate
            if 0 <= row < n_rows and 0 <= col < n_cols:
                data[row, col] = 0.0

    # origin='upper' keeps matrix-style orientation (row 0 at top).
    image = axis.imshow(data, cmap=colortheme, origin="upper", interpolation="nearest")

    axis.set_xticks(np.arange(-0.5, n_cols, 1), minor=True)
    axis.set_yticks(np.arange(-0.5, n_rows, 1), minor=True)
    axis.grid(which="minor", linestyle="-", linewidth=0.5)
    axis.tick_params(which="both", bottom=False, left=False, labelbottom=False, labelleft=False)

    def _validate_coordinate(coord: Coordinate, name: str) -> None:
        """Ensure a marker coordinate is inside current map bounds.

        Args:
            coord: Coordinate to validate.
            name: Human-readable label for error messages.

        Returns:
            `None`.
        """

        row, col = coord
        if not (0 <= row < n_rows and 0 <= col < n_cols):
            raise ValueError(f"{name} must be inside map bounds ({n_rows}, {n_cols}), got {coord}")

    if start is not None:
        _validate_coordinate(start, "start")
        row, col = start
        axis.scatter(
            [col],
            [row],
            s=180,
            marker="o",
            facecolors="none",
            edgecolors="green",
            linewidths=2.5,
            zorder=5,
        )

    if target is not None:
        _validate_coordinate(target, "target")
        row, col = target
        axis.scatter(
            [col],
            [row],
            s=200,
            marker="x",
            c="red",
            linewidths=3.0,
            zorder=6,
        )

    if numtiles:
        # Offset text to keep markers readable at the cell center.
        dx, dy = 0.35, 0.35
        for row in range(n_rows):
            for col in range(n_cols):
                current = Coordinate(row, col)
                if current == start or current == target or (empty_tiles and current in empty_tiles):
                    continue
                axis.text(
                    col + dx,
                    row + dy,
                    f"{data[row, col]:.2f}",
                    ha="right",
                    va="bottom",
                    fontsize=7,
                    zorder=10,
                )

    if cost is not None:
        axis.set_title(f"Cost: {cost:.4f}")

    if colorbar:
        figure = axis.get_figure()
        if figure is None:
            raise RuntimeError("axis is not attached to a matplotlib figure")
        figure.colorbar(image, ax=axis, fraction=0.046, pad=0.04)

    axis.set_xlim(-0.5, n_cols - 0.5)
    axis.set_ylim(n_rows - 0.5, -0.5)
    return axis
