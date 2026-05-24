"""Declares a multi-player autograder that evaluates all players from one zip file."""

from __future__ import annotations

import csv
import itertools
import math
import zipfile
from collections.abc import Mapping
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

import yaml

from iarena.gaming.Configuration import Configuration
from iarena.gaming.Game import Game
from iarena.gaming.goldmine.GoldMineGame import GoldMineGame
from iarena.gaming.hanoi.HanoiGame import HanoiGame
from iarena.gaming.tictactoe.TicTacToeGame import TicTacToeGame
from iarena.grading.DebugLevel import DebugLevel
from iarena.grading.MatchConfiguration import MatchConfiguration
from iarena.grading.Trial import Trial
from iarena.grading.TrialConfiguration import TrialConfiguration
from iarena.playing.LoadPlayer import LoadPlayer
from iarena.playing.Player import Player
from iarena.playing.PlayerIndex import PlayerIndex
from iarena.scoring.Score import Score
from iarena.utilizing.filing.FileLoader import FileLoader


class MultiGrader:
    """Autograder that evaluates multiple players loaded from one zip archive.

    Purpose:
        Provide one high-level entry point that grades all discoverable player
        files from a submissions zip against a shared grader configuration.
    How it is used:
        Build with `from_zip`, run `grade_all`, and persist results with
        `write_csv`.
    Why it exists:
        Supports classroom-style grading workflows where many independent
        players must be evaluated in one batch.
    """

    game: Game
    configuration_class: type[Configuration]
    trial_definitions: list[tuple[Configuration, int, float]]
    match_configuration: MatchConfiguration
    players: list[dict[str, Any]]
    results: list[dict[str, Any]]
    token: str
    _temporary_directory: TemporaryDirectory[str]

    @classmethod
    def from_zip(
        cls,
        configuration_filename: str,
        zip_filename: str,
        repetitions: int = 1,
        token: str = "PLAYER =",
    ) -> MultiGrader:
        """Build one `MultiGrader` from a configuration source and submissions zip.

        Args:
            configuration_filename: YAML configuration path or HTTP(S) URL.
            zip_filename: Path to the zip archive containing player files.
            repetitions: Global repetition multiplier applied to all reports.
            token: Notebook cell selector token used for `.ipynb` players.

        Returns:
            MultiGrader: Configured grader ready to evaluate all discovered players.
        """
        grader = cls()
        configuration = grader._read_configuration(configuration_filename)
        grader._configure_from_mapping(configuration=configuration, repetitions=max(1, int(repetitions)))
        grader.players = []
        grader.results = []
        grader.token = token

        grader._temporary_directory = TemporaryDirectory()
        extract_root = Path(grader._temporary_directory.name)
        with zipfile.ZipFile(zip_filename, "r") as archive:
            archive.extractall(path=extract_root)

        grader._discover_players(extract_root)
        return grader

    def _read_configuration(self, configuration_filename: str) -> dict[str, Any]:
        """Read one grading configuration from disk or URL."""
        _ = self
        payload = yaml.safe_load(FileLoader.read_file(filename=configuration_filename))
        if payload is None:
            return {}
        if not isinstance(payload, Mapping):
            raise TypeError("Configuration root content must be a mapping/object.")
        return dict(payload)

    def _configure_from_mapping(self, configuration: dict[str, Any], repetitions: int) -> None:
        """Parse mapping settings into concrete grading runtime objects."""
        self.game = self._resolve_game(configuration.get("game", ""))

        configuration_candidates = sorted(
            self.game.get_configurations(lambda _: True),
            key=lambda candidate: candidate.__name__,
        )
        if not configuration_candidates:
            raise RuntimeError(f"Game '{self.game.name()}' does not expose any configuration class.")
        self.configuration_class = configuration_candidates[0]

        global_repetitions = max(1, int(configuration.get("repetitions", 1)))
        self.match_configuration = MatchConfiguration(
            move_timeout_s=float(configuration.get("move_timeout_s", 1.0)),
            total_timeout_s=float(configuration.get("total_timeout_s", 60.0)),
            max_turns=int(configuration.get("max_moves", 10_000)),
            score_limits=(
                Score(float(configuration.get("min_score", float("-inf")))),
                Score(float(configuration.get("max_score", float("inf")))),
            ),
        )
        self.trial_definitions = self._build_trial_definitions(
            reports=configuration.get("trials", configuration.get("reports", [])),
            global_repetitions=global_repetitions * repetitions,
        )

    def _resolve_game(self, game_name: object) -> Game:
        """Resolve one textual game name into a concrete game singleton."""
        if not isinstance(game_name, str) or not game_name.strip():
            raise ValueError("Configuration requires a non-empty `game` field.")

        normalized = game_name.strip().lower()
        registry: dict[str, Game] = {
            "hanoi": HanoiGame.instance(),
            "goldmine": GoldMineGame.instance(),
            "tictactoe": TicTacToeGame.instance(),
        }
        if normalized not in registry:
            supported = ", ".join(sorted(registry))
            raise ValueError(f"Unsupported game '{game_name}'. Supported games: {supported}.")
        return registry[normalized]

    def _build_trial_definitions(
        self,
        reports: object,
        global_repetitions: int,
    ) -> list[tuple[Configuration, int, float]]:
        """Expand trial definitions into concrete configuration/repetition pairs."""
        if not isinstance(reports, list):
            raise TypeError("Configuration field `trials` (or `reports`) must be a list.")

        definitions: list[tuple[Configuration, int, float]] = []
        for report in reports:
            if not isinstance(report, dict):
                raise TypeError("Each report entry must be a mapping/object.")
            raw_base_args = report.get("args", {})
            if not isinstance(raw_base_args, dict):
                raise TypeError("Report field `args` must be a mapping/object when provided.")
            base_args = dict(raw_base_args)

            per_report_repetitions = max(1, int(report.get("repetitions", 1))) * global_repetitions
            trial_value = float(report.get("value", 1.0))
            for expanded_args in self._expand_args(base_args=base_args, multi_args=report.get("multi_args", {})):
                definition = self.configuration_class.from_dict(expanded_args)
                definitions.append((definition, per_report_repetitions, trial_value))

        if not definitions:
            definition = self.configuration_class.from_dict({})
            definitions.append((definition, global_repetitions, 1.0))
        return definitions

    def _expand_args(self, base_args: dict[str, Any], multi_args: object) -> list[dict[str, Any]]:
        """Expand `base_args` using cartesian products declared in `multi_args`."""
        if not isinstance(multi_args, dict):
            raise TypeError("Report field `multi_args` must be a mapping/object when provided.")
        if not multi_args:
            return [dict(base_args)]

        normalized_multi_args: dict[str, list[Any]] = {}
        for field_name, values in multi_args.items():
            if isinstance(values, list):
                candidate_values = list(values)
            else:
                candidate_values = [values]
            if not candidate_values:
                raise ValueError(f"Report field `multi_args.{field_name}` must not be empty.")
            normalized_multi_args[field_name] = candidate_values

        expanded: list[dict[str, Any]] = []
        multi_arg_keys = list(normalized_multi_args.keys())
        domains = [normalized_multi_args[key] for key in multi_arg_keys]
        for choices in itertools.product(*domains):
            args = dict(base_args)
            for field_name, value in zip(multi_arg_keys, choices, strict=False):
                args[field_name] = value
            expanded.append(args)
        return expanded

    def _discover_players(self, extracted_root: Path) -> None:
        """Load all `.py` and `.ipynb` candidate player files from one extracted folder."""
        self.players = []
        player_files = sorted(
            path
            for path in extracted_root.rglob("*")
            if path.is_file() and path.suffix.lower() in {".py", ".ipynb"}
        )
        for player_file in player_files:
            try:
                player = LoadPlayer.from_file(str(player_file), token=self.token)
                self.players.append(
                    {
                        "file": str(player_file),
                        "player": player,
                        "authors": self._authors(player),
                    },
                )
            except Exception as error:  # pragma: no cover - exercised by integration-oriented test paths
                self.players.append(
                    {
                        "file": str(player_file),
                        "player": None,
                        "authors": [],
                        "load_error": f"{type(error).__name__}: {error}",
                    },
                )

    def _authors(self, player: Player) -> list[str]:
        """Return a safe authors list for one loaded player."""
        try:
            authors_method = getattr(player, "authors")
            authors = authors_method()
        except Exception:
            return []
        if not isinstance(authors, list):
            return []
        return [str(author) for author in authors]

    def grade_all(self, debug: bool = False) -> list[dict[str, Any]]:
        """Grade all discovered players and store one result row per player.

        Args:
            debug: Whether to run grading with debug-level metadata.

        Returns:
            list[dict[str, Any]]: Result rows ready for CSV export.
        """
        self.results = []
        debug_level = DebugLevel.DEBUG if debug else DebugLevel.USER

        for player_entry in self.players:
            player_file = str(player_entry["file"])
            player = player_entry.get("player")
            authors = list(player_entry.get("authors", []))
            load_error = player_entry.get("load_error")

            if load_error is not None or player is None:
                self.results.append(
                    {
                        "player_file": player_file,
                        "player_name": Path(player_file).stem,
                        "authors": ";".join(authors),
                        "score": 0.0,
                        "grade": 0.0,
                        "status": "load_error",
                        "error": str(load_error or "Unknown load error."),
                        "n_trials": len(self.trial_definitions),
                    },
                )
                continue

            try:
                score = self._grade_player(player=player, debug_level=debug_level)
                self.results.append(
                    {
                        "player_file": player_file,
                        "player_name": player.name(),
                        "authors": ";".join(authors),
                        "score": score,
                        "grade": score,
                        "status": "graded",
                        "error": "",
                        "n_trials": len(self.trial_definitions),
                    },
                )
            except Exception as error:  # pragma: no cover - exercised by integration-oriented test paths
                self.results.append(
                    {
                        "player_file": player_file,
                        "player_name": player.name(),
                        "authors": ";".join(authors),
                        "score": 0.0,
                        "grade": 0.0,
                        "status": "grading_error",
                        "error": f"{type(error).__name__}: {error}",
                        "n_trials": len(self.trial_definitions),
                    },
                )

        return self.results

    def _grade_player(self, player: Player, debug_level: DebugLevel) -> float:
        """Compute the final score for one player across all configured trials."""
        weighted_trial_scores: list[float] = []
        for configuration, repetitions, trial_value in self.trial_definitions:
            rules = self.game.generate_rules(configuration)
            n_players = max(1, int(rules.n_players()))
            trial = Trial()
            trial.configuration = TrialConfiguration(
                match_configuration=self.match_configuration,
                trialing_player_index=PlayerIndex(0),
                rules=rules,
                players=[player for _ in range(n_players)],
                repetitions=repetitions,
                description=f"Configuration {configuration}",
                game_configuration=configuration,
                value=trial_value,
                min_score=float(self.match_configuration.score_limits[0]),
                max_score=float(self.match_configuration.score_limits[1]),
            )
            trial.match_reports = []
            trial.trial(debug_level=debug_level)
            weighted_trial_scores.append(trial.score() * trial_value)

        if not weighted_trial_scores:
            return 0.0
        return float(sum(weighted_trial_scores))

    def write_csv(self, filename: str) -> None:
        """Write graded rows to one CSV file.

        Args:
            filename: Destination CSV path.

        Returns:
            None.
        """
        if not self.results:
            _ = self.grade_all(debug=False)

        output_path = Path(filename)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fields = ["player_file", "player_name", "authors", "score", "grade", "status", "error", "n_trials"]

        with output_path.open("w", encoding="utf-8", newline="") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fields)
            writer.writeheader()
            for row in self.results:
                serialized_row = dict(row)
                serialized_row["score"] = self._safe_float(serialized_row.get("score"))
                serialized_row["grade"] = self._safe_float(serialized_row.get("grade"))
                writer.writerow(serialized_row)

    def _safe_float(self, value: object) -> float:
        """Convert one numeric-like value to a finite float for CSV serialization."""
        try:
            casted = float(value)
        except (TypeError, ValueError):
            return 0.0
        return 0.0 if not math.isfinite(casted) else casted
