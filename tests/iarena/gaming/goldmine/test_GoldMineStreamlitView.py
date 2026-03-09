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
