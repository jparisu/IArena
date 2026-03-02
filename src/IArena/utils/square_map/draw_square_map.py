from __future__ import annotations

from typing import Optional, Set, Tuple
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.axes import Axes

from IArena.utils.square_map.SquareMap import Coordinate, SquareMap


def plot_square_map(
    axis: Axes,
    square_map: SquareMap,
    *,
    start: Optional[Coordinate] = None,
    target: Optional[Coordinate] = None,
    colorbar: bool = False,
    cost: Optional[float] = None,
    numtiles: bool = True,
    empty_tiles: Optional[Set[Coordinate]] = None,
    colortheme: str = "viridis",
) -> Axes:
    """
    Draw a square/cost map on the given matplotlib axis as a colormap.

    Parameters
    ----------
    axis:
        Matplotlib axis to draw on.
    square_map:
        2D matrix (n x m) of float values.
    start:
        Optional (row, col). Drawn as green circle.
    target:
        Optional (row, col). Drawn as red X.
    colorbar:
        If True, add a colorbar to the plot.
    cost:
        If provided, shown in the plot title.
    numtiles:
        If True, print tile values in the bottom-right corner of each tile.
    empty_tiles:
        Optional set of (row, col). Those tiles are displayed as special (only for plotting).
    colortheme:
        Matplotlib colormap name (e.g., "viridis", "plasma", "inferno", "magma", ...).

    Notes
    -----
    - This function does NOT mutate the input `square_map`. If `dug_tiles` is provided,
      a copy is used for display.
    - Coordinateinates are interpreted as (row, col) and plotted centered in each cell.
    """
    n, m = square_map.size()

    matrix = square_map.map_

    # Copy to avoid mutating the original
    if isinstance(matrix, np.matrix):
        data = np.array(matrix, dtype=float, copy=True)
    else:
        data = np.array(matrix, dtype=float)

    # Apply dug tiles (display only)
    if empty_tiles:
        for (r, c) in empty_tiles:
            if 0 <= r < n and 0 <= c < m:
                data[r, c] = 0.0

    # Draw colormap (use origin='upper' to match matrix indexing)
    im = axis.imshow(data, cmap=colortheme, origin="upper", interpolation="nearest")

    # Gridlines to emphasize tiles
    axis.set_xticks(np.arange(-0.5, m, 1), minor=True)
    axis.set_yticks(np.arange(-0.5, n, 1), minor=True)
    axis.grid(which="minor", linestyle="-", linewidth=0.5)
    axis.tick_params(which="both", bottom=False, left=False, labelbottom=False, labelleft=False)

    # Optional markers
    def _validate_Coordinate(c: Coordinate, name: str) -> None:
        r, col = c
        if not (0 <= r < n and 0 <= col < m):
            raise ValueError(f"{name} must be inside the map. Got {c} for shape ({n}, {m}).")

    if start is not None:
        _validate_Coordinate(start, "start")
        sr, sc = start
        axis.scatter(
            [sc],
            [sr],
            s=180,
            marker="o",
            facecolors="none",
            edgecolors="green",
            linewidths=2.5,
            zorder=5,
        )

    if target is not None:
        _validate_Coordinate(target, "target")
        tr, tc = target
        axis.scatter(
            [tc],
            [tr],
            s=200,
            marker="x",
            c="red",
            linewidths=3.0,
            zorder=6,
        )

    # Add numbers on tiles
    if numtiles:
        # Slight offset to bottom-right of the cell
        dx, dy = 0.35, 0.35
        for r in range(n):
            for c in range(m):

                # Do not draw on start/target/empty_tiles
                if Coordinate(r,c) == start or Coordinate(r,c) == target or (empty_tiles and Coordinate(r,c) in empty_tiles):
                    continue

                axis.text(
                    c + dx,
                    r + dy,
                    f"{data[r, c]:.2f}",
                    ha="right",
                    va="bottom",
                    fontsize=7,
                    zorder=10,
                )

    # Title with cost
    if cost is not None:
        axis.set_title(f"Cost: {cost:.4f}")

    # Colorbar
    if colorbar:
        # Attach colorbar to the specific axis (important when using subplots)
        fig = axis.get_figure()
        fig.colorbar(im, ax=axis, fraction=0.046, pad=0.04)

    # Tight bounds
    axis.set_xlim(-0.5, m - 0.5)
    axis.set_ylim(n - 0.5, -0.5)  # keep origin='upper' visual orientation

    return axis
