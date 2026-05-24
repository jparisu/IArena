"""Declares the streamlit state panel used by the streamlit application."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from iarena.gaming.Position import Position
    from iarena.visualizing.streamlit_frontend.StreamlitContainer import StreamlitContainer
    from iarena.visualizing.streamlit_frontend.StreamlitView import StreamlitView


class StatePanel:
    """Streamlit panel dedicated to current game state rendering.

    Purpose:
        Encapsulate position rendering on the central streamlit panel.
    How it works:
        Delegates rendering to the selected game streamlit view.
    Used for:
        Displaying the currently selected position during live play and review.
    Public Attributes:
        None declared at class level in this base definition.
    """

    def render_position(self, view: StreamlitView, position: Position, canvas: StreamlitContainer) -> None:
        """Render the provided position using the game streamlit view.

        Args:
            view: Streamlit renderer selected for the active game.
            position: Position object to render.
            canvas: Streamlit container wrapper for state rendering.

        Returns:
            None.
        """
        view.render_position(position, canvas)
