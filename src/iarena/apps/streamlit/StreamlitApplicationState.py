"""Declares runtime states used by the streamlit application workflow."""

from __future__ import annotations

from enum import Enum


class StreamlitApplicationState(str, Enum):
    """Finite state machine values used by `StreamlitApplication`.

    Purpose:
        Define explicit user-interface states for streamlit gameplay flows.
    How it works:
        Exposes stable string enum values consumed by session-state transitions.
    Used for:
        Coordinating selection, configuration, playing, and review lifecycle steps.
    Public Attributes:
        SELECTION: Game selection stage.
        CONFIGURATION: Pre-game setup stage.
        PLAYING: Live interaction stage.
        REVIEWING: Replay and step-navigation stage.
    """

    SELECTION = "SELECTION"
    CONFIGURATION = "CONFIGURATION"
    PLAYING = "PLAYING"
    REVIEWING = "REVIEWING"
