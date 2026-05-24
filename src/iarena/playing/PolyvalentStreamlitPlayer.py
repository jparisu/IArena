"""Defines a generic streamlit human player implementation."""

from __future__ import annotations

from iarena.playing.StreamlitPlayer import StreamlitPlayer


class PolyvalentStreamlitPlayer(StreamlitPlayer):
    """Generic streamlit human player driven by the bound streamlit view parser.

    Purpose:
        Provides one reusable streamlit human-player class for games exposing a
        `StreamlitView.capture_input` implementation.
    How it works:
        Inherits generic streamlit interaction logic from `StreamlitPlayer`.
    Used for:
        Browser-based human interaction without per-game player boilerplate.
    Public Attributes:
        Inherits streamlit runtime attributes from `StreamlitPlayer`.
    """

    def name(self) -> str:
        """Return a stable identifier for this streamlit player type.

        Returns:
            str: Canonical streamlit-player identifier.
        """
        return "polyvalent-streamlit"
