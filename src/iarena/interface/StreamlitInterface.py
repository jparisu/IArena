"""Streamlit implementation of the game Interface."""

from __future__ import annotations

import streamlit as st

from iarena.interface.Interface import Interface
from iarena.view.View import View


class StreamlitInterface(Interface):
    """Interface that routes output to Streamlit widgets.

    ``render`` writes text via ``st.write``.  ``ask`` is not supported
    because Streamlit's reactive model drives input through widget
    callbacks and ``st.session_state`` rather than blocking calls.

    Parameters
    ----------
    view:
        Optional game-specific view used by ``on_turn_start``.
    """

    def __init__(self, view: View | None = None) -> None:
        super().__init__(view)

    def render(self, content: str) -> None:
        """Write content to the Streamlit page.

        Parameters
        ----------
        content:
            The string to display.
        """
        st.write(content)

    def ask(self, prompt: str) -> str:
        """Not supported — Streamlit uses widget callbacks for input.

        Raises
        ------
        NotImplementedError
            Always.
        """
        raise NotImplementedError(
            "StreamlitInterface does not support blocking ask(). "
            "Use widget callbacks and st.session_state instead."
        )
