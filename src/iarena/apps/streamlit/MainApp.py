"""Declares the main streamlit layout holder wiring all streamlit UI panels."""

from __future__ import annotations

from typing import Any

from iarena.visualizing.streamlit_frontend.StreamlitContainer import StreamlitContainer

from .ConfigurationPanel import ConfigurationPanel
from .MovementPanel import MovementPanel
from .StatePanel import StatePanel


class MainApp:
    """Main streamlit layout holder wiring all UI panels together.

    Purpose:
        Group and expose the panel components used by `StreamlitApplication`.
    How it works:
        Holds one configuration panel, one movement panel, and one state panel,
        and can build the central layout containers.
    Used for:
        Consistent streamlit page composition across reruns.
    Public Attributes:
        left_column (ConfigurationPanel): Sidebar configuration panel.
        right_column (MovementPanel): Movement and score panel.
        central (StatePanel): Main position-rendering panel.
    """

    left_column: ConfigurationPanel
    right_column: MovementPanel
    central: StatePanel

    def __init__(self) -> None:
        """Initialize panel objects for one streamlit application instance.

        Args:
            None.

        Returns:
            None.
        """
        self.left_column = ConfigurationPanel()
        self.right_column = MovementPanel()
        self.central = StatePanel()

    def build_layout(self) -> dict[str, StreamlitContainer | Any]:
        """Build and return the primary page containers.

        Args:
            None.

        Returns:
            dict[str, StreamlitContainer | Any]: Mapping containing wrapped
            `position`, `movements`, and `score` containers plus raw slider host.
        """
        import streamlit as st

        center_column, right_column = st.columns([3, 2], gap="large")
        position = StreamlitContainer(center_column.container(border=True))

        right_column.markdown("### Movements")
        movements = StreamlitContainer(right_column.container(border=True))

        right_column.markdown("### Score")
        score = StreamlitContainer(right_column.container(border=True))

        slider = st.container(border=False)
        return {
            "position": position,
            "movements": movements,
            "score": score,
            "slider": slider,
        }
