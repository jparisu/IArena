"""Tests for the GoldMine streamlit view implementation."""

from __future__ import annotations

from typing import Any

from iarena.gaming.goldmine.GoldMineConfiguration import GoldMineConfiguration
from iarena.gaming.goldmine.GoldMineRules import GoldMineRules
from iarena.gaming.goldmine.GoldMineStreamlitView import GoldMineStreamlitView
from iarena.visualizing.streamlit_frontend.StreamlitContainer import StreamlitContainer
from iarena.utilizing.mapping.square_map.SquareMapCoordinate import SquareMapCoordinate


class _RecordingCanvas:
    """Minimal streamlit-like container that records markdown payloads."""

    def __init__(self) -> None:
        """Initialize one empty payload recorder."""
        self.payloads: list[str] = []

    def markdown(self, message: str, **_: Any) -> None:
        """Record one markdown payload."""
        self.payloads.append(message)

    def write(self, message: object) -> None:
        """Record one generic payload."""
        self.payloads.append(str(message))


class _RecordingDebugCanvas:
    """Minimal streamlit-like canvas used to record pyplot calls."""

    def __init__(self) -> None:
        """Initialize one empty figure recorder."""
        self.figures: list[object] = []

    def pyplot(self, figure: object, **_: Any) -> None:
        """Record one matplotlib figure payload."""
        self.figures.append(figure)


class _RecordingExpander:
    """Context manager stub returned by one expander call."""

    def __init__(self, debug_canvas: _RecordingDebugCanvas) -> None:
        """Store the debug canvas yielded by this context manager."""
        self._debug_canvas = debug_canvas

    def __enter__(self) -> _RecordingDebugCanvas:
        """Yield the wrapped debug canvas."""
        return self._debug_canvas

    def __exit__(self, *_: object) -> None:
        """End the context manager without suppressing exceptions."""
        return None


class _RecordingNativeCanvas:
    """Minimal streamlit-like container exposing expander support."""

    def __init__(self) -> None:
        """Initialize expander invocation and debug payload recorders."""
        self.debug_canvas = _RecordingDebugCanvas()
        self.expanders: list[tuple[str, bool]] = []

    def expander(self, label: str, *, expanded: bool = False) -> _RecordingExpander:
        """Record one expander invocation and return one context manager stub."""
        self.expanders.append((label, expanded))
        return _RecordingExpander(self.debug_canvas)


def _rules() -> GoldMineRules:
    """Create one deterministic GoldMine ruleset with hints enabled."""
    return GoldMineRules(
        GoldMineConfiguration(
            n_rows=2,
            n_cols=2,
            start=SquareMapCoordinate(0, 0),
            target=SquareMapCoordinate(1, 1),
            map_data=[[0.0, 2.0], [3.0, 4.0]],
            heuristic_map_data=[[0.0, 0.1], [0.2, 0.3]],
            compass_activated=True,
            proximity_activated=True,
            density_activated=True,
        ),
    )


def test_render_position_displays_hint_panel_in_state_section() -> None:
    """`render_position` should include heuristic hints in the state section."""
    view = GoldMineStreamlitView()
    position = _rules().first_position()
    canvas = _RecordingCanvas()
    wrapped_canvas = StreamlitContainer(canvas)

    view.render_position(position, wrapped_canvas)

    combined_payload = "\n".join(canvas.payloads)
    assert "Heuristic Signals" in combined_payload
    assert "Compass" in combined_payload
    assert "Proximity" in combined_payload
    assert "Density" in combined_payload


def test_render_score_does_not_include_heuristic_hints() -> None:
    """`render_score` should keep hints out of the score section."""
    view = GoldMineStreamlitView()
    position = _rules().first_position()
    canvas = _RecordingCanvas()
    wrapped_canvas = StreamlitContainer(canvas)

    view.render_score(position, wrapped_canvas)

    combined_payload = "\n".join(canvas.payloads)
    assert "Position Score" in combined_payload
    assert "Compass hint" not in combined_payload
    assert "Proximity hint" not in combined_payload
    assert "Density hint" not in combined_payload


def test_render_position_adds_collapsed_debug_map_expander() -> None:
    """`render_position` should expose full map plot inside a collapsed expander."""
    view = GoldMineStreamlitView()
    position = _rules().first_position()
    native_canvas = _RecordingNativeCanvas()
    wrapped_canvas = StreamlitContainer(native_canvas)

    view.render_position(position, wrapped_canvas)

    assert native_canvas.expanders == [("Debug map (hidden information)", False)]
    assert len(native_canvas.debug_canvas.figures) == 1
