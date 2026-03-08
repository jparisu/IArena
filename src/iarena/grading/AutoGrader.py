"""Declares the autograder façade that binds configuration inputs to exams."""

from __future__ import annotations

from iarena.grading.Exam import Exam
from iarena.grading.MatchReport import MatchReport


class AutoGrader:
    """Facade that bridges user configuration files with exam grading.

    Purpose:
        Provide a single entry abstraction that links external grading inputs
        to internal exam execution workflows.
    How it is used:
        Applications instantiate this class with configuration artifacts and
        delegate grade/score operations to the underlying exam.
    Why it exists:
        Keeps file-driven orchestration concerns separate from core grading
        domain structures such as trials and reports.
    """

    grader: Exam
    configuration_file: str
    player_file: str

    def _require_grader(self) -> Exam:
        """Return the configured grader instance or raise a clear error.

        Args:
            None.

        Returns:
            Exam instance stored in this autograder.

        Raises:
            RuntimeError: If `grader` has not been configured.
        """
        grader = getattr(self, "grader", None)
        if grader is None:
            raise RuntimeError("AutoGrader requires `grader` to be configured before grading.")
        return grader

    def grade(self) -> list[list[MatchReport]]:
        """Run grading and return grouped match reports.

        What it does:
            Triggers the grading process managed by the underlying exam and
            returns trial-grouped match reports.
        How it works:
            Delegates grading orchestration to `grader` while preserving a
            simple API for file-driven application entry points.
        Args:
            None.
        Returns:
            list[list[MatchReport]]: Nested reports grouped by trial in the
                same order as exam execution.
        """
        return self._require_grader().grade()

    def score(self) -> float:
        """Return the final numeric score computed by the grader.

        What it does:
            Exposes one direct accessor for the final scalar score generated
            by grading execution.
        How it works:
            Delegates score retrieval to the associated `grader` instance.
        Args:
            None.
        Returns:
            float: Final score for the current autograding context.
        """
        return self._require_grader().score()
