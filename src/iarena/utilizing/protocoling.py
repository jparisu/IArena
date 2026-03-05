"""Generic opt-in protocols and helpers not tied to a specific interface."""

from __future__ import annotations

from typing import Any, Protocol, TypeGuard, runtime_checkable


@runtime_checkable
class ITextRenderable(Protocol):
    """Opt-in capability for terminal-friendly textual rendering."""

    def to_text(self) -> str:
        """Render this object as plain text."""
        ...


@runtime_checkable
class IPlotRenderable(Protocol):
    """Opt-in capability for graphical rendering.

    The `target` parameter can be any backend object, such as a matplotlib
    axis or a Streamlit container.
    """

    def plot(self, target: Any | None = None) -> Any:
        """Draw this object on an optional backend-specific target."""
        ...


def supports_text_rendering(value: object) -> TypeGuard[ITextRenderable]:
    """Return whether `value` exposes `ITextRenderable` capability."""
    return isinstance(value, ITextRenderable)


def supports_plotting(value: object) -> TypeGuard[IPlotRenderable]:
    """Return whether `value` exposes `IPlotRenderable` capability."""
    return isinstance(value, IPlotRenderable)


def as_text(value: object) -> str:
    """Render objects as text with capability-aware fallback.

    If `value` implements `ITextRenderable`, this method delegates to
    `to_text`; otherwise it falls back to `str(value)`.
    """
    if supports_text_rendering(value):
        return value.to_text()
    return str(value)
