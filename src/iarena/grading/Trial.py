"""Declares the trial aggregate for repeated match evaluation."""
# pylint: disable=too-many-lines  # TODO: review

from __future__ import annotations

from time import perf_counter
from typing import TYPE_CHECKING

from iarena.arening.ArenaFactory import ArenaFactory
from iarena.grading.DebugLevel import DebugLevel
from iarena.grading.MatchConfiguration import MatchConfiguration
from iarena.grading.MatchReport import MatchReport
from iarena.grading.TrialConfiguration import TrialConfiguration

if TYPE_CHECKING:
    from iarena.arening.Arena import Arena
    from iarena.scoring.Score import Score
    from iarena.scoring.ScoreBoard import ScoreBoard

from iarena.visualizing.EmptyView import EmptyView


class Trial:
    """Trial runner that evaluates one player setup over repeated matches.

    Purpose:
        Represent one grading unit that executes multiple matches under a
        shared configuration.
    How it is used:
        Exam objects coordinate several trials and consume their reports to
        derive final scores for the evaluated player.
    Why it exists:
        Separates trial-level concerns from individual match reporting and
        whole-exam orchestration.
    """

    configuration: TrialConfiguration
    match_reports: list[MatchReport]

    def _is_score_inside_limits(self, score: Score) -> bool:
        """Return whether one score is inside configured accepted limits.

        Args:
            score: Score obtained by the trialed player in one match.

        Returns:
            bool: `True` when score belongs to `[min_score, max_score]`.
        """
        numeric_score = float(score)
        return self.configuration.min_score <= numeric_score <= self.configuration.max_score

    def _score_from_scoreboard(self, scoreboard: ScoreBoard) -> Score:
        """Return the trial-player score extracted from a scoreboard.

        Args:
            scoreboard: Scoreboard produced by one finished match.

        Returns:
            Score assigned to the configured trialing player index.
        """
        return scoreboard.get_score(self.configuration.trialing_player_index)

    def _create_arena(self, view: EmptyView) -> Arena:
        """Build one arena configured from current match limits.

        Args:
            view: View instance attached to the created arena.

        Returns:
            Arena configured with trial rules, players, and execution limits.
        """
        match_configuration: MatchConfiguration = self.configuration.match_configuration
        return ArenaFactory.create_arena(
            rules=self.configuration.rules,
            view=view,
            players=self.configuration.players,
            max_turns=match_configuration.max_turns,
            max_turn_time_s=match_configuration.move_timeout_s,
            max_total_time_s=match_configuration.total_timeout_s,
            score_limits=match_configuration.score_limits,
            store_logs=False,
        )

    def _new_report(
        self,
        arena: Arena,
        score: Score,
        elapsed_s: float,
        repetition: int,
        debug_level: DebugLevel,
        warnings: list[str] | None = None,
    ) -> MatchReport:
        """Create one match report from runtime artifacts.

        Args:
            arena: Arena used to execute the match.
            score: Score extracted for the trialing player.
            elapsed_s: Match elapsed wall-clock time in seconds.
            repetition: Zero-based repetition index of the match.
            debug_level: Debug verbosity value used for trial execution.
            warnings: Optional warning messages attached to this match.

        Returns:
            MatchReport populated with per-match execution metadata.
        """
        report = MatchReport()
        report.moves = int(getattr(arena, "_turn_count", 0))
        report.total_time_s = float(elapsed_s)
        report.score = score
        report.messages = {
            "repetition": repetition,
            "debug_level": debug_level.name,
        }
        if warnings:
            report.messages["warnings"] = warnings
        return report

    def _error_report(
        self,
        elapsed_s: float,
        repetition: int,
        debug_level: DebugLevel,
        error: Exception,
    ) -> MatchReport:
        """Create one report representing a failed match execution.

        Args:
            elapsed_s: Match elapsed wall-clock time in seconds before failure.
            repetition: Zero-based repetition index of the failed match.
            debug_level: Debug verbosity value used for trial execution.
            error: Exception raised during arena creation or execution.

        Returns:
            MatchReport with neutral score and captured failure details.
        """
        report = MatchReport()
        report.moves = 0
        report.total_time_s = float(elapsed_s)
        report.score = self.configuration.match_configuration.score_limits[0]
        report.messages = {
            "repetition": repetition,
            "debug_level": debug_level.name,
            "error": str(error),
            "error_type": type(error).__name__,
            "errors": [f"{type(error).__name__}: {error}"],
        }
        return report

    def trial(self, debug_level: DebugLevel = DebugLevel.USER) -> list[MatchReport]:
        """Run match repetitions and return generated reports.

        What it does:
            Executes the configured amount of match repetitions and records
            one report per executed match.
        How it works:
            Uses the trial configuration to orchestrate runs and stores the
            resulting report objects in `match_reports`.
        Args:
            debug_level (DebugLevel, optional): Verbosity level controlling
                runtime diagnostic output during the trial process.
        Returns:
            List[MatchReport]: Ordered collection of report entries generated
                by the repeated match executions.
        Raises:
            RuntimeError: If match failures exceed the configured `allow_fails`
                threshold.
        """
        self.match_reports = []
        failures = 0

        for repetition in range(self.configuration.repetitions):
            started = perf_counter()
            match_failed = False
            failure_error: Exception | None = None
            try:
                view = EmptyView()
                arena = self._create_arena(view=view)
                scoreboard = arena.play(
                    rules=self.configuration.rules,
                    players=self.configuration.players,
                    view=view,
                )
                score = self._score_from_scoreboard(scoreboard)
                report = self._new_report(
                    arena=arena,
                    score=score,
                    elapsed_s=perf_counter() - started,
                    repetition=repetition,
                    debug_level=debug_level,
                )
                if not self._is_score_inside_limits(score):
                    failures += 1
                    match_failed = True
                    report.messages["warnings"] = [
                        (
                            f"Score {float(score)} is outside accepted range "
                            f"[{self.configuration.min_score}, {self.configuration.max_score}]."
                        ),
                    ]
            except Exception as error:  # pragma: no cover - exercised by fail-path tests
                failures += 1
                match_failed = True
                failure_error = error
                report = self._error_report(
                    elapsed_s=perf_counter() - started,
                    repetition=repetition,
                    debug_level=debug_level,
                    error=error,
                )

            if match_failed and failures > self.configuration.allow_fails:
                if failure_error is not None:
                    raise RuntimeError("Trial exceeded the allowed number of failed matches.") from failure_error
                raise RuntimeError("Trial exceeded the allowed number of failed matches.")
            self.match_reports.append(report)

        return self.match_reports

    def score(self) -> float:
        """Compute the aggregated numeric score for the trial.

        What it does:
            Derives one scalar value that summarizes trial performance across
            all generated match reports.
        How it works:
            Aggregates report-level score values according to the trial scoring
            policy defined by concrete implementations.
        Args:
            None.
        Returns:
            float: Numeric score representing the overall trial result.
        """
        reports: list[MatchReport] = getattr(self, "match_reports", [])
        if not reports:
            return 0.0
        return float(sum(float(report.score) for report in reports) / len(reports))
