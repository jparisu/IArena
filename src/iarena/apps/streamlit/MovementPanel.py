"""Declares the streamlit movement panel used by the streamlit application."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from iarena.gaming.Movement import Movement


class MovementPanel:
    """Streamlit panel dedicated to movement interaction widgets.

    Purpose:
        Render movement interaction controls and capture selected movements.
    How it works:
        Creates one button per movement when interaction is enabled.
    Used for:
        Manual move selection in streamlit gameplay flows.
    Public Attributes:
        None declared at class level in this base definition.
    """

    def render_possible_movements(
        self,
        movements: Sequence[Movement],
        *,
        interactive: bool,
        key_prefix: str = "streamlit_movement",
    ) -> Movement | None:
        """Render possible movements and return one selected movement.

        Args:
            movements: Ordered movement options to display.
            interactive: Whether movement buttons should be clickable.
            key_prefix: Prefix used for streamlit widget keys.

        Returns:
            Movement | None: Selected movement when one button is clicked.
        """
        import streamlit as st

        if not movements:
            st.info("No legal movements available.")
            return None

        selected: Movement | None = None
        for movement_index, movement in enumerate(movements):
            clicked = st.button(
                label=str(movement),
                key=f"{key_prefix}_{movement_index}",
                disabled=not interactive,
                use_container_width=True,
            )
            if clicked:
                selected = movement
        return selected

    def render_selected_movement(self, movement: Movement | None) -> None:
        """Render a read-only selected movement line.

        Args:
            movement: Movement to display as selected for the reviewed step.

        Returns:
            None.
        """
        import streamlit as st

        if movement is None:
            st.write("Selected movement: -")
            return
        st.write(f"Selected movement: {movement}")
