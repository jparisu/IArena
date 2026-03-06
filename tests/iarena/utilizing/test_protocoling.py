"""Tests for optional capability protocols."""

from __future__ import annotations

from iarena.utilizing.protocoling import (
    IPlotRenderable,
    ITextRenderable,
    as_text,
    supports_plotting,
    supports_text_rendering,
)


class TextRenderable:
    """Minimal text-renderable object for protocol checks."""

    def to_text(self) -> str:
        return "rendered"


class PlotRenderable:
    """Minimal plot-renderable object for protocol checks."""

    def plot(self, target=None):
        return ("plotted", target)


class PlainObject:
    """Object with only __str__ fallback."""

    def __str__(self) -> str:
        return "plain"


def test_runtime_protocols_and_capability_helpers() -> None:
    """Helpers should detect protocol support through runtime checks."""
    text = TextRenderable()
    plot = PlotRenderable()

    assert isinstance(text, ITextRenderable)
    assert isinstance(plot, IPlotRenderable)
    assert supports_text_rendering(text) is True
    assert supports_text_rendering(plot) is False
    assert supports_plotting(plot) is True
    assert supports_plotting(text) is False


def test_as_text_prefers_protocol_then_fallback() -> None:
    """`as_text` should dispatch to `to_text` when available."""
    assert as_text(TextRenderable()) == "rendered"
    assert as_text(PlainObject()) == "plain"
