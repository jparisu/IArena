"""Declares the exam aggregate that groups multiple trials for grading."""

from __future__ import annotations

from iarena.gaming.Configuration import Configuration
from iarena.gaming.ConfigurationSuite import ConfigurationSuite
from iarena.gaming.Game import Game
from iarena.grading.DebugLevel import DebugLevel
from iarena.grading.MatchConfiguration import MatchConfiguration
from iarena.grading.MatchReport import MatchReport
from iarena.grading.Trial import Trial
from iarena.grading.TrialConfiguration import TrialConfiguration
from iarena.playing.Player import Player
from iarena.playing.PlayerIndex import PlayerIndex
from iarena.scoring.Score import Score


class Exam:
    """Collection of trials used to grade one player over a suite.

    Purpose:
        Aggregate all trial executions required to evaluate a player for a
        given game and configuration suite.
    How it is used:
        Autograding workflows instantiate one exam and collect trial outcomes
        and computed numeric values from it.
    Why it exists:
        Concentrates cross-trial grading state in a single domain object that
        can be managed by higher-level tools.
    """

    game: Game
    player: Player
    suite_configuration: ConfigurationSuite
    trial_configurations: list[TrialConfiguration]
    trials: list[Trial]
    trial_value: list[float]

    def _iter_configurations(self) -> list[Configuration]:
        """Return all concrete configurations contained in the suite.

        Returns:
            List of concrete game configurations to evaluate.

        Raises:
            TypeError: If `suite_configuration` does not expose
                `generate_configurations`.
        """
        generator = getattr(self.suite_configuration, "generate_configurations", None)
        if not callable(generator):
            raise TypeError("suite_configuration must expose a callable `generate_configurations()` method.")
        return list(generator())

    def _build_players(self, n_players: int) -> list[Player]:
        """Build the ordered player list used by trial execution.

        Args:
            n_players: Required number of players declared by the rules object.

        Returns:
            Player list containing the graded player in each required slot.
        """
        return [self.player for _ in range(n_players)]

    def _build_trial_configuration(self, configuration: Configuration) -> TrialConfiguration:
        """Create one trial configuration from a concrete game configuration.

        Args:
            configuration: Concrete game configuration to evaluate.

        Returns:
            TrialConfiguration configured for one full repeated match evaluation.
        """
        rules = self.game.generate_rules(configuration)
        n_players = max(1, rules.n_players())
        return TrialConfiguration(
            match_configuration=MatchConfiguration(
                move_timeout_s=1.0,
                total_timeout_s=60.0,
                max_turns=10_000,
                score_limits=(Score(float("-inf")), Score(float("inf"))),
            ),
            trialing_player_index=PlayerIndex(0),
            rules=rules,
            players=self._build_players(n_players=n_players),
            repetitions=1,
            allow_fails=0,
        )

    def _iter_trial_configurations(self) -> list[TrialConfiguration]:
        """Return all trial configurations to execute.

        Returns:
            list[TrialConfiguration]: Explicit configurations when already set;
            otherwise defaults built from the suite configurations.
        """
        explicit_trial_configurations = list(getattr(self, "trial_configurations", []))
        if explicit_trial_configurations:
            return explicit_trial_configurations

        return [
            self._build_trial_configuration(configuration=configuration)
            for configuration in self._iter_configurations()
        ]

    def grade(self, debug_level: DebugLevel = DebugLevel.USER) -> list[list[MatchReport]]:
        """Execute all trials and return nested match reports.

        What it does:
            Runs each configured trial for the current exam and returns all
            produced match reports grouped by trial.
        How it works:
            Iterates through `trials`, delegates execution to each trial
            object, and collects one list of reports per trial in order.
        Args:
            debug_level (DebugLevel, optional): Verbosity level used while
                grading each trial in the exam.
        Returns:
            List[List[MatchReport]]: Nested collection where each inner list
                contains reports for one executed trial.
        """
        self.trials = []
        self.trial_value = []
        grouped_reports: list[list[MatchReport]] = []

        for trial_configuration in self._iter_trial_configurations():
            trial = Trial()
            trial.configuration = trial_configuration
            trial.match_reports = []
            reports = trial.trial(debug_level=debug_level)
            grouped_reports.append(reports)
            self.trials.append(trial)
            self.trial_value.append(trial.score())

        return grouped_reports

    def score(self) -> float:
        """Compute the final numeric score across all trials.

        What it does:
            Produces the consolidated score for the exam from all trial
            outcomes.
        How it works:
            Aggregates trial-level numeric values based on the exam scoring
            policy applied by concrete implementations.
        Args:
            None.
        Returns:
            float: Final score of the evaluated player for this exam.
        """
        trial_scores = list(getattr(self, "trial_value", []))
        if not trial_scores:
            trial_scores = [trial.score() for trial in getattr(self, "trials", [])]
        if not trial_scores:
            return 0.0
        return float(sum(trial_scores) / len(trial_scores))
