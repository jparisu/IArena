"""Declares the abstract streamlit human-player type that interacts through a streamlit view."""

from __future__ import annotations

from abc import ABC
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any

from iarena.gaming.Movement import Movement
from iarena.playing.HumanPlayer import HumanPlayer
from iarena.visualizing.streamlit_frontend.StreamlitSession import StreamlitSession

if TYPE_CHECKING:
    from iarena.gaming.Position import Position
    from iarena.gaming.Rules import Rules
    from iarena.playing.PlayerIndex import PlayerIndex


class StreamlitPlayer(HumanPlayer, ABC):
    """Abstract human player that consumes interaction state from streamlit sessions.

    Purpose:
        Defines the reusable human-player behavior expected by streamlit-based
        applications.
    How it works:
        Stores a session-state wrapper and delegates movement parsing to the
        bound streamlit view through `capture_input`.
    Used for:
        Building concrete streamlit-interactive human players for any game.
    Public Attributes:
        render: Streamlit-compatible view used to capture user input.
    """

    def __init__(self, name: str | None = None) -> None:
        """Initialize the player with an optional name.

        Args:
            name (str | None): Optional name for the player. If None, a default name is assigned.

        Returns:
            None.
        """
        super().__init__(name=name)

    def set_session_state(self, state: StreamlitSession | Mapping[str, Any]) -> None:
        """Set the streamlit session state used for the next `play` call.

        Args:
            state: Streamlit session wrapper or mapping-like state object.

        Returns:
            None.
        """
        if isinstance(state, StreamlitSession):
            self._session_state = state
            return
        self._session_state = StreamlitSession(state)

    def _read_selected_movement(self, state: StreamlitSession) -> Movement | None:
        """Return the pre-selected movement from session state when available.

        Args:
            state: Streamlit session state wrapper.

        Returns:
            Movement | None: Directly selected movement object, if present.
        """
        selected = state.get("selected_movement")
        if isinstance(selected, Movement):
            return selected
        return None

    def play(self, pos: Position) -> Movement:
        """Choose and return one movement for the provided position.

        Args:
            pos: Current position where this player must act.

        Returns:
            Movement: Movement parsed from current streamlit interaction state.
        """
        _ = pos
        render = getattr(self, "render", None)
        capture_input = getattr(render, "capture_input", None)
        if not callable(capture_input):
            raise TypeError("`render` must expose a callable `capture_input(state)` method.")

        state = getattr(self, "_session_state", StreamlitSession())
        selected = self._read_selected_movement(state)
        if selected is not None:
            state.pop("selected_movement", None)
            return selected

        return capture_input(state)

    def starting_game(self, rules: Rules, player_index: PlayerIndex) -> None:
        """Initialize runtime state before the first turn of a game.

        Args:
            rules: Rules object that governs the upcoming game.
            player_index: Index assigned to this player.

        Returns:
            None.
        """
        self._rules = rules
        self._player_index = player_index
        self._session_state = StreamlitSession()
