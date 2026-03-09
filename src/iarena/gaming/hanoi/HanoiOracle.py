"""Declares the concrete best-player oracle for the Hanoi game."""

from __future__ import annotations

from typing import TYPE_CHECKING

from iarena.gaming.BestPlayerOracle import BestPlayerOracle
from iarena.gaming.hanoi.PerfectHanoiPlayer import PerfectHanoiPlayer

if TYPE_CHECKING:
    from iarena.gaming.Rules import Rules
    from iarena.scoring.ScoreBoard import ScoreBoard

from iarena.gaming.hanoi.HanoiRules import HanoiRules


class HanoiOracle(BestPlayerOracle):
    """Benchmark oracle that delegates score estimation to `PerfectHanoiPlayer`.

    Purpose:
        Provide score limits for Hanoi by repeatedly running the best known
        deterministic player in an unconstrained arena.
    How it works:
        Uses `BestPlayerOracle` with `PerfectHanoiPlayer` and ratio `1.0` for
        both lower and higher score limits.
    Used for:
        Match grading and score-limit configuration for Hanoi sessions.
    Public Attributes:
        Inherits public attributes from `BestPlayerOracle`.
    """

    def __init__(self) -> None:
        """Create one Hanoi oracle with fixed perfect-player limit ratios.

        Returns:
            None.
        """
        super().__init__(
            best_player=PerfectHanoiPlayer(),
            higher_limit_ratio=1.0,
            lower_limit_ratio=1.0,
            repetitions=1,
        )

    @classmethod
    def default(cls) -> BestPlayerOracle:
        """Return the default configured Hanoi oracle instance.

        Returns:
            BestPlayerOracle: Default Hanoi oracle configuration.
        """
        return cls()

    @classmethod
    def reckon_solution_score(cls, rules: Rules) -> tuple[ScoreBoard, ScoreBoard]:
        """Compute best and worst benchmark scoreboards for one Hanoi ruleset.

        Args:
            rules: Rules instance to evaluate.

        Returns:
            tuple[ScoreBoard, ScoreBoard]: Best and worst benchmark scoreboards.
        """
        if not isinstance(rules, HanoiRules):
            raise TypeError("rules must be an instance of HanoiRules.")
        return super().reckon_solution_score(rules=rules)
