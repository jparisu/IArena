from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, List, Optional, Sequence, Tuple, Any

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.widgets import Button, Slider

from IArena.interfaces.IPosition import IPosition
from IArena.interfaces.IGameRules import IGameRules


Coord = Tuple[int, int]


RenderFn = Callable[[Axes, IPosition], Any]
# You can pass a richer function, e.g. plot_square_map(axis, matrix, start=..., target=..., ...)


@dataclass
class MapViewerConfig:
    interval_ms: int = 300
    start: Optional[Coord] = None
    target: Optional[Coord] = None
    show_colorbar: bool = True
    show_numtiles: bool = False
    colortheme: str = "viridis"


class InteractiveViewer:
    """
    Matplotlib interactive viewer for a sequence of maps.

    Controls:
      - Play/Pause (timer-based)
      - Step back / Step forward
      - Slider to jump to any frame
      - Interval slider (ms) to adjust playback speed

    You provide:
      - a sequence of matrices
      - a render function that draws the current matrix on the axis
        (e.g. a lambda calling plot_square_map(...))
    """

    def __init__(
        self,
        rules: IGameRules,
        positions: List[IPosition],
        *,
        config: Optional[MapViewerConfig] = None,
    ) -> None:
        if len(positions) == 0:
            raise ValueError("positions sequence is empty.")

        self.positions = positions
        self.rules = rules
        self.config = config if config is not None else MapViewerConfig()

        self.idx = 0
        self.playing = False

        self.fig: Figure
        self.ax: Axes

        # Matplotlib timer (created later when fig exists)
        self._timer = None

        # Widgets
        self._btn_play = None
        self._btn_prev = None
        self._btn_next = None
        self._slider_frame = None
        self._slider_interval = None

    def show(self) -> None:
        self._build_ui()
        self._draw_current()
        plt.show()

    # ---------------- UI building ----------------

    def _build_ui(self) -> None:
        self.fig, self.ax = plt.subplots(figsize=(7, 7))
        self.fig.canvas.manager.set_window_title(self.title)
        plt.subplots_adjust(bottom=0.22)  # space for widgets

        # --- Buttons ---
        ax_prev = self.fig.add_axes([0.10, 0.08, 0.12, 0.06])
        ax_play = self.fig.add_axes([0.24, 0.08, 0.12, 0.06])
        ax_next = self.fig.add_axes([0.38, 0.08, 0.12, 0.06])

        self._btn_prev = Button(ax_prev, "⟵ Prev")
        self._btn_play = Button(ax_play, "▶ Play")
        self._btn_next = Button(ax_next, "Next ⟶")

        self._btn_prev.on_clicked(self._on_prev)
        self._btn_play.on_clicked(self._on_play_pause)
        self._btn_next.on_clicked(self._on_next)

        # --- Frame slider ---
        ax_slider_frame = self.fig.add_axes([0.10, 0.15, 0.75, 0.03])
        self._slider_frame = Slider(
            ax=ax_slider_frame,
            label="Frame",
            valmin=0,
            valmax=len(self.positions) - 1,
            valinit=self.idx,
            valstep=1,
        )
        self._slider_frame.on_changed(self._on_slider_frame)

        # --- Interval slider (ms) ---
        ax_slider_interval = self.fig.add_axes([0.60, 0.08, 0.25, 0.03])
        self._slider_interval = Slider(
            ax=ax_slider_interval,
            label="ms",
            valmin=50,
            valmax=2000,
            valinit=self.config.interval_ms,
            valstep=10,
        )
        self._slider_interval.on_changed(self._on_slider_interval)

        # --- Timer ---
        self._timer = self.fig.canvas.new_timer(interval=self.config.interval_ms)
        self._timer.add_callback(self._on_tick)

    # ---------------- Rendering ----------------

    def _draw_current(self) -> None:
        self.ax.clear()
        self.rules.plot_step()
        self.fig.canvas.draw_idle()

    # ---------------- Playback logic ----------------

    def _set_index(self, new_idx: int, update_slider: bool = True) -> None:
        new_idx = int(np.clip(new_idx, 0, len(self.maps) - 1))
        if new_idx == self.idx:
            return

        self.idx = new_idx

        if update_slider and self._slider_frame is not None:
            # avoid recursive callbacks by temporarily disconnecting if needed
            self._slider_frame.set_val(self.idx)

        self._draw_current()

    def _on_tick(self) -> None:
        if not self.playing:
            return
        if self.idx >= len(self.maps) - 1:
            self.playing = False
            self._update_play_button()
            return
        self._set_index(self.idx + 1, update_slider=True)

    # ---------------- Widget callbacks ----------------

    def _on_prev(self, _event) -> None:
        self.playing = False
        self._update_play_button()
        self._set_index(self.idx - 1, update_slider=True)

    def _on_next(self, _event) -> None:
        self.playing = False
        self._update_play_button()
        self._set_index(self.idx + 1, update_slider=True)

    def _on_play_pause(self, _event) -> None:
        self.playing = not self.playing
        self._update_play_button()
        if self.playing:
            self._timer.start()
        else:
            self._timer.stop()

    def _on_slider_frame(self, val: float) -> None:
        self.playing = False
        self._update_play_button()
        self._set_index(int(val), update_slider=False)

    def _on_slider_interval(self, val: float) -> None:
        self.config.interval_ms = int(val)
        if self._timer is not None:
            self._timer.interval = self.config.interval_ms

    def _update_play_button(self) -> None:
        if self._btn_play is None:
            return
        self._btn_play.label.set_text("⏸ Pause" if self.playing else "▶ Play")


# ---------------- Example wiring with plot_square_map ----------------
# This assumes you already have your plot_square_map(axis, square_map, ...) defined.

def build_render_fn(
    *,
    start: Optional[Coord] = None,
    target: Optional[Coord] = None,
    show_colorbar: bool = True,
    show_numtiles: bool = False,
    colortheme: str = "viridis",
    dug_tiles_per_frame: Optional[Sequence[set[Coord]]] = None,
) -> Callable[[Axes, np.ndarray, int], None]:
    """
    Create a renderer compatible with InteractiveMapViewer.
    You can adapt this to your own metadata per frame.
    """
    def _render(ax: Axes, matrix: np.ndarray, idx: int) -> None:
        dug = None
        if dug_tiles_per_frame is not None and idx < len(dug_tiles_per_frame):
            dug = dug_tiles_per_frame[idx]

        plot_square_map(
            ax,
            matrix,
            start=start,
            target=target,
            colorbar=show_colorbar,
            cost=float(idx),  # example: title uses idx; replace with your own cost
            numtiles=show_numtiles,
            dug_tiles=dug,
            colortheme=colortheme,
        )

    return _render
