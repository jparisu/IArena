"""Protocol for games that provide Streamlit-oriented interaction methods."""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from iarena.desining.gaming.GameConfiguration import GameConfiguration
from iarena.desining.gaming.Movement import Movement
from iarena.desining.gaming.Position import Position


@runtime_checkable
class StreamlitGame(Protocol):
    """Game capability interface for Streamlit visualization and interaction."""

    def streamlit_instructions(self, streamlit_container: Any) -> None:
        """Render game instructions in a Streamlit container.

        Args:
            streamlit_container: Streamlit container used to render content.

        Returns:
            None.
        """
        raise NotImplementedError

    def render_streamlit_position(self, position: Position, streamlit_container: Any) -> None:
        """Render one game position in a Streamlit container.

        Args:
            position: Position to render.
            streamlit_container: Streamlit container used to render content.

        Returns:
            None.
        """
        raise NotImplementedError

    def render_streamlit_configuration(self, streamlit_container: Any) -> GameConfiguration:
        """Render Streamlit controls and return selected game configuration.

        Args:
            streamlit_container: Streamlit container used to render controls.

        Returns:
            Configuration object selected in the UI.
        """
        raise NotImplementedError

    def select_streamlit_movement(self, position: Position, streamlit_container: Any) -> Movement:
        """Render movement controls and return selected movement.

        Args:
            position: Current game position.
            streamlit_container: Streamlit container used to render controls.

        Returns:
            Movement selected by the user.
        """
        raise NotImplementedError
