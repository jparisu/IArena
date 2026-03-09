"""Build exam instances from file-based grading configuration mappings."""

from __future__ import annotations

import itertools
from collections.abc import Mapping
from typing import Any

from iarena.gaming.Configuration import Configuration
from iarena.gaming.Game import Game
from iarena.gaming.GameGovernor import GameGovernor
from iarena.gaming.Oracle import Oracle
from iarena.grading.Exam import Exam
from iarena.grading.MatchConfiguration import MatchConfiguration
from iarena.grading.TrialConfiguration import TrialConfiguration
from iarena.playing.Player import Player
from iarena.playing.PlayerIndex import PlayerIndex
from iarena.scoring.Score import Score
from iarena.utilizing.reading.YamlReader import YamlReader


class ExamReader:
    """Factory that builds fully configured `Exam` objects from YAML files.

    Purpose:
        Convert external grading configuration payloads into executable exam
        instances with explicit trial configurations.
    How it is used:
        Autograder workflows call `from_file` or `from_mapping` to obtain one
        ready-to-run exam for a specific player.
    Why it exists:
        Centralizes file-schema parsing, game/oracle resolution, and trial
        configuration creation in one reusable component.
    """

    @classmethod
    def from_file(cls, configuration_file: str, player: Player) -> Exam:
        """Read one YAML configuration file and build an exam for the player.

        Args:
            configuration_file: Path to the grader YAML file.
            player: Player instance to grade.

        Returns:
            Exam: Exam containing fully expanded trial configurations.
        """
        return cls.from_mapping(configuration=YamlReader.read_mapping(configuration_file), player=player)

    @classmethod
    def from_mapping(cls, configuration: Mapping[str, Any], player: Player) -> Exam:
        """Build one exam from a mapping already loaded in memory.

        Args:
            configuration: Mapping that follows grader configuration schema.
            player: Player instance to grade.

        Returns:
            Exam: Configured exam object.
        """
        game = cls._resolve_game(configuration.get("game", ""))
        configuration_class = cls._resolve_configuration_class(game=game)
        oracle_class = cls._resolve_oracle_class(game=game)

        global_repetitions = max(1, int(configuration.get("repetitions", 1)))
        global_move_timeout_s = float(configuration.get("move_timeout_s", 1.0))
        global_total_timeout_s = float(configuration.get("total_timeout_s", 60.0))
        global_max_turns = int(configuration.get("max_moves", 10_000))
        trialing_player_index = PlayerIndex(int(configuration.get("trialing_player_index", 0)))

        trial_entries = cls._trial_entries(configuration=configuration)
        trial_configurations: list[TrialConfiguration] = []
        for trial_entry in trial_entries:
            trial_configurations.extend(
                cls._build_trial_configurations(
                    trial_entry=trial_entry,
                    configuration_class=configuration_class,
                    oracle_class=oracle_class,
                    player=player,
                    trialing_player_index=trialing_player_index,
                    global_repetitions=global_repetitions,
                    global_move_timeout_s=global_move_timeout_s,
                    global_total_timeout_s=global_total_timeout_s,
                    global_max_turns=global_max_turns,
                    global_min_score=configuration.get("min_score"),
                    global_max_score=configuration.get("max_score"),
                    game=game,
                ),
            )

        exam = Exam()
        exam.game = game
        exam.player = player
        exam.trial_configurations = trial_configurations
        exam.trials = []
        exam.trial_results = []
        exam.trial_value = []
        return exam

    @staticmethod
    def _resolve_game(game_name: object) -> Game:
        """Return one game from `GameGovernor` by the provided name.

        Args:
            game_name: Raw game identifier from external configuration.

        Returns:
            Game: Resolved game instance.
        """
        if not isinstance(game_name, str) or not game_name.strip():
            raise ValueError("Configuration requires a non-empty `game` field.")

        return GameGovernor.find_game(
            name=game_name.strip(),
            requirement=lambda _game: True,
            throw=True,
        )

    @staticmethod
    def _resolve_configuration_class(game: Game) -> type[Configuration]:
        """Resolve the configuration class to instantiate trial rules.

        Args:
            game: Game to inspect.

        Returns:
            type[Configuration]: Configuration class selected for the game.
        """
        configuration_classes = sorted(
            game.get_configurations(requirements=lambda candidate: isinstance(candidate, type)),
            key=lambda candidate: candidate.__name__,
        )
        if not configuration_classes:
            raise RuntimeError(f"Game '{game.name()}' does not expose any configuration class.")
        return configuration_classes[0]

    @staticmethod
    def _resolve_oracle_class(game: Game) -> type[Oracle]:
        """Resolve one oracle class that can benchmark the selected game.

        Args:
            game: Game to inspect.

        Returns:
            type[Oracle]: Oracle class selected for benchmark score limits.
        """
        oracle_classes = sorted(
            game.get_oracles(requirements=lambda candidate: isinstance(candidate, type)),
            key=lambda candidate: candidate.__name__,
        )
        if not oracle_classes:
            raise RuntimeError(f"Game '{game.name()}' does not expose any oracle class.")
        return oracle_classes[0]

    @staticmethod
    def _trial_entries(configuration: Mapping[str, Any]) -> list[Mapping[str, Any]]:
        """Return normalized trial entries from grader configuration mapping.

        Args:
            configuration: Root configuration mapping.

        Returns:
            list[Mapping[str, Any]]: Trial entries to expand.
        """
        trials = configuration.get("trials", configuration.get("reports", []))
        if not isinstance(trials, list):
            raise TypeError("Configuration field `trials` (or `reports`) must be a list.")

        if not trials:
            return [{}]

        normalized_trials: list[Mapping[str, Any]] = []
        for trial_entry in trials:
            if not isinstance(trial_entry, Mapping):
                raise TypeError("Each trial entry must be a mapping/object.")
            normalized_trials.append(trial_entry)
        return normalized_trials

    @classmethod
    def _build_trial_configurations(
        cls,
        trial_entry: Mapping[str, Any],
        configuration_class: type[Configuration],
        oracle_class: type[Oracle],
        player: Player,
        trialing_player_index: PlayerIndex,
        global_repetitions: int,
        global_move_timeout_s: float,
        global_total_timeout_s: float,
        global_max_turns: int,
        global_min_score: object,
        global_max_score: object,
        game: Game,
    ) -> list[TrialConfiguration]:
        """Expand one trial declaration into concrete trial configurations.

        Args:
            trial_entry: Trial declaration from YAML.
            configuration_class: Configuration class for the selected game.
            oracle_class: Oracle class used to infer score limits.
            player: Graded player instance.
            trialing_player_index: Player index to score.
            global_repetitions: Root repetition multiplier.
            global_move_timeout_s: Root per-move timeout.
            global_total_timeout_s: Root per-match timeout.
            global_max_turns: Root maximum turns per match.
            global_min_score: Root explicit minimum score override, if any.
            global_max_score: Root explicit maximum score override, if any.
            game: Selected game instance.

        Returns:
            list[TrialConfiguration]: Expanded trial configurations.
        """
        raw_base_args = trial_entry.get("args", {})
        if not isinstance(raw_base_args, Mapping):
            raise TypeError("Trial field `args` must be a mapping/object when provided.")
        base_args = dict(raw_base_args)

        per_trial_repetitions = max(1, int(trial_entry.get("repetitions", 1))) * global_repetitions
        trial_value = float(trial_entry.get("value", 1.0))
        move_timeout_s = float(trial_entry.get("move_timeout_s", global_move_timeout_s))
        total_timeout_s = float(trial_entry.get("total_timeout_s", global_total_timeout_s))
        max_turns = int(trial_entry.get("max_moves", global_max_turns))

        trial_match_min_score = cls._resolve_score_limit(
            local_override=trial_entry.get("min_score"),
            global_override=global_min_score,
            default=float("-inf"),
        )
        trial_match_max_score = cls._resolve_score_limit(
            local_override=trial_entry.get("max_score"),
            global_override=global_max_score,
            default=float("inf"),
        )
        if trial_match_min_score > trial_match_max_score:
            raise ValueError("Match score limits require `min_score` to be less than or equal to `max_score`.")

        match_configuration = MatchConfiguration(
            move_timeout_s=move_timeout_s,
            total_timeout_s=total_timeout_s,
            max_turns=max_turns,
            score_limits=(Score(trial_match_min_score), Score(trial_match_max_score)),
        )

        trial_configurations: list[TrialConfiguration] = []
        for expanded_args in cls._expand_args(base_args=base_args, multi_args=trial_entry.get("multi_args", {})):
            configuration = configuration_class.from_dict(expanded_args)
            trial_description = str(trial_entry.get("description", trial_entry.get("name", f"Configuration {configuration}")))
            rules = game.generate_rules(configuration)
            best_board, worst_board = oracle_class.reckon_solution_score(rules=rules)
            best_score = float(best_board.get_score(trialing_player_index))
            worst_score = float(worst_board.get_score(trialing_player_index))

            oracle_min_score = min(best_score, worst_score)
            oracle_max_score = max(best_score, worst_score)

            trial_min_score = cls._resolve_score_limit(
                local_override=trial_entry.get("min_score"),
                global_override=global_min_score,
                default=oracle_min_score,
            )
            trial_max_score = cls._resolve_score_limit(
                local_override=trial_entry.get("max_score"),
                global_override=global_max_score,
                default=oracle_max_score,
            )
            if trial_min_score > trial_max_score:
                raise ValueError("Trial score limits require `min_score` to be less than or equal to `max_score`.")

            n_players = max(1, int(rules.n_players()))
            trial_configurations.append(
                TrialConfiguration(
                    match_configuration=match_configuration,
                    trialing_player_index=trialing_player_index,
                    rules=rules,
                    players=[player for _ in range(n_players)],
                    repetitions=per_trial_repetitions,
                    description=trial_description,
                    game_configuration=configuration,
                    value=trial_value,
                    min_score=trial_min_score,
                    max_score=trial_max_score,
                ),
            )

        return trial_configurations

    @staticmethod
    def _resolve_score_limit(local_override: object, global_override: object, default: float) -> float:
        """Resolve one numeric score limit from local/global/default sources.

        Args:
            local_override: Trial-level override value.
            global_override: Global-level override value.
            default: Fallback value.

        Returns:
            float: Resolved score limit.
        """
        if local_override is not None:
            return float(local_override)
        if global_override is not None:
            return float(global_override)
        return float(default)

    @staticmethod
    def _expand_args(base_args: dict[str, Any], multi_args: object) -> list[dict[str, Any]]:
        """Expand one `args` dictionary against declared `multi_args` products.

        Args:
            base_args: Fixed arguments shared by all generated configurations.
            multi_args: Optional field mapping to one or many candidate values.

        Returns:
            list[dict[str, Any]]: Expanded configuration argument dictionaries.
        """
        if not isinstance(multi_args, Mapping):
            raise TypeError("Trial field `multi_args` must be a mapping/object when provided.")
        if not multi_args:
            return [dict(base_args)]

        normalized_multi_args: dict[str, list[Any]] = {}
        for field_name, values in multi_args.items():
            if isinstance(values, list):
                candidate_values = list(values)
            else:
                candidate_values = [values]
            if not candidate_values:
                raise ValueError(f"Trial field `multi_args.{field_name}` must not be empty.")
            normalized_multi_args[field_name] = candidate_values

        multi_arg_keys = list(normalized_multi_args.keys())
        multi_arg_domains = [normalized_multi_args[key] for key in multi_arg_keys]
        expanded_args: list[dict[str, Any]] = []
        for choices in itertools.product(*multi_arg_domains):
            args = dict(base_args)
            for field_name, value in zip(multi_arg_keys, choices, strict=False):
                args[field_name] = value
            expanded_args.append(args)
        return expanded_args
