"""Declares the autograder façade that binds configuration inputs to exams."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import yaml

from iarena.grading.Exam import Exam
from iarena.grading.DebugLevel import DebugLevel
from iarena.grading.ExamReader import ExamReader
from iarena.grading.MatchReport import MatchReport
from iarena.playing.LoadPlayer import LoadPlayer
from iarena.utilizing.filing.FileLoader import FileLoader


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
    token: str

    @classmethod
    def from_files(
        cls,
        configuration_file: str,
        player_file: str,
        token: str = "PLAYER =",
    ) -> AutoGrader:
        """Build one autograder from a YAML configuration and player file.

        Args:
            configuration_file: Path to grader YAML configuration.
            player_file: Path to a player file exposing `PLAYER`.
            token: Notebook cell selector token used for `.ipynb` players.

        Returns:
            AutoGrader: Configured autograder ready to grade the player.
        """
        autograder = cls()
        autograder.configuration_file = configuration_file
        autograder.player_file = player_file
        autograder.token = token

        player = LoadPlayer.from_file(player_file, token=token)
        configuration = cls._read_configuration(configuration_file=configuration_file)
        autograder.grader = ExamReader.from_mapping(configuration=configuration, player=player)
        return autograder

    @classmethod
    def _read_configuration(cls, configuration_file: str) -> dict[str, Any]:
        """Read one YAML configuration from local disk or an online URL.

        Args:
            configuration_file: Local file path or HTTP(S) URL.

        Returns:
            dict[str, Any]: Parsed configuration mapping.

        Raises:
            TypeError: If parsed YAML root content is not a mapping.
            ValueError: If YAML payload is invalid.
        """
        _ = cls
        payload = yaml.safe_load(FileLoader.read_file(filename=configuration_file))
        if payload is None:
            return {}
        if not isinstance(payload, Mapping):
            raise TypeError("Configuration root content must be a mapping/object.")
        return dict(payload)

    def _require_grader(self) -> Exam:
        """Return the configured grader instance or raise a clear error.

        Returns:
            Exam instance stored in this autograder.

        Raises:
            RuntimeError: If `grader` has not been configured.
        """
        grader = getattr(self, "grader", None)
        if grader is None:
            raise RuntimeError("AutoGrader requires `grader` to be configured before grading.")
        return grader

    def grade(self, debug_level: DebugLevel = DebugLevel.USER) -> list[list[MatchReport]]:
        """Run grading and return grouped match reports.

        What it does:
            Triggers the grading process managed by the underlying exam and
            returns trial-grouped match reports.
        How it works:
            Delegates grading orchestration to `grader` while preserving a
            simple API for file-driven application entry points.
        Args:
            debug_level: Verbosity level propagated to exam and trial execution.
        Returns:
            list[list[MatchReport]]: Nested reports grouped by trial in the
                same order as exam execution.
        """
        return self._require_grader().grade(debug_level=debug_level)

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
