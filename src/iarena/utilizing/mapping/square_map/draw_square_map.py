from __future__ import annotations

from collections.abc import Iterable

import numpy as np
from matplotlib.axes import Axes

from iarena.utilizing.mapping.square_map.SquareMap import SquareMap
from iarena.utilizing.mapping.square_map.SquareMapCoordinate import SquareMapCoordinate


def plot_square_map(
    axis: Axes,
    square_map: SquareMap,
    *,
    start: SquareMapCoordinate | None = None,
    target: SquareMapCoordinate | None = None,
    colorbar: bool = False,
    cost: float | None = None,
    numtiles: bool = True,
    empty_tiles: Iterable[SquareMapCoordinate | tuple[int, int]] | None = None,
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
    - SquareMapCoordinateinates are interpreted as (row, col) and plotted centered in each cell.
    """
    n, m = square_map.size()

    matrix = square_map.to_numpy(dtype=float)

    # Copy to avoid mutating the original
    if isinstance(matrix, np.matrix):
        data = np.array(matrix, dtype=float, copy=True)
    else:
        data = np.array(matrix, dtype=float)

    # Apply dug tiles (display only)
    normalized_empty_tiles: set[tuple[int, int]] = set()
    if empty_tiles:
        for tile in empty_tiles:
            if isinstance(tile, SquareMapCoordinate):
                r, c = tile.as_tuple()
            else:
                r, c = int(tile[0]), int(tile[1])
            if 0 <= r < n and 0 <= c < m:
                normalized_empty_tiles.add((r, c))
                data[r, c] = 0.0

    # Draw colormap (use origin='upper' to match matrix indexing)
    im = axis.imshow(data, cmap=colortheme, origin="upper", interpolation="nearest")

    # Gridlines to emphasize tiles
    axis.set_xticks(np.arange(-0.5, m, 1), minor=True)
    axis.set_yticks(np.arange(-0.5, n, 1), minor=True)
    axis.grid(which="minor", linestyle="-", linewidth=0.5)
    axis.tick_params(which="both", bottom=False, left=False, labelbottom=False, labelleft=False)

    # Optional markers
    def _validate_SquareMapCoordinate(c: SquareMapCoordinate, name: str) -> None:
        r, col = c
        if not (0 <= r < n and 0 <= col < m):
            raise ValueError(f"{name} must be inside the map. Got {c} for shape ({n}, {m}).")

    if start is not None:
        _validate_SquareMapCoordinate(start, "start")
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
        _validate_SquareMapCoordinate(target, "target")
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
                is_start = start is not None and (r, c) == start.as_tuple()
                is_target = target is not None and (r, c) == target.as_tuple()
                is_empty = (r, c) in normalized_empty_tiles
                if is_start or is_target or is_empty:
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


def generate_plot_map(
    square_map: SquareMap,
    *,
    start: SquareMapCoordinate | None = None,
    target: SquareMapCoordinate | None = None,
    colorbar: bool = False,
    cost: float | None = None,
    numtiles: bool = True,
    empty_tiles: Iterable[SquareMapCoordinate | tuple[int, int]] | None = None,
    colortheme: str = "viridis",
) -> Axes:
    """Convenience wrapper around plot_square_map that creates a new figure and axis."""
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(6, 6))
    plot_square_map(
        axis=ax,
        square_map=square_map,
        start=start,
        target=target,
        colorbar=colorbar,
        cost=cost,
        numtiles=numtiles,
        empty_tiles=empty_tiles,
        colortheme=colortheme,
    )

    return fig
