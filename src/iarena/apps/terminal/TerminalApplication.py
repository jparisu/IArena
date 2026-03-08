"""Defines the interactive terminal executable for playing IArena games."""
# pylint: disable=too-many-lines  # TODO: review

from __future__ import annotations

import inspect
from collections.abc import Callable
from pathlib import Path
from types import NoneType
from typing import Any, ClassVar, TypeVar, get_args, get_origin

import yaml

from iarena.arening.Arena import Arena
from iarena.arening.ArenaFactory import ArenaFactory
from iarena.gaming.Configuration import Configuration
from iarena.gaming.Game import Game
from iarena.gaming.GameGovernor import GameGovernor
from iarena.gaming.Rules import Rules
from iarena.playing.HumanPlayer import HumanPlayer
from iarena.playing.LoadPlayer import LoadPlayer
from iarena.playing.Player import Player
from iarena.playing.PlayerIndex import PlayerIndex
from iarena.scoring.Score import Score
from iarena.scoring.ScoreBoard import ScoreBoard
from iarena.utilizing.reading.YamlReader import YamlReader
from iarena.utilizing.structuring.GenericSuiteParameter import GenericSuiteParameter
from iarena.visualizing.terminal_frontend.TerminalView import TerminalView

T = TypeVar("T")


class TerminalApplication:
    """Terminal executable orchestrating game setup and gameplay loop.

    Purpose:
        Provide a complete command-line application to select a game,
        configure it, select players, and run one match.
    How it works:
        Discovers terminal-compatible games through `GameGovernor`, prepares
        rules/players/view, and delegates turn execution to an arena.
    Used for:
        Local terminal gameplay and quick smoke testing of game integrations.
    Public Attributes:
        arena (Arena | None): Arena instance created for the current run.
        view (TerminalView | None): Terminal view selected for the current run.
    """

    arena: Arena | None
    view: TerminalView | None
    _DEFAULT_SCORE_LIMITS: ClassVar[tuple[Score, Score]] = (Score(-1_000_000_000.0), Score(1_000_000_000.0))

    def __init__(
        self,
        input_fnc: Callable[[str], str] = input,
        output_fnc: Callable[[str], None] = print,
        *,
        max_turns: int = 500,
        max_turn_time_s: float = 120.0,
        max_total_time_s: float = 3_600.0,
    ) -> None:
        """Initialize one terminal application instance.

        Args:
            input_fnc: Callable used to collect terminal input.
            output_fnc: Callable used to display terminal output.
            max_turns: Maximum number of turns allowed in one match.
            max_turn_time_s: Timeout budget in seconds for one turn.
            max_total_time_s: Timeout budget in seconds for the full match.

        Returns:
            None.
        """
        self.input_fnc = input_fnc
        self.output_fnc = output_fnc
        self.max_turns = max_turns
        self.max_turn_time_s = max_turn_time_s
        self.max_total_time_s = max_total_time_s

        self.arena = None
        self.view = None
        self._game: Game | None = None
        self._configuration: Configuration | None = None
        self._players: list[Player] = []

    def _supports_terminal_renderer(self, game: Game) -> bool:
        """Return whether a game exposes at least one terminal renderer class.

        Args:
            game: Candidate game object to evaluate.

        Returns:
            bool: `True` when at least one renderer is a `TerminalView`.
        """
        renderers = game.get_renderers(
            requirements=lambda renderer_cls: isinstance(renderer_cls, type) and issubclass(renderer_cls, TerminalView),
        )
        return bool(renderers)

    def _terminal_renderer_classes(self, game: Game) -> list[type[TerminalView]]:
        """Return terminal renderer classes available for a game.

        Args:
            game: Game object whose renderer classes should be listed.

        Returns:
            list[type[TerminalView]]: Sorted terminal renderer classes.
        """
        renderers = game.get_renderers(
            requirements=lambda renderer_cls: isinstance(renderer_cls, type) and issubclass(renderer_cls, TerminalView),
        )
        return sorted(renderers, key=lambda renderer_cls: renderer_cls.__name__)

    def _ask_choice(self, title: str, options: list[str], *, default_index: int | None = None) -> int:
        """Ask the user to choose one option by index.

        Args:
            title: Prompt title displayed before options.
            options: Ordered option labels to choose from.
            default_index: Optional fallback index when user submits blank input.

        Returns:
            int: Index selected by the user.
        """
        if not options:
            raise ValueError("Cannot ask for a choice from an empty option list.")

        self.output_fnc(title)
        for option_index, option in enumerate(options):
            self.output_fnc(f"  [{option_index}] {option}")

        while True:
            prompt = "Choose an index"
            if default_index is not None:
                prompt += f" [{default_index}]"
            raw_value = self.input_fnc(f"{prompt}: ").strip()

            if raw_value == "" and default_index is not None:
                return default_index

            if raw_value.isdigit():
                selected_index = int(raw_value)
                if 0 <= selected_index < len(options):
                    return selected_index

            self.output_fnc("Invalid selection. Please choose a valid numeric index.")

    def ask_for_game(self) -> Game:
        """Request and return the selected game from terminal input.

        Args:
            None.

        Returns:
            Game: Selected game compatible with terminal rendering.
        """
        available_games = sorted(
            GameGovernor.get_games(requirement=self._supports_terminal_renderer),
            key=lambda game: game.name(),
        )
        if not available_games:
            raise RuntimeError("No terminal-compatible games are registered in GameGovernor.")

        selected_index = self._ask_choice(
            "Select a game:",
            [game.name() for game in available_games],
            default_index=0,
        )
        selected_game = available_games[selected_index]
        self._game = selected_game
        return selected_game

    def _ask_configuration_class(self, game: Game) -> type[Configuration]:
        """Request one configuration class from the selected game.

        Args:
            game: Game whose configuration classes should be listed.

        Returns:
            type[Configuration]: Selected configuration class.
        """
        configuration_classes = sorted(
            game.get_configurations(requirements=lambda configuration_cls: isinstance(configuration_cls, type)),
            key=lambda configuration_cls: configuration_cls.__name__,
        )
        if not configuration_classes:
            raise RuntimeError(f"Game '{game.name()}' does not expose any configuration class.")

        if len(configuration_classes) == 1:
            return configuration_classes[0]

        selected_index = self._ask_choice(
            "Select a configuration type:",
            [configuration_cls.__name__ for configuration_cls in configuration_classes],
            default_index=0,
        )
        return configuration_classes[selected_index]

    def _ask_configuration_from_file(self, configuration_cls: type[Configuration]) -> Configuration:
        """Request a YAML file path and load one configuration from it.

        Args:
            configuration_cls: Target configuration class used for parsing.

        Returns:
            Configuration: Parsed concrete configuration object.
        """
        while True:
            raw_path = self.input_fnc("Configuration YAML path: ").strip()
            if raw_path == "":
                self.output_fnc("A YAML file path is required.")
                continue

            path = Path(raw_path)
            if not path.exists():
                self.output_fnc(f"File not found: {path}")
                continue

            parameter_or_suite = YamlReader.read_parameter_or_suite(
                path=path,
                parameter_cls=configuration_cls,
                treat_plain_lists_as_suite=False,
            )
            if isinstance(parameter_or_suite, GenericSuiteParameter):
                generated_configurations = list(parameter_or_suite.individual_parameters())
                if not generated_configurations:
                    raise ValueError("Configuration suite generated no concrete configurations.")
                if len(generated_configurations) == 1:
                    return generated_configurations[0]

                selected_index = self._ask_choice(
                    "Select one generated configuration:",
                    [f"Combination {index}" for index in range(len(generated_configurations))],
                    default_index=0,
                )
                return generated_configurations[selected_index]

            return parameter_or_suite

    def _coerce_value(self, target_type: Any, value: Any) -> Any:  # pylint: disable=too-complex  # TODO: review
        """Coerce one value into the provided target type when possible.

        Args:
            target_type: Type hint or runtime type used as coercion target.
            value: Input value to convert.

        Returns:
            Any: Converted value compatible with `target_type` when possible.
        """
        if value is None:
            return None
        if target_type in (Any, object, inspect._empty):
            return value

        origin = get_origin(target_type)
        args = get_args(target_type)

        if origin is None:
            if isinstance(target_type, type):
                if isinstance(value, target_type):
                    return value
                if target_type is bool:
                    if isinstance(value, bool):
                        return value
                    if isinstance(value, str):
                        normalized = value.strip().lower()
                        if normalized in {"true", "1", "yes", "y", "on"}:
                            return True
                        if normalized in {"false", "0", "no", "n", "off"}:
                            return False
                    raise ValueError(f"Cannot convert '{value}' to bool.")
                return target_type(value)
            return value

        if origin is list:
            if len(args) != 1:
                return list(value)
            if not isinstance(value, list):
                raise ValueError(f"Expected a list value, got {type(value).__name__}.")
            return [self._coerce_value(args[0], item) for item in value]

        if origin is tuple:
            if not isinstance(value, (list, tuple)):
                raise ValueError(f"Expected a tuple/list value, got {type(value).__name__}.")
            if len(args) == 2 and args[1] is Ellipsis:
                return tuple(self._coerce_value(args[0], item) for item in value)
            if len(args) != len(value):
                raise ValueError("Tuple value length does not match the annotated tuple arity.")
            return tuple(self._coerce_value(item_type, item) for item_type, item in zip(args, value, strict=True))

        if origin in (set, frozenset):
            if len(args) != 1:
                return origin(value)
            return origin(self._coerce_value(args[0], item) for item in value)

        if origin in (dict,):
            if len(args) != 2:
                return dict(value)
            if not isinstance(value, dict):
                raise ValueError(f"Expected a dict value, got {type(value).__name__}.")
            return {
                self._coerce_value(args[0], key): self._coerce_value(args[1], item_value)
                for key, item_value in value.items()
            }

        if origin is not None and args:
            non_none_types = [arg for arg in args if arg is not NoneType]
            for candidate_type in non_none_types:
                try:
                    return self._coerce_value(candidate_type, value)
                except (TypeError, ValueError):
                    continue
            return value

        return value

    def _parse_input_value(self, raw_text: str, target_type: Any) -> Any:
        """Parse one raw terminal input string into a typed value.

        Args:
            raw_text: Raw user input text.
            target_type: Type hint used to parse/coerce the input value.

        Returns:
            Any: Parsed and coerced value.
        """
        if target_type is str:
            return raw_text
        parsed_value = yaml.safe_load(raw_text)
        return self._coerce_value(target_type, parsed_value)

    def _build_configuration_from_signature(
        self,
        configuration_cls: type[Configuration],
        *,
        defaults_only: bool,
    ) -> Configuration:
        """Build one configuration by inspecting constructor parameters.

        Args:
            configuration_cls: Configuration class to instantiate.
            defaults_only: When `True`, only constructor defaults are allowed.

        Returns:
            Configuration: Constructed configuration instance.
        """
        signature = inspect.signature(configuration_cls.__init__)
        constructor_kwargs: dict[str, Any] = {}

        for parameter_name, parameter in signature.parameters.items():
            if parameter_name == "self":
                continue

            has_default = parameter.default is not inspect._empty
            if defaults_only and not has_default:
                raise ValueError(
                    "Cannot derive default configuration because constructor "
                    f"parameter '{parameter_name}' has no default value.",
                )

            if defaults_only and has_default:
                constructor_kwargs[parameter_name] = parameter.default
                continue

            default_suffix = f" [default: {parameter.default}]" if has_default else ""
            while True:
                raw_value = self.input_fnc(f"  - {parameter_name}{default_suffix}: ").strip()
                if raw_value == "" and has_default:
                    constructor_kwargs[parameter_name] = parameter.default
                    break
                if raw_value == "" and not has_default:
                    self.output_fnc("This field is required.")
                    continue

                try:
                    constructor_kwargs[parameter_name] = self._parse_input_value(raw_value, parameter.annotation)
                    break
                except (TypeError, ValueError) as error:
                    self.output_fnc(f"Invalid value for '{parameter_name}': {error}")

        return configuration_cls(**constructor_kwargs)

    def _ask_configuration_from_prompt(self, game: Game, configuration_cls: type[Configuration]) -> Configuration:
        """Request one configuration through a guided terminal workflow.

        Args:
            game: Game object that may expose guided configuration hooks.
            configuration_cls: Fallback configuration class for generic prompting.

        Returns:
            Configuration: Configuration chosen through guided prompts.
        """
        prompt_hook = getattr(game, "terminal_prompt_configuration", None)
        if callable(prompt_hook):
            return prompt_hook(self.input_fnc, self.output_fnc)
        self.output_fnc("Guided game-specific prompt is unavailable, using generic constructor prompts.")
        return self._build_configuration_from_signature(configuration_cls, defaults_only=False)

    def _ask_default_configuration(self, game: Game, configuration_cls: type[Configuration]) -> Configuration:
        """Build and return one default configuration.

        Args:
            game: Game object that may expose a default-configuration hook.
            configuration_cls: Fallback configuration class when no hook exists.

        Returns:
            Configuration: Default configuration object.
        """
        default_hook = getattr(game, "default_configuration", None)
        if callable(default_hook):
            return default_hook()

        try:
            return configuration_cls.from_dict({})
        except Exception:
            return self._build_configuration_from_signature(configuration_cls, defaults_only=True)

    def ask_for_configuration(self) -> Configuration:
        """Request and return the selected game configuration.

        Args:
            None.

        Returns:
            Configuration: Selected configuration object.
        """
        if self._game is None:
            raise RuntimeError("No selected game. Call `ask_for_game()` first.")

        configuration_cls = self._ask_configuration_class(self._game)
        selected_mode = self._ask_choice(
            "Select configuration mode:",
            [
                "Load from YAML file",
                "Guided terminal setup",
                "Use default configuration",
            ],
            default_index=2,
        )

        if selected_mode == 0:
            configuration = self._ask_configuration_from_file(configuration_cls)
        elif selected_mode == 1:
            configuration = self._ask_configuration_from_prompt(self._game, configuration_cls)
        else:
            configuration = self._ask_default_configuration(self._game, configuration_cls)

        self._configuration = configuration
        return configuration

    def _create_view(self, game: Game) -> TerminalView:
        """Create and configure one terminal view for the selected game.

        Args:
            game: Selected game whose terminal renderer should be instantiated.

        Returns:
            TerminalView: Instantiated and configured terminal view.
        """
        renderer_classes = self._terminal_renderer_classes(game)
        if not renderer_classes:
            raise RuntimeError(f"Game '{game.name()}' does not provide terminal renderers.")

        if len(renderer_classes) == 1:
            selected_renderer_cls = renderer_classes[0]
        else:
            selected_renderer_index = self._ask_choice(
                "Select a terminal renderer:",
                [renderer_cls.__name__ for renderer_cls in renderer_classes],
                default_index=0,
            )
            selected_renderer_cls = renderer_classes[selected_renderer_index]

        view = selected_renderer_cls()
        view.input_fnc = self.input_fnc
        view.output_fnc = self.output_fnc
        self.view = view
        return view

    def _player_classes(self, game: Game) -> list[type[Player]]:
        """Return supported player classes for terminal application usage.

        Args:
            game: Selected game whose player classes should be listed.

        Returns:
            list[type[Player]]: Sorted supported player classes.
        """
        player_classes = game.get_players(
            requirements=lambda player_cls: isinstance(player_cls, type) and issubclass(player_cls, Player),
        )
        allowed_player_classes = sorted(
            [player_cls for player_cls in player_classes if self._is_terminal_or_automatic_player(player_cls)],
            key=lambda player_cls: player_cls.__name__,
        )
        if not allowed_player_classes:
            raise RuntimeError(f"Game '{game.name()}' does not provide any player class.")
        return allowed_player_classes

    def _is_terminal_or_automatic_player(self, player_cls: type[Player]) -> bool:
        """Return whether a player class is valid for terminal application usage.

        Args:
            player_cls: Player class to validate.

        Returns:
            bool: `True` for terminal-human players and automatic players.
        """
        if issubclass(player_cls, HumanPlayer):
            return True
        return not issubclass(player_cls, HumanPlayer)

    def _player_label(self, player_cls: type[Player]) -> str:
        """Return a display label for one player class.

        Args:
            player_cls: Player class to describe.

        Returns:
            str: Display label including semantic category.
        """
        category = "terminal" if issubclass(player_cls, HumanPlayer) else "automatic"
        try:
            display_name = player_cls().name()
        except Exception:
            display_name = player_cls.__name__
        return f"{display_name} ({category})"

    def ask_for_players(self, rules: Rules) -> list[Player]:
        """Request and return selected players for all player slots.

        Args:
            rules: Rules object used to derive the number of required players.

        Returns:
            list[Player]: Instantiated players in turn order.
        """
        if self._game is None:
            raise RuntimeError("No selected game. Call `ask_for_game()` first.")
        if self.view is None:
            raise RuntimeError("No selected terminal view. View must be created before selecting players.")

        player_classes = self._player_classes(self._game)
        required_players = rules.n_players()
        selected_players: list[Player] = []

        for slot_index in range(required_players):
            selected_players.append(self.ask_for_player(slot_index=slot_index, player_classes=player_classes))

        self._players = selected_players
        return selected_players

    def ask_for_player(self, slot_index: int = 0, player_classes: list[type[Player]] | None = None) -> Player:
        """Request and return one selected player instance.

        Args:
            slot_index: Player slot index currently being configured.
            player_classes: Optional candidate player classes allowed for selection.

        Returns:
            Player: Instantiated selected player.
        """
        if self.view is None:
            raise RuntimeError("No selected terminal view. View must be created before selecting players.")

        available_player_classes = player_classes
        if available_player_classes is None:
            if self._game is None:
                raise RuntimeError("No selected game. Call `ask_for_game()` first.")
            available_player_classes = self._player_classes(self._game)

        selection_labels = [self._player_label(player_cls) for player_cls in available_player_classes]
        selection_labels.append("load-player (from file)")
        selected_index = self._ask_choice(
            f"Select player for slot {slot_index}:",
            selection_labels,
            default_index=0,
        )
        if selected_index == len(available_player_classes):
            player_instance = self._ask_load_player_from_file(slot_index=slot_index)
        else:
            player_instance = available_player_classes[selected_index]()
        if isinstance(player_instance, HumanPlayer):
            player_instance.render = self.view
        return player_instance

    def _ask_load_player_from_file(self, slot_index: int) -> Player:
        """Request a Python file path and load one `LoadPlayer` instance from it.

        Args:
            slot_index: Player slot index currently being configured.

        Returns:
            Player: Loaded player instance.
        """
        while True:
            raw_path = self.input_fnc(f"Python player file path for slot {slot_index}: ").strip()
            if raw_path == "":
                self.output_fnc("A Python file path is required.")
                continue
            try:
                return LoadPlayer.from_file(raw_path)
            except (FileNotFoundError, IsADirectoryError, ImportError, TypeError, ValueError) as error:
                self.output_fnc(f"Invalid player file: {error}")

    def _format_scoreboard(self, scoreboard: ScoreBoard, players: list[Player], rules: Rules) -> str:
        """Build a human-readable scoreboard text block.

        Args:
            scoreboard: Final scoreboard to format.
            players: Players associated with each scoreboard slot.
            rules: Rules object to resolve player count.

        Returns:
            str: Multi-line formatted scoreboard.
        """
        lines = ["Final Scoreboard", "-" * 40]
        best_player_index = 0
        best_score: Score | None = None
        for player_index in range(rules.n_players()):
            player_name = players[player_index].name() if player_index < len(players) else f"player-{player_index}"
            score = scoreboard.get_score(PlayerIndex(player_index))
            lines.append(f"  - P{player_index} {player_name}: {float(score):.3f}")
            if best_score is None or score > best_score:
                best_score = score
                best_player_index = player_index

        winner_name = (
            players[best_player_index].name() if best_player_index < len(players) else f"player-{best_player_index}"
        )
        lines.extend(
            [
                "-" * 40,
                f"Best score: P{best_player_index} {winner_name} ({float(best_score or Score(0.0)):.3f})",
            ],
        )
        return "\n".join(lines)

    def run(self) -> None:
        """Run the terminal application entrypoint flow.

        Args:
            None.

        Returns:
            None.
        """
        game = self.ask_for_game()
        configuration = self.ask_for_configuration()
        rules = game.generate_rules(configuration)
        view = self._create_view(game)
        players = self.ask_for_players(rules)

        view.render_info(rules, object())
        arena = ArenaFactory.create_arena(
            rules=rules,
            view=view,
            players=players,
            max_turns=self.max_turns,
            max_turn_time_s=self.max_turn_time_s,
            max_total_time_s=self.max_total_time_s,
            score_limits=self._DEFAULT_SCORE_LIMITS,
            store_logs=False,
        )
        self.arena = arena
        scoreboard = arena.play(rules=rules, players=players, view=view)

        final_position = getattr(arena, "_position", None)
        if final_position is not None:
            view.render_state(final_position, object())
        self.output_fnc(self._format_scoreboard(scoreboard, players, rules))

    def main(self) -> None:
        """Run this object as an executable application.

        Args:
            None.

        Returns:
            None.
        """
        self.run()
