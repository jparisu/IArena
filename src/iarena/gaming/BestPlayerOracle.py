"""Declares an abstract oracle that derives score limits from a best player."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
import math

from iarena.arening.OracleArena import OracleArena
from iarena.gaming.Oracle import Oracle
from iarena.playing.PlayerIndex import PlayerIndex
from iarena.scoring.Score import Score
from iarena.scoring.ScoreBoard import ScoreBoard
from iarena.visualizing.EmptyView import EmptyView

if TYPE_CHECKING:
    from iarena.gaming.Rules import Rules
    from iarena.playing.Player import Player


class BestPlayerOracle(Oracle, ABC):
    """Abstract oracle that estimates score limits by running a reference player.

    Purpose:
        Provide reusable logic to derive benchmark score limits from repeated runs
        of a game-specific best player.
    How it works:
        Executes the configured player in a lightweight arena for a fixed number of
        repetitions, computes the average resulting score, and applies configurable
        lower/higher ratios to that average.
    Used for:
        Building concrete game oracles where one trusted strategy is available.
    Public Attributes:
        best_player (Player): Player used as reference strategy for oracle runs.
        higher_limit_ratio (float): Ratio applied to average score for upper limit.
        lower_limit_ratio (float): Ratio applied to average score for lower limit.
        repetitions (int): Number of repeated runs used for average estimation.
    """

    best_player: Player
    higher_limit_ratio: float = math.inf
    lower_limit_ratio: float = -math.inf
    repetitions: int

    def __init__(
        self,
        best_player: Player,
        higher_limit_ratio: float = math.inf,
        lower_limit_ratio: float = -math.inf,
        repetitions: int = 1,
    ) -> None:
        """Create one best-player oracle configuration.

        Args:
            best_player: Reference strategy used to estimate score limits.
            higher_limit_ratio: Ratio applied to the average score upper bound.
            lower_limit_ratio: Ratio applied to the average score lower bound.
            repetitions: Number of repeated arena runs used for averaging.

        Returns:
            None.
        """
        if repetitions <= 0:
            raise ValueError("repetitions must be strictly positive.")

        self.best_player = best_player
        self.higher_limit_ratio = higher_limit_ratio
        self.lower_limit_ratio = lower_limit_ratio
        self.repetitions = repetitions

    @classmethod
    @abstractmethod
    def default(cls) -> BestPlayerOracle:
        """Return the default configured oracle instance for one concrete game.

        Returns:
            BestPlayerOracle: Ready-to-use oracle with concrete best player configuration.
        """
        raise NotImplementedError

    @classmethod
    def reckon_solution_score(cls, rules: Rules) -> tuple[ScoreBoard, ScoreBoard]:
        """Compute best and worst benchmark scoreboards for the provided rules.

        Args:
            rules: Rules instance used for oracle simulation.

        Returns:
            tuple[ScoreBoard, ScoreBoard]: Best and worst benchmark scoreboards.
        """
        return cls.default()._reckon_solution_score_from_best_player(rules=rules)

    def _build_scoreboard(self, score: Score) -> ScoreBoard:
        """Return one scoreboard containing only the single-player score.

        Args:
            score: Score value to bind to player index `0`.

        Returns:
            ScoreBoard: Scoreboard containing one score entry.
        """
        board = ScoreBoard()
        board._scores = {PlayerIndex(0): score}
        return board

    def _run_once(self, rules: Rules) -> float:
        """Execute one oracle simulation and return the resulting score.

        Args:
            rules: Rules object used to run one match.

        Returns:
            float: Final score achieved by the configured best player.
        """
        view = EmptyView()
        players = [self.best_player]
        arena = OracleArena(
            rules=rules,
            view=view,
            players=players,
            max_turns=1,
            max_turn_time_s=float("inf"),
            max_total_time_s=float("inf"),
            score_limits=(Score(float("-inf")), Score(float("inf"))),
            store_logs=False,
        )
        scoreboard = arena.play(rules=rules, players=players, view=view)
        return float(scoreboard.get_score(PlayerIndex(0)))

    def _reckon_solution_score_from_best_player(self, rules: Rules) -> tuple[ScoreBoard, ScoreBoard]:
        """Compute benchmark scoreboards from repeated best-player simulations.

        Args:
            rules: Rules object whose score limits must be estimated.

        Returns:
            tuple[ScoreBoard, ScoreBoard]: Best and worst scoreboards for one-player game.
        """
        if rules.n_players() != 1:
            raise ValueError("BestPlayerOracle can only be used with one-player rules.")

        sampled_scores = [self._run_once(rules=rules) for _ in range(self.repetitions)]
        min_observed_score = min(sampled_scores)
        max_observed_score = max(sampled_scores)

        lower_score = min_observed_score * self.lower_limit_ratio
        higher_score = max_observed_score * self.higher_limit_ratio

        worst_board = self._build_scoreboard(score=lower_score)
        best_board = self._build_scoreboard(score=higher_score)

        return best_board, worst_board
