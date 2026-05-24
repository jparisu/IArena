"""Declares the grader facade for configuration files and in-memory players."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import yaml

from iarena.grading.Exam import Exam
from iarena.grading.DebugLevel import DebugLevel
from iarena.grading.ExamReader import ExamReader
from iarena.grading.MatchReport import MatchReport
from iarena.playing.Player import Player
from iarena.utilizing.filing.FileLoader import FileLoader


class Grader:
    """Facade that bridges one configuration file with one existing player.

    Purpose:
        Provide a single entry abstraction that links one grading
        configuration file and one already-created player to exam execution.
    How it is used:
        Applications instantiate this class from a file and player instance,
        then delegate grade/score operations to the underlying exam.
    Why it exists:
        Keeps file-driven exam setup while avoiding player-loading concerns
        when player instances are already available in memory.
    """

    grader: Exam
    configuration_file: str
    player: Player

    @classmethod
    def from_file(cls, configuration_file: str, player: Player) -> Grader:
        """Build one grader from a YAML configuration and one player instance.

        Args:
            configuration_file: Path to grader YAML configuration.
            player: Player instance to grade.

        Returns:
            Grader: Configured grader ready to run grading.
        """
        grader = cls()
        grader.configuration_file = configuration_file
        grader.player = player
        configuration = cls._read_configuration(configuration_file)
        grader.grader = ExamReader.from_mapping(configuration=configuration, player=player)
        return grader

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
        """Return the configured exam instance or raise a clear error.

        Returns:
            Exam: Exam instance stored in this grader.

        Raises:
            RuntimeError: If `grader` has not been configured.
        """
        grader = getattr(self, "grader", None)
        if grader is None:
            raise RuntimeError("Grader requires `grader` to be configured before grading.")
        return grader

    def grade(self, debug_level: DebugLevel = DebugLevel.USER) -> list[list[MatchReport]]:
        """Run grading and return grouped match reports.

        Args:
            debug_level: Verbosity level propagated to exam and trial execution.

        Returns:
            list[list[MatchReport]]: Nested reports grouped by trial.
        """
        return self._require_grader().grade(debug_level=debug_level)

    def score(self) -> float:
        """Return the final numeric score computed by the grader.

        Returns:
            float: Final score for the current grading context.
        """
        return self._require_grader().score()
