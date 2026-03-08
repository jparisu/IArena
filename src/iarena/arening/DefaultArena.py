"""Declares the default composed arena used by the factory."""

from __future__ import annotations

from .behaviors.LogsStoringArena import LogsStoringArena
from .behaviors.MaxTurnsCheckingArena import MaxTurnsCheckingArena
from .behaviors.ScoreLimitCheckingArena import ScoreLimitCheckingArena
from .behaviors.TimeoutCheckingArena import TimeoutCheckingArena
from .behaviors.WorkerExecuteTurnArena import WorkerExecuteTurnArena


class DefaultArena(
    WorkerExecuteTurnArena,
    TimeoutCheckingArena,
    ScoreLimitCheckingArena,
    MaxTurnsCheckingArena,
    LogsStoringArena,
):
    """Default arena combining the standard behavior implementation set."""
