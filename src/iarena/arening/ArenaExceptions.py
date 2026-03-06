"""Arena-specific exceptions used to signal controlled game-stop conditions."""

from __future__ import annotations

from iarena.desining.gaming.ScoreBoard import ScoreBoard


class ArenaStoppedError(RuntimeError):
    """Raised when one arena stop condition interrupts normal game completion."""

    def __init__(self, reason: str, final_score: ScoreBoard) -> None:
        """Initialize an arena stop error.

        Args:
            reason: Human-readable explanation for the stop.
            final_score: Final/failure score associated with the stop.

        Returns:
            None.
        """
        super().__init__(reason)
        self.reason = reason
        self.final_score = final_score
