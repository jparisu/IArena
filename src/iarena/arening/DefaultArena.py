"""Declares the default composed arena used by the factory."""

from __future__ import annotations

from iarena.arening.behaviors.LogsStoringArena import LogsStoringArena
from iarena.arening.behaviors.MaxTurnsCheckingArena import MaxTurnsCheckingArena
from iarena.arening.behaviors.ScoreLimitCheckingArena import ScoreLimitCheckingArena
from iarena.arening.behaviors.TimeoutCheckingArena import TimeoutCheckingArena
from iarena.arening.behaviors.DirectExecuteTurnArena import DirectExecuteTurnArena


class DefaultArena(
    DirectExecuteTurnArena,
    TimeoutCheckingArena,
    ScoreLimitCheckingArena,
    MaxTurnsCheckingArena,
    LogsStoringArena,
):
    """Default arena combining the standard behavior implementation set."""
