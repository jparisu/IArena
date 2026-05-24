"""Declares a backward-compatible alias for the Hanoi perfect player type."""

from __future__ import annotations

from iarena.gaming.hanoi.PerfectHanoiPlayer import PerfectHanoiPlayer


class HanoiPerfectPlayer(PerfectHanoiPlayer):
    """Backward-compatible alias for :class:`PerfectHanoiPlayer`.

    Purpose:
        Preserve compatibility with previous public imports while delegating the
        implementation to `PerfectHanoiPlayer`.
    How it works:
        Inherits the full behavior from `PerfectHanoiPlayer` without overriding methods.
    Used for:
        Legacy imports and integrations still referencing `HanoiPerfectPlayer`.
    Public Attributes:
        Inherits public API from `PerfectHanoiPlayer`.
    """
