"""Declares a lightweight arena variant dedicated to oracle score estimation."""

from __future__ import annotations

from iarena.arening.behaviors.DirectExecuteTurnArena import DirectExecuteTurnArena
from iarena.arening.behaviors.NoLogsArena import NoLogsArena
from iarena.arening.behaviors.NoMaxTurnsArena import NoMaxTurnsArena
from iarena.arening.behaviors.NoScoreLimitArena import NoScoreLimitArena
from iarena.arening.behaviors.NoTimeoutArena import NoTimeoutArena


class OracleArena(
    DirectExecuteTurnArena,
    NoTimeoutArena,
    NoScoreLimitArena,
    NoMaxTurnsArena,
    NoLogsArena,
):
    """Arena optimized for oracle runs with only game-finished termination."""
