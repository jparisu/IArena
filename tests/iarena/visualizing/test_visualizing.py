"""Tests for visualization base classes and frontend default behaviors."""

from __future__ import annotations

import pytest

from iarena.gaming.Movement import Movement
from iarena.visualizing.EmptyView import EmptyView
from iarena.visualizing.streamlit_frontend.StreamlitContainer import StreamlitContainer
from iarena.visualizing.streamlit_frontend.StreamlitSession import StreamlitSession
from iarena.visualizing.streamlit_frontend.StreamlitView import StreamlitView
from iarena.visualizing.terminal_frontend.TerminalView import TerminalView


class _DummyMovement(Movement):
    """Simple concrete movement for tests."""


class _DummyTerminalView(TerminalView):
    """Concrete terminal view used to test default terminal rendering."""

    def __init__(self) -> None:
        self.outputs: list[str] = []
        self.output_fnc = self.outputs.append

    def get_str_info(self, rules: object) -> str:
        _ = rules
        return "info-text"

    def get_str_state(self, position: object) -> str:
        _ = position
        return "state-text"

    def capture_input(self, input: str) -> Movement:
        _ = input
        return _DummyMovement()


class _DummyStreamlitView(StreamlitView):
    """Concrete streamlit view used to test default streamlit state rendering."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, object, StreamlitContainer]] = []

    def render_info(self, rules: object, canvas: object) -> None:
        _ = rules
        _ = canvas

    def render_position(self, position: object, canvas: StreamlitContainer) -> None:
        self.calls.append(("position", position, canvas))

    def render_movements(self, position: object, canvas: StreamlitContainer) -> None:
        self.calls.append(("movements", position, canvas))

    def render_score(self, position: object, canvas: StreamlitContainer) -> None:
        self.calls.append(("score", position, canvas))

    def capture_input(self, state: object) -> Movement:
        _ = state
        return _DummyMovement()


class _CanvasBundle:
    """Simple container bundle matching expected streamlit section attributes."""

    def __init__(self, position: StreamlitContainer, movements: StreamlitContainer, score: StreamlitContainer) -> None:
        self.position = position
        self.movements = movements
        self.score = score


def test_empty_view_render_methods_are_noop() -> None:
    """`EmptyView` rendering methods should accept calls and do nothing."""
    view = EmptyView()
    view.render_info(rules=object(), canvas=object())
    view.render_state(pos=object(), canvas=object())


def test_empty_view_capture_input_raises_runtime_error() -> None:
    """`EmptyView.capture_input` should reject interactive usage."""
    view = EmptyView()
    with pytest.raises(RuntimeError, match="does not support input capture"):
        view.capture_input("any")


def test_terminal_view_default_rendering_emits_text() -> None:
    """`TerminalView` default rendering should send formatted text to output."""
    view = _DummyTerminalView()
    view.render_info(rules=object(), canvas=object())
    view.render_state(pos=object(), canvas=object())
    assert view.outputs == ["info-text", "state-text"]


def test_streamlit_view_render_state_accepts_single_container() -> None:
    """`StreamlitView.render_state` should reuse a single container for all sections."""
    view = _DummyStreamlitView()
    container = StreamlitContainer()
    position = object()

    view.render_state(position, container)

    assert [name for name, _, _ in view.calls] == ["position", "movements", "score"]
    assert all(canvas is container for _, _, canvas in view.calls)


def test_streamlit_view_render_state_accepts_mapping_canvas() -> None:
    """`StreamlitView.render_state` should resolve the three section canvases from a mapping."""
    view = _DummyStreamlitView()
    position_canvas = StreamlitContainer()
    movement_canvas = StreamlitContainer()
    score_canvas = StreamlitContainer()
    position = object()

    view.render_state(
        position,
        {
            "position": position_canvas,
            "movements": movement_canvas,
            "score": score_canvas,
        },
    )

    assert view.calls[0] == ("position", position, position_canvas)
    assert view.calls[1] == ("movements", position, movement_canvas)
    assert view.calls[2] == ("score", position, score_canvas)


def test_streamlit_view_render_state_accepts_attribute_bundle() -> None:
    """`StreamlitView.render_state` should resolve section canvases from object attributes."""
    view = _DummyStreamlitView()
    position_canvas = StreamlitContainer()
    movement_canvas = StreamlitContainer()
    score_canvas = StreamlitContainer()
    position = object()
    bundle = _CanvasBundle(position_canvas, movement_canvas, score_canvas)

    view.render_state(position, bundle)

    assert view.calls[0] == ("position", position, position_canvas)
    assert view.calls[1] == ("movements", position, movement_canvas)
    assert view.calls[2] == ("score", position, score_canvas)


def test_streamlit_view_render_state_rejects_invalid_canvas() -> None:
    """`StreamlitView.render_state` should raise for unsupported canvas formats."""
    view = _DummyStreamlitView()
    with pytest.raises(TypeError, match="Invalid streamlit canvas section"):
        view.render_state(object(), object())


def test_streamlit_container_delegates_write_calls_to_wrapped_container() -> None:
    class _Wrapped:
        def __init__(self) -> None:
            self.payloads: list[object] = []

        def write(self, payload: object) -> None:
            self.payloads.append(payload)

    wrapped = _Wrapped()
    container = StreamlitContainer(wrapped)

    container.write("hello")

    assert wrapped.payloads == ["hello"]


def test_streamlit_session_behaves_like_mapping_and_attribute_container() -> None:
    session = StreamlitSession({"from_peg": 0})
    session.set("to_peg", 2)

    assert session["from_peg"] == 0
    assert session.to_peg == 2
    assert session.pop("to_peg") == 2
    assert "to_peg" not in session
