"""Declares the best-player oracle for the GoldMine game."""

from __future__ import annotations

from typing import TYPE_CHECKING

from iarena.gaming.BestPlayerOracle import BestPlayerOracle
from iarena.gaming.goldmine.GoldMinePerfectPlayer import GoldMinePerfectPlayer

if TYPE_CHECKING:
    from iarena.gaming.Rules import Rules
    from iarena.scoring.ScoreBoard import ScoreBoard

from iarena.gaming.goldmine.GoldMineRules import GoldMineRules


class GoldMineOracle(BestPlayerOracle):
    """Benchmark oracle relying on repeated GoldMine perfect-player simulations.

    Purpose:
        Estimate GoldMine score limits with a high-quality stochastic player.
    How it works:
        Replays the same rules with `GoldMinePerfectPlayer` for a configurable
        number of repetitions and applies lower and higher score ratios.
    Used for:
        Deriving practical benchmark limits for grading and arena score bounds.
    Public Attributes:
        Inherits public attributes from `BestPlayerOracle`.
    """

    def __init__(
        self,
        repetitions: int = 10,
        higher_limit_ratio: float = 0.0,
        lower_limit_ratio: float = 1.2,
        player_seed: int | None = 0,

    ) -> None:
        """Create one GoldMine oracle with configurable stochastic simulation.

        Args:
            repetitions: Number of oracle simulations used to estimate limits.
            higher_limit_ratio: Ratio applied to average score for upper bound.
            lower_limit_ratio: Ratio applied to average score for lower bound.
            player_seed: Seed used by the internal perfect player.
        """
        super().__init__(
            higher_limit_ratio=higher_limit_ratio,
            lower_limit_ratio=lower_limit_ratio,
            repetitions=repetitions,
        )
        self._seed = player_seed if player_seed is not None else 0

    @classmethod
    def default(cls) -> BestPlayerOracle:
        """Return one default GoldMine oracle configuration.

        Returns:
            BestPlayerOracle: Default configured oracle.
        """
        return cls()

    @classmethod
    def reckon_solution_score(cls, rules: Rules) -> tuple[ScoreBoard, ScoreBoard]:
        """Compute benchmark score limits for one GoldMine ruleset.

        Args:
            rules: Rules instance to evaluate.

        Returns:
            tuple[ScoreBoard, ScoreBoard]: Best and worst benchmark scoreboards.
        """
        if not isinstance(rules, GoldMineRules):
            raise TypeError("rules must be an instance of GoldMineRules.")
        return super().reckon_solution_score(rules=rules)

    def _create_best_player(self, iteration: int) -> GoldMinePerfectPlayer:
        """Create one instance of the configured best player for the given iteration.

        Args:
            iteration: Index of the current repetition (starting from 0).

        Returns:
            Player: New instance of the configured best player.
        """
        return GoldMinePerfectPlayer(seed=self._seed + iteration)
