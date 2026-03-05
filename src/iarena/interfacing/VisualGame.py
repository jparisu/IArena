"""Protocol definitions for game-specific visual UI integration."""

from __future__ import annotations

from collections.abc import Mapping
from enum import Enum
from typing import Any, Protocol, runtime_checkable


class VisualGameState(str, Enum):
    """Enumerate Streamlit UI lifecycle states for visual games."""

    CONFIGURING = "CONFIGURING"
    PLAYING = "PLAYING"
    REVIEWING = "REVIEWING"


@runtime_checkable
class VisualGame(Protocol):
    """Protocol for games that provide visual UI callbacks."""

    def visual_configuration(self, container: Any) -> Mapping[str, object]:
        """Render game-specific configuration controls.

        Args:
            container: Streamlit-like container where controls are rendered.

        Returns:
            Mapping with validated configuration values.
        """
        raise NotImplementedError

    def visual_description(self, container: Any, configuration: Mapping[str, object]) -> None:
        """Render game description during configuration mode.

        Args:
            container: Streamlit-like container where description is rendered.
            configuration: Current game configuration mapping.

        Returns:
            None.
        """
        raise NotImplementedError

    def visual_position(self, container: Any, view_state: Any) -> None:
        """Render game position during playing/reviewing modes.

        Args:
            container: Streamlit-like container for rendering.
            view_state: Frame/view object with game state details.

        Returns:
            None.
        """
        raise NotImplementedError

    def visual_movements(self, container: Any, view_state: Any, state: VisualGameState) -> None:
        """Render movement panel details for one UI state.

        Args:
            container: Streamlit-like container for rendering.
            view_state: Frame/view object with game state details.
            state: Current visual UI state.

        Returns:
            None.
        """
        raise NotImplementedError

    def visual_scoreboard(self, container: Any, view_state: Any) -> None:
        """Render scoreboard details in the movement panel.

        Args:
            container: Streamlit-like container for rendering.
            view_state: Frame/view object with game state details.

        Returns:
            None.
        """
        raise NotImplementedError
