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
from iarena.scoring.Score import Score

if TYPE_CHECKING:
    from iarena.arening.Arena import Arena
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

    def _debug_enabled(self, current_level: DebugLevel, required_level: DebugLevel) -> bool:
        """Return whether one debug message should be emitted.

        Args:
            current_level: Active debug level for current execution.
            required_level: Minimum level required for the message.

        Returns:
            bool: `True` when `current_level` includes `required_level`.
        """
        return current_level.value >= required_level.value

    def _emit_debug(self, message: str, current_level: DebugLevel, required_level: DebugLevel) -> None:
        """Print one debug line when active level includes the required level.

        Args:
            message: Text to print.
            current_level: Active debug level.
            required_level: Minimum level required to print.

        Returns:
            None.
        """
        if self._debug_enabled(current_level=current_level, required_level=required_level):
            print(message, flush=True)

    def _emit_trial_start(self, debug_level: DebugLevel) -> None:
        """Emit trial start messages according to current debug level.

        Args:
            debug_level: Active debug level.

        Returns:
            None.
        """
        description = self.configuration.description.strip() or "trial"
        self._emit_debug(message=f"> Running: {description}", current_level=debug_level, required_level=DebugLevel.USER)
        self._emit_debug(
            message=f"  > Info: {self.configuration}",
            current_level=debug_level,
            required_level=DebugLevel.INFO,
        )

    def _emit_repetition_result(self, report: MatchReport, debug_level: DebugLevel) -> None:
        """Emit per-repetition outcome diagnostics.

        Args:
            report: Match report generated for one repetition.
            debug_level: Active debug level.

        Returns:
            None.
        """
        repetition = int(report.messages.get("repetition", 0)) + 1
        accepted = bool(report.messages.get("accepted", False))
        status = "accepted" if accepted else "rejected"
        marker = "✓" if accepted else "✗"

        self._emit_debug(
            message=f"  > {marker} repetition {repetition}/{self.configuration.repetitions} ({status})",
            current_level=debug_level,
            required_level=DebugLevel.USER,
        )

        warnings = report.messages.get("warnings", [])
        if warnings:
            warning_message = str(warnings[0])
            self._emit_debug(
                message=f"  > WARNING repetition {repetition}: {warning_message}",
                current_level=debug_level,
                required_level=DebugLevel.WARNING,
            )

        error_text = report.messages.get("error")
        if isinstance(error_text, str):
            self._emit_debug(
                message=f"  > ERROR repetition {repetition}: {error_text}",
                current_level=debug_level,
                required_level=DebugLevel.ERROR,
            )

        self._emit_debug(
            message=(
                f"    > DEBUG repetition {repetition}: "
                f"score={float(report.score)} moves={report.moves} total_time_s={report.total_time_s:.6f} "
                f"messages={report.messages}"
            ),
            current_level=debug_level,
            required_level=DebugLevel.DEBUG,
        )

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

    def _create_arena(self) -> Arena:
        """Build one arena configured from current match limits.

        Returns:
            Arena configured with current execution limits.
        """
        match_configuration: MatchConfiguration = self.configuration.match_configuration
        return ArenaFactory.create_arena(
            max_turns=match_configuration.max_turns,
            max_turn_time_s=match_configuration.move_timeout_s,
            max_total_time_s=match_configuration.total_timeout_s,
            score_limits=match_configuration.score_limits,
            store_logs=False,
        )

    def _new_report(
        self,
        arena: Arena,
        accepted: bool,
        elapsed_s: float,
        repetition: int,
        debug_level: DebugLevel,
        warnings: list[str] | None = None,
    ) -> MatchReport:
        """Create one match report from runtime artifacts.

        Args:
            arena: Arena used to execute the match.
            accepted: Whether the run was accepted by grading constraints.
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
        report.score = Score(1.0 if accepted else 0.0)
        report.messages = {
            "repetition": repetition,
            "debug_level": debug_level.name,
            "accepted": accepted,
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
        report.score = Score(0.0)
        report.messages = {
            "repetition": repetition,
            "debug_level": debug_level.name,
            "accepted": False,
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
        """
        self.match_reports = []
        self._emit_trial_start(debug_level=debug_level)

        for repetition in range(self.configuration.repetitions):
            started = perf_counter()
            try:
                view = EmptyView()
                arena = self._create_arena()
                scoreboard = arena.play(
                    rules=self.configuration.rules,
                    players=self.configuration.players,
                    view=view,
                )
                score = self._score_from_scoreboard(scoreboard)
                accepted = self._is_score_inside_limits(score)
                warnings: list[str] | None = None
                if not accepted:
                    warnings = [
                        (
                            f"Score {float(score)} is outside accepted range "
                            f"[{self.configuration.min_score}, {self.configuration.max_score}]."
                        ),
                    ]
                report = self._new_report(
                    arena=arena,
                    accepted=accepted,
                    elapsed_s=perf_counter() - started,
                    repetition=repetition,
                    debug_level=debug_level,
                    warnings=warnings,
                )
            except Exception as error:  # pragma: no cover - exercised by fail-path tests
                report = self._error_report(
                    elapsed_s=perf_counter() - started,
                    repetition=repetition,
                    debug_level=debug_level,
                    error=error,
                )

            self.match_reports.append(report)
            self._emit_repetition_result(report=report, debug_level=debug_level)

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
        all_accepted = all(float(report.score) == 1.0 for report in reports)
        return 1.0 if all_accepted else 0.0
