"""Abstract base class for Streamlit-specific game views."""

from __future__ import annotations

from abc import abstractmethod

from iarena.game.GameMove import GameMove
from iarena.view.View import View


class StreamlitView(View):
    """View specialisation for Streamlit interfaces.

    Extends View with a move-extraction hook suited to Streamlit's
    reactive model: instead of blocking on input, the view renders
    clickable widgets that store the chosen move in ``st.session_state``,
    and ``pop_pending_move`` retrieves and clears it on the next rerun.
    """

    @abstractmethod
    def pop_pending_move(self) -> GameMove | None:
        """Return and clear the pending move from session state, if any.

        Returns
        -------
        GameMove | None
            The move stored by the last widget interaction, or None if
            no move is pending.
        """
