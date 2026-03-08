"""Defines the interactive streamlit executable for playing IArena games."""
# pylint: disable=too-many-lines  # TODO: review

from __future__ import annotations

import inspect
import tempfile
from types import NoneType
from typing import Any, ClassVar, TypeVar, cast, get_args, get_origin

import yaml

from iarena.gaming.Configuration import Configuration
from iarena.gaming.Game import Game
from iarena.gaming.GameGovernor import GameGovernor
from iarena.gaming.Position import Position
from iarena.playing.HumanPlayer import HumanPlayer
from iarena.playing.LoadPlayer import LoadPlayer
from iarena.playing.Player import Player
from iarena.playing.PlayerIndex import PlayerIndex
from iarena.playing.StreamlitPlayer import StreamlitPlayer
from iarena.scoring.Score import Score
from iarena.visualizing.streamlit_frontend.StreamlitContainer import StreamlitContainer
from iarena.visualizing.streamlit_frontend.StreamlitSession import StreamlitSession
from iarena.visualizing.streamlit_frontend.StreamlitView import StreamlitView

from .MainApp import MainApp
from .StreamlitApplicationState import StreamlitApplicationState

T = TypeVar("T")


class StreamlitApplication:
    """Streamlit executable orchestrating game selection and UI rendering.

    Purpose:
        Provide a complete streamlit application to select one game, configure
        runtime options, and play/review matches.
    How it works:
        Uses session-state keys as a finite state machine and advances gameplay
        turn-by-turn by combining `Game`, `Rules`, `Player`, and `StreamlitView`.
    Used for:
        Browser-based interactive gameplay and replay workflows.
    Public Attributes:
        main_app (MainApp): Main panel holder for streamlit page composition.
        view (StreamlitView | None): Active streamlit view for the initialized run.
    """

    _DEFAULT_SCORE_LIMITS: ClassVar[tuple[Score, Score]] = (Score(-1_000_000_000.0), Score(1_000_000_000.0))

    def __init__(
        self,
        *,
        max_turns: int = 500,
        max_turn_time_s: float = 120.0,
        max_total_time_s: float = 3_600.0,
    ) -> None:
        """Initialize one streamlit application instance.

        Args:
            max_turns: Maximum number of turns allowed in one match.
            max_turn_time_s: Turn timeout budget in seconds.
            max_total_time_s: Match timeout budget in seconds.

        Returns:
            None.
        """
        self.max_turns = max_turns
        self.max_turn_time_s = max_turn_time_s
        self.max_total_time_s = max_total_time_s

        self.main_app = MainApp()
        self.view: StreamlitView | None = None

        self._state_key = "streamlit_app_state"
        self._game_key = "streamlit_selected_game"
        self._runtime_key = "streamlit_runtime"
        self._max_turns_key = "streamlit_max_turns"
        self._review_step_key = "streamlit_review_step"
        self._review_slider_key = "streamlit_review_slider_step"
        self._autoplay_key = "streamlit_review_autoplay"

    def _supports_streamlit_renderer(self, game: Game) -> bool:
        """Return whether a game exposes at least one streamlit renderer class.

        Args:
            game: Candidate game object to evaluate.

        Returns:
            bool: `True` when at least one renderer is a `StreamlitView`.
        """
        renderers = game.get_renderers(
            requirements=lambda renderer_cls: isinstance(renderer_cls, type)
            and issubclass(renderer_cls, StreamlitView),
        )
        return bool(renderers)

    def _streamlit_renderer_classes(self, game: Game) -> list[type[StreamlitView]]:
        """Return streamlit renderer classes available for one game.

        Args:
            game: Game object whose renderer classes should be listed.

        Returns:
            list[type[StreamlitView]]: Sorted streamlit renderer classes.
        """
        renderers = game.get_renderers(
            requirements=lambda renderer_cls: isinstance(renderer_cls, type)
            and issubclass(renderer_cls, StreamlitView),
        )
        return sorted(renderers, key=lambda renderer_cls: renderer_cls.__name__)

    def _streamlit_renderer_class(self, game: Game) -> type[StreamlitView]:
        """Return the selected streamlit renderer class for a game.

        Args:
            game: Game whose renderer class should be selected.

        Returns:
            type[StreamlitView]: Selected renderer class.
        """
        renderer_classes = self._streamlit_renderer_classes(game)
        if not renderer_classes:
            raise RuntimeError(f"Game '{game.name()}' does not provide streamlit renderers.")

        if len(renderer_classes) == 1:
            return renderer_classes[0]

        import streamlit as st

        labels = [renderer_cls.__name__ for renderer_cls in renderer_classes]
        selected_label = st.sidebar.selectbox("Renderer", labels, index=0, key="streamlit_renderer")
        selected_index = labels.index(selected_label)
        return renderer_classes[selected_index]

    def _available_games(self) -> list[Game]:
        """Return all registered games supporting streamlit rendering.

        Args:
            None.

        Returns:
            list[Game]: Sorted streamlit-compatible game objects.
        """
        return sorted(
            GameGovernor.get_games(requirement=self._supports_streamlit_renderer),
            key=lambda game: game.name(),
        )

    def _initialize_session_state(self, game_names: list[str]) -> None:
        """Ensure required streamlit session-state keys are initialized.

        Args:
            game_names: Ordered game names available in the current runtime.

        Returns:
            None.
        """
        import streamlit as st

        if self._state_key not in st.session_state:
            st.session_state[self._state_key] = StreamlitApplicationState.SELECTION.value
        if self._game_key not in st.session_state:
            st.session_state[self._game_key] = game_names[0]
        if self._runtime_key not in st.session_state:
            st.session_state[self._runtime_key] = None
        if self._review_step_key not in st.session_state:
            st.session_state[self._review_step_key] = 0
        if self._review_slider_key not in st.session_state:
            st.session_state[self._review_slider_key] = 0
        if self._autoplay_key not in st.session_state:
            st.session_state[self._autoplay_key] = False

    def _set_app_state(self, state: StreamlitApplicationState) -> None:
        """Update the streamlit application state value.

        Args:
            state: New state enum value.

        Returns:
            None.
        """
        import streamlit as st

        st.session_state[self._state_key] = state.value

    def _current_app_state(self) -> StreamlitApplicationState:
        """Return the current streamlit application state enum value.

        Args:
            None.

        Returns:
            StreamlitApplicationState: Current state value from session state.
        """
        import streamlit as st

        raw_state = st.session_state.get(self._state_key, StreamlitApplicationState.SELECTION.value)
        return StreamlitApplicationState(raw_state)

    def _reset_runtime(self) -> None:
        """Reset runtime-related session-state keys to pre-initialization values.

        Args:
            None.

        Returns:
            None.
        """
        import streamlit as st

        st.session_state[self._runtime_key] = None
        st.session_state[self._review_step_key] = 0
        st.session_state[self._review_slider_key] = 0
        st.session_state[self._autoplay_key] = False
        st.session_state.pop("selected_movement", None)

    def ask_for_game(self) -> Game:
        """Request and return the selected game from streamlit sidebar widgets.

        Args:
            None.

        Returns:
            Game: Selected game compatible with streamlit rendering.
        """
        import streamlit as st

        games = self._available_games()
        if not games:
            raise RuntimeError("No streamlit-compatible games are registered in GameGovernor.")

        game_names = [game.name() for game in games]
        current_name = st.session_state.get(self._game_key, game_names[0])
        if current_name not in game_names:
            current_name = game_names[0]

        selected_name = st.sidebar.selectbox(
            "Game",
            game_names,
            index=game_names.index(current_name),
            key="streamlit_game_selector",
        )
        st.session_state[self._game_key] = selected_name
        return games[game_names.index(selected_name)]

    def _configuration_classes(self, game: Game) -> list[type[Configuration]]:
        """Return configuration classes available for a game.

        Args:
            game: Game object whose configuration classes should be listed.

        Returns:
            list[type[Configuration]]: Sorted configuration classes.
        """
        configurations = game.get_configurations(
            requirements=lambda configuration_cls: isinstance(configuration_cls, type),
        )
        return sorted(configurations, key=lambda configuration_cls: configuration_cls.__name__)

    def _default_configuration(self, game: Game, configuration_cls: type[Configuration]) -> Configuration:
        """Build and return one default configuration object.

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
        except Exception as error:
            raise RuntimeError(f"Cannot derive default configuration for '{configuration_cls.__name__}'.") from error

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

    def _parse_text_value(self, raw_text: str, target_type: Any) -> Any:
        """Parse one raw text value into one typed value.

        Args:
            raw_text: Raw widget input text.
            target_type: Type hint used as conversion target.

        Returns:
            Any: Parsed and coerced value.
        """
        if target_type is str:
            return raw_text
        parsed_value = yaml.safe_load(raw_text)
        return self._coerce_value(target_type, parsed_value)

    def _render_constructor_configuration(
        self,
        configuration_cls: type[Configuration],
        *,
        key_prefix: str,
    ) -> Configuration:
        """Render constructor-driven widgets and build one configuration object.

        Args:
            configuration_cls: Configuration class to instantiate.
            key_prefix: Prefix used to namespace widget keys.

        Returns:
            Configuration: Built configuration object.
        """
        import streamlit as st

        signature = inspect.signature(configuration_cls.__init__)
        constructor_kwargs: dict[str, Any] = {}

        for parameter_name, parameter in signature.parameters.items():
            if parameter_name == "self":
                continue

            has_default = parameter.default is not inspect._empty
            default_value = parameter.default if has_default else ""
            raw_value = st.text_input(
                f"{parameter_name}",
                value=str(default_value),
                key=f"{key_prefix}_{parameter_name}",
            )
            if raw_value.strip() == "" and has_default:
                constructor_kwargs[parameter_name] = parameter.default
                continue
            constructor_kwargs[parameter_name] = self._parse_text_value(raw_value, parameter.annotation)

        return configuration_cls(**constructor_kwargs)

    def _render_hook_configuration(self, game: Game, *, key_prefix: str) -> Configuration:
        """Render widgets from a game-specific streamlit configuration hook.

        Args:
            game: Selected game exposing `streamlit_prompt_configuration`.
            key_prefix: Prefix used to namespace widget keys.

        Returns:
            Configuration: Configuration created by the game hook.
        """
        import streamlit as st

        hook = getattr(game, "streamlit_prompt_configuration", None)
        if not callable(hook):
            raise RuntimeError(f"Game '{game.name()}' does not expose `streamlit_prompt_configuration`.")

        signature = inspect.signature(hook)
        kwargs: dict[str, Any] = {}

        for parameter_name, parameter in signature.parameters.items():
            if parameter_name == "self":
                continue

            annotation = parameter.annotation
            has_default = parameter.default is not inspect._empty
            default_value = parameter.default if has_default else None
            widget_key = f"{key_prefix}_{parameter_name}"

            if annotation is int:
                initial_value = int(default_value if default_value is not None else 0)
                kwargs[parameter_name] = int(
                    st.number_input(parameter_name, min_value=0, step=1, value=initial_value, key=widget_key),
                )
                continue

            if annotation is float:
                initial_float_value = float(default_value if default_value is not None else 0.0)
                kwargs[parameter_name] = float(
                    st.number_input(parameter_name, value=initial_float_value, key=widget_key),
                )
                continue

            if annotation is bool:
                initial_value = bool(default_value) if has_default else False
                kwargs[parameter_name] = bool(
                    st.checkbox(parameter_name, value=initial_value, key=widget_key),
                )
                continue

            raw_default = "" if default_value is None else str(default_value)
            raw_value = st.text_input(parameter_name, value=raw_default, key=widget_key)
            kwargs[parameter_name] = self._parse_text_value(raw_value, annotation)

        return hook(**kwargs)

    def _configuration_from_yaml_text(
        self,
        configuration_cls: type[Configuration],
        yaml_text: str,
    ) -> Configuration:
        """Build one configuration from YAML text content.

        Args:
            configuration_cls: Target configuration class.
            yaml_text: YAML text content entered or uploaded in UI.

        Returns:
            Configuration: Parsed configuration object.
        """
        payload = yaml.safe_load(yaml_text) if yaml_text.strip() else {}
        if payload is None:
            payload = {}
        if not isinstance(payload, dict):
            raise TypeError("YAML configuration root must be a mapping.")
        return configuration_cls.from_dict(payload)

    def _resolve_configuration(self, game: Game) -> Configuration:
        """Render configuration widgets and return the selected configuration.

        Args:
            game: Selected game object.

        Returns:
            Configuration: Selected game configuration.
        """
        import streamlit as st

        configuration_classes = self._configuration_classes(game)
        if not configuration_classes:
            raise RuntimeError(f"Game '{game.name()}' does not expose any configuration class.")

        selected_configuration_cls = configuration_classes[0]
        if len(configuration_classes) > 1:
            class_names = [configuration_cls.__name__ for configuration_cls in configuration_classes]
            selected_name = st.selectbox("Configuration class", class_names, index=0, key="streamlit_config_class")
            selected_configuration_cls = configuration_classes[class_names.index(selected_name)]

        mode = st.radio(
            "Configuration source",
            ["Game controls", "YAML"],
            index=0,
            key="streamlit_configuration_mode",
        )

        if mode == "YAML":
            uploaded_file = st.file_uploader(
                "YAML configuration file",
                type=["yaml", "yml"],
                key="streamlit_configuration_file",
            )
            raw_yaml = ""
            if uploaded_file is not None:
                raw_yaml = uploaded_file.getvalue().decode("utf-8")
            raw_yaml = st.text_area(
                "YAML content",
                value=raw_yaml,
                key="streamlit_configuration_text",
                height=160,
            )
            if raw_yaml.strip() == "":
                configuration = self._default_configuration(game, selected_configuration_cls)
            else:
                configuration = self._configuration_from_yaml_text(selected_configuration_cls, raw_yaml)
        else:
            hook = getattr(game, "streamlit_prompt_configuration", None)
            if callable(hook):
                configuration = self._render_hook_configuration(game, key_prefix="streamlit_config_hook")
            else:
                configuration = self._render_constructor_configuration(
                    selected_configuration_cls,
                    key_prefix="streamlit_config_constructor",
                )

        self.main_app.left_column.set_configuration(configuration)
        return configuration

    def _player_classes(self, game: Game) -> list[type[Player]]:
        """Return supported player classes for streamlit application usage.

        Args:
            game: Selected game whose player classes should be listed.

        Returns:
            list[type[Player]]: Sorted supported player classes.
        """
        player_classes = game.get_players(
            requirements=lambda player_cls: isinstance(player_cls, type) and issubclass(player_cls, Player),
        )
        compatible_classes = sorted(
            [player_cls for player_cls in player_classes if self._is_streamlit_or_automatic_player(player_cls)],
            key=lambda player_cls: player_cls.__name__,
        )
        if not compatible_classes:
            raise RuntimeError(f"Game '{game.name()}' does not provide streamlit-compatible player classes.")
        return compatible_classes

    def _is_streamlit_or_automatic_player(self, player_cls: type[Player]) -> bool:
        """Return whether a player class is valid for streamlit application usage.

        Args:
            player_cls: Player class to validate.

        Returns:
            bool: `True` for streamlit-human players and automatic players.
        """
        if issubclass(player_cls, HumanPlayer):
            return issubclass(player_cls, StreamlitPlayer)
        return True

    def _default_player_index(self, player_classes: list[type[Player]]) -> int:
        """Return the recommended default player class index.

        Args:
            player_classes: Candidate player classes.

        Returns:
            int: Default selected class index.
        """
        for index, player_cls in enumerate(player_classes):
            if player_cls.__name__ == "PolyvalentRandomPlayer":
                return index
        for index, player_cls in enumerate(player_classes):
            if issubclass(player_cls, StreamlitPlayer):
                return index
        return 0

    def _selected_player_classes(self, game: Game, configuration: Configuration) -> list[type[Player] | Player]:
        """Render player selectors and return selected player entries.

        Args:
            game: Selected game object.
            configuration: Configuration used to derive required player count.

        Returns:
            list[type[Player] | Player]: Selected player classes or loaded players by slot.
        """
        import streamlit as st

        rules = game.generate_rules(configuration)
        player_classes = self._player_classes(game)
        default_index = self._default_player_index(player_classes)

        selected: list[type[Player] | Player] = []
        for slot_index in range(rules.n_players()):
            use_file = bool(
                st.checkbox(
                    f"Load player from file for slot {slot_index}",
                    value=False,
                    key=f"streamlit_player_use_file_slot_{slot_index}",
                ),
            )
            if use_file:
                uploaded_player_file = st.file_uploader(
                    f"Player file for slot {slot_index}",
                    type=["py"],
                    key=f"streamlit_player_file_slot_{slot_index}",
                )
                if uploaded_player_file is None:
                    raise ValueError(f"Please upload a Python player file for slot {slot_index}.")
                selected.append(self._load_player_from_uploaded_file(uploaded_player_file))
                continue

            selected.append(
                self.main_app.left_column.ask_for_player(
                    player_classes,
                    slot_index,
                    default_index=default_index,
                    key_prefix="streamlit_player_slot",
                ),
            )
        return selected

    def _load_player_from_file(self, file_path: str) -> Player:
        """Load one player instance from a Python file path.

        Args:
            file_path: Path to a Python source file that defines `PLAYER`.

        Returns:
            Player: Loaded player instance.
        """
        return LoadPlayer.from_file(file_path)

    def _load_player_from_uploaded_file(self, uploaded_file: Any) -> Player:
        """Load one player instance from a streamlit uploaded Python file.

        Args:
            uploaded_file: Streamlit uploaded file object exposing `getvalue`.

        Returns:
            Player: Loaded player instance.
        """
        source_bytes = bytes(uploaded_file.getvalue())
        with tempfile.NamedTemporaryFile(mode="wb", suffix=".py", delete=True) as temporary_file:
            temporary_file.write(source_bytes)
            temporary_file.flush()
            return self._load_player_from_file(temporary_file.name)

    def _instantiate_players(
        self,
        player_entries: list[type[Player] | Player],
        view: StreamlitView,
        rules: Any,
    ) -> list[Player]:
        """Instantiate selected players and bind view/session context.

        Args:
            player_entries: Player classes or loaded player instances selected in UI.
            view: Selected streamlit renderer.
            rules: Rules object used to initialize players.

        Returns:
            list[Player]: Instantiated players in turn order.
        """
        players: list[Player] = []
        for player_index, player_entry in enumerate(player_entries):
            player = player_entry() if isinstance(player_entry, type) else player_entry
            if isinstance(player, HumanPlayer):
                player.render = view
            player.starting_game(rules=rules, player_index=PlayerIndex(player_index))
            if isinstance(player, StreamlitPlayer):
                player.set_session_state(StreamlitSession())
            players.append(player)
        return players

    def _is_automatic_player(self, player: Player) -> bool:
        """Return whether the provided player instance is automatic.

        Args:
            player: Player instance to inspect.

        Returns:
            bool: `True` when player is not a human player.
        """
        return not isinstance(player, HumanPlayer)

    def _current_player(self, runtime: dict[str, Any]) -> Player:
        """Return the player whose turn is next in the given runtime.

        Args:
            runtime: Runtime dictionary stored in session state.

        Returns:
            Player: Player expected to act at the current position.
        """
        current_index = int(runtime["position"].next_player())
        return runtime["players"][current_index]

    def _initialize_runtime(
        self,
        game: Game,
        configuration: Configuration,
        player_entries: list[type[Player] | Player],
        max_turns: int,
    ) -> None:
        """Initialize one playable runtime from the selected settings.

        Args:
            game: Selected game.
            configuration: Selected configuration.
            player_entries: Selected player classes or loaded player instances.
            max_turns: Maximum number of allowed turns.

        Returns:
            None.
        """
        import streamlit as st

        rules = game.generate_rules(configuration)
        view = self._streamlit_renderer_class(game)()
        players = self._instantiate_players(player_entries=player_entries, view=view, rules=rules)
        position = rules.first_position()

        runtime = {
            "game": game,
            "configuration": configuration,
            "rules": rules,
            "view": view,
            "players": players,
            "position": position,
            "positions": [position],
            "movements": [],
            "turn_count": 0,
            "max_turns": max_turns,
            "finished": bool(rules.is_finished(position)),
            "last_error": None,
        }
        st.session_state[self._runtime_key] = runtime
        st.session_state[self._review_step_key] = 0
        st.session_state[self._review_slider_key] = 0
        st.session_state[self._autoplay_key] = False
        self.view = view

        if runtime["finished"]:
            self._set_app_state(StreamlitApplicationState.REVIEWING)
            return

        current_player = self._current_player(runtime)
        if self._is_automatic_player(current_player):
            self._set_app_state(StreamlitApplicationState.REVIEWING)
        else:
            self._set_app_state(StreamlitApplicationState.PLAYING)

    def _advance_one_turn(self, runtime: dict[str, Any]) -> bool:
        """Advance the runtime by one turn when possible.

        Args:
            runtime: Runtime dictionary stored in session state.

        Returns:
            bool: `True` when one movement was applied, otherwise `False`.
        """
        import streamlit as st

        if runtime["finished"]:
            return False

        if runtime["turn_count"] >= int(runtime["max_turns"]):
            runtime["finished"] = True
            return False

        rules = runtime["rules"]
        position = runtime["position"]
        player = self._current_player(runtime)

        try:
            if isinstance(player, StreamlitPlayer):
                session_payload = {str(key): value for key, value in st.session_state.items()}
                player.set_session_state(StreamlitSession(session_payload))

            movement = player.play(position)
            next_position = rules.next_position(position, movement)
        except Exception as error:
            error_message = str(error)
            if "object of type 'generator' has no len()" in error_message:
                error_message += (
                    " Hint: convert possible movements to a list before random choice, for example "
                    "`random.choice(list(pos.get_rules().possible_movements(pos)))`."
                )
            runtime["last_error"] = error_message
            return False

        runtime["position"] = next_position
        runtime["positions"].append(next_position)
        runtime["movements"].append(movement)
        runtime["turn_count"] += 1
        runtime["last_error"] = None

        st.session_state.pop("selected_movement", None)
        st.session_state[self._review_step_key] = len(runtime["positions"]) - 1

        if runtime["turn_count"] >= int(runtime["max_turns"]):
            runtime["finished"] = True
        else:
            runtime["finished"] = bool(rules.is_finished(next_position))

        return True

    def _score_for_position(self, runtime: dict[str, Any], position: Position) -> Score:
        """Return score of the current position for the next player.

        Args:
            runtime: Runtime dictionary with rules and player information.
            position: Position to evaluate.

        Returns:
            Score: Score value for the position.
        """
        scoreboard = runtime["rules"].get_score(position)
        try:
            return scoreboard.get_score(position.next_player())
        except Exception:
            scores = getattr(scoreboard, "_scores", {})
            if scores:
                return next(iter(scores.values()))
            return Score(0.0)

    def _sync_state_with_slider(self, runtime: dict[str, Any], step_index: int) -> None:
        """Update application state based on selected history slider step.

        Args:
            runtime: Runtime dictionary with position history.
            step_index: Selected history index.

        Returns:
            None.
        """
        import streamlit as st

        last_index = len(runtime["positions"]) - 1
        bounded_step = min(max(step_index, 0), last_index)
        st.session_state[self._review_step_key] = bounded_step

        if bounded_step < last_index:
            self._set_app_state(StreamlitApplicationState.REVIEWING)
            return

        if runtime["finished"]:
            self._set_app_state(StreamlitApplicationState.REVIEWING)
            return

        current_player = self._current_player(runtime)
        if self._is_automatic_player(current_player):
            self._set_app_state(StreamlitApplicationState.REVIEWING)
        else:
            self._set_app_state(StreamlitApplicationState.PLAYING)

    def _handle_review_controls(self, runtime: dict[str, Any]) -> bool:
        """Render reviewing controls and process actions.

        Args:
            runtime: Runtime dictionary with history and play state.

        Returns:
            bool: `True` when caller should trigger `st.rerun()`.
        """
        import streamlit as st

        should_rerun = False
        last_index = len(runtime["positions"]) - 1
        current_step = min(st.session_state.get(self._review_step_key, 0), last_index)

        play_col, pause_col = st.columns(2)
        if play_col.button("Play", key="streamlit_review_play", use_container_width=True):
            st.session_state[self._autoplay_key] = True
            should_rerun = True
        if pause_col.button("Pause", key="streamlit_review_pause", use_container_width=True):
            st.session_state[self._autoplay_key] = False

        back_col, fwd_col = st.columns(2)
        if back_col.button("Step backward", key="streamlit_review_back", use_container_width=True):
            st.session_state[self._autoplay_key] = False
            self._sync_state_with_slider(runtime, current_step - 1)
            should_rerun = True

        if fwd_col.button("Step forward", key="streamlit_review_forward", use_container_width=True):
            st.session_state[self._autoplay_key] = False
            if current_step < last_index:
                self._sync_state_with_slider(runtime, current_step + 1)
                should_rerun = True
            elif not runtime["finished"]:
                moved = self._advance_one_turn(runtime)
                self._sync_state_with_slider(runtime, len(runtime["positions"]) - 1)
                should_rerun = moved

        return should_rerun

    def _process_autoplay(self, runtime: dict[str, Any]) -> bool:
        """Advance reviewing autoplay by one step or one automatic turn.

        Args:
            runtime: Runtime dictionary with history and play state.

        Returns:
            bool: `True` when caller should trigger `st.rerun()`.
        """
        import streamlit as st

        if not st.session_state.get(self._autoplay_key, False):
            return False

        last_index = len(runtime["positions"]) - 1
        current_step = min(st.session_state.get(self._review_step_key, 0), last_index)

        if current_step < last_index:
            self._sync_state_with_slider(runtime, current_step + 1)
            return True

        if runtime["finished"]:
            st.session_state[self._autoplay_key] = False
            return False

        current_player = self._current_player(runtime)
        if self._is_automatic_player(current_player):
            moved = self._advance_one_turn(runtime)
            self._sync_state_with_slider(runtime, len(runtime["positions"]) - 1)
            if not moved:
                st.session_state[self._autoplay_key] = False
            return moved

        st.session_state[self._autoplay_key] = False
        self._set_app_state(StreamlitApplicationState.PLAYING)
        return True

    def _advance_automatic_until_stop(self, runtime: dict[str, Any]) -> bool:
        """Advance turns while the latest position belongs to an automatic player.

        Args:
            runtime: Runtime dictionary with history and play state.

        Returns:
            bool: `True` when at least one automatic turn was executed.
        """
        import streamlit as st

        moved_any = False

        while True:
            last_index = len(runtime["positions"]) - 1
            current_step = min(st.session_state.get(self._review_step_key, last_index), last_index)

            if current_step < last_index:
                break
            if runtime["finished"]:
                break

            current_player = self._current_player(runtime)
            if not self._is_automatic_player(current_player):
                break

            moved = self._advance_one_turn(runtime)
            if not moved:
                break
            moved_any = True

        self._sync_state_with_slider(runtime, len(runtime["positions"]) - 1)
        return moved_any

    def _render_runtime_panels(self, runtime: dict[str, Any], layout: dict[str, StreamlitContainer | Any]) -> bool:
        """Render runtime-dependent panels and apply live interaction effects.

        Args:
            runtime: Runtime dictionary in session state.
            layout: Layout container mapping from `MainApp.build_layout`.

        Returns:
            bool: `True` when caller should trigger `st.rerun()`.
        """
        import streamlit as st

        should_rerun = False
        state = self._current_app_state()

        last_index = len(runtime["positions"]) - 1
        selected_step = min(st.session_state.get(self._review_step_key, last_index), last_index)
        self._sync_state_with_slider(runtime, selected_step)
        state = self._current_app_state()

        current_position = runtime["positions"][selected_step]
        view = runtime["view"]

        position_container = layout["position"]
        movement_container = layout["movements"]
        score_container = layout["score"]

        if not isinstance(position_container, StreamlitContainer):
            raise TypeError("Invalid position container generated by MainApp.")
        if not isinstance(movement_container, StreamlitContainer):
            raise TypeError("Invalid movement container generated by MainApp.")
        if not isinstance(score_container, StreamlitContainer):
            raise TypeError("Invalid score container generated by MainApp.")

        self.main_app.central.render_position(view, current_position, position_container)

        native_movement_container = cast(
            Any,
            movement_container.container if movement_container.container is not None else st.container(),
        )
        with native_movement_container:
            if state == StreamlitApplicationState.REVIEWING:
                movement = runtime["movements"][selected_step - 1] if selected_step > 0 else None
                self.main_app.right_column.render_selected_movement(movement)
            else:
                current_player = self._current_player(runtime)
                if isinstance(current_player, StreamlitPlayer):
                    possible_movements = list(runtime["rules"].possible_movements(runtime["position"]))
                    selected_movement = self.main_app.right_column.render_possible_movements(
                        possible_movements,
                        interactive=True,
                    )
                    if selected_movement is not None:
                        st.session_state["selected_movement"] = selected_movement
                        moved = self._advance_one_turn(runtime)
                        self._sync_state_with_slider(runtime, len(runtime["positions"]) - 1)
                        should_rerun = moved
                else:
                    st.info(f"Current player '{current_player.name()}' is automatic.")

        native_score_container = cast(
            Any,
            score_container.container if score_container.container is not None else st.container(),
        )
        with native_score_container:
            score = self._score_for_position(runtime, current_position)
            st.write(f"Score: {float(score):.3f}")

        if runtime["last_error"]:
            st.error(runtime["last_error"])

        if runtime["finished"]:
            self._set_app_state(StreamlitApplicationState.REVIEWING)

        return should_rerun

    def main(self) -> None:  # pylint: disable=too-complex,too-many-statements  # TODO: review
        """Run the streamlit application entrypoint flow.

        Args:
            None.

        Returns:
            None.
        """
        import streamlit as st

        st.set_page_config(page_title="IArena", layout="wide")
        st.title("IArena")

        games = self._available_games()
        if not games:
            st.error("No streamlit-compatible games are registered in GameGovernor.")
            return

        game_names = [game.name() for game in games]
        self._initialize_session_state(game_names)

        st.sidebar.header("Game Selection")
        game = self.ask_for_game()

        previous_game_name = st.session_state.get("streamlit_previous_game")
        if previous_game_name != game.name():
            self._reset_runtime()
            st.session_state["streamlit_previous_game"] = game.name()
            self._set_app_state(StreamlitApplicationState.CONFIGURATION)

        layout = self.main_app.build_layout()

        st.sidebar.header("Configuration")
        configuration_tab, controls_tab = st.sidebar.tabs(["Configuration", "Controls"])

        with configuration_tab:
            with st.expander("Game configuration", expanded=True):
                try:
                    configuration = self._resolve_configuration(game)
                except Exception as error:
                    st.error(f"Configuration error: {error}")
                    configuration = self._default_configuration(game, self._configuration_classes(game)[0])
                    self.main_app.left_column.set_configuration(configuration)

            with st.expander("Player selection", expanded=True):
                try:
                    player_entries = self._selected_player_classes(game, configuration)
                except Exception as error:
                    st.error(f"Player configuration error: {error}")
                    player_entries = []

            with st.expander("Arena configuration", expanded=True):
                max_turns = int(
                    st.number_input(
                        "Maximum movements",
                        min_value=1,
                        step=1,
                        value=self.max_turns,
                        key=self._max_turns_key,
                    ),
                )

        runtime = st.session_state.get(self._runtime_key)
        with controls_tab:
            init_clicked = st.button("Init", key="streamlit_init", use_container_width=True)
            restart_clicked = st.button("Restart", key="streamlit_restart", use_container_width=True)

        if restart_clicked:
            self._reset_runtime()
            self._set_app_state(StreamlitApplicationState.SELECTION)
            st.rerun()

        if init_clicked:
            if not player_entries:
                st.error("At least one player must be selected before initialization.")
            else:
                self._initialize_runtime(
                    game=game,
                    configuration=configuration,
                    player_entries=player_entries,
                    max_turns=max_turns,
                )
                st.rerun()

        runtime = st.session_state.get(self._runtime_key)
        if runtime is None:
            preview_rules = game.generate_rules(configuration)
            preview_view = self._streamlit_renderer_class(game)()
            preview_position = preview_rules.first_position()
            preview_position_container = layout["position"]
            preview_movement_container = layout["movements"]
            preview_score_container = layout["score"]
            slider_container = cast(Any, layout["slider"])

            if not isinstance(preview_position_container, StreamlitContainer):
                raise TypeError("Invalid preview position container generated by MainApp.")
            if not isinstance(preview_movement_container, StreamlitContainer):
                raise TypeError("Invalid preview movement container generated by MainApp.")
            if not isinstance(preview_score_container, StreamlitContainer):
                raise TypeError("Invalid preview score container generated by MainApp.")

            preview_view.render_info(preview_rules, cast(Any, preview_position_container))
            self.main_app.central.render_position(preview_view, preview_position, preview_position_container)

            native_preview_movement_container = cast(
                Any,
                preview_movement_container.container
                if preview_movement_container.container is not None
                else st.container(),
            )
            with native_preview_movement_container:
                st.info("Initialize a match to start playing.")

            native_preview_score_container = cast(
                Any,
                preview_score_container.container if preview_score_container.container is not None else st.container(),
            )
            with native_preview_score_container:
                score = preview_rules.get_score(preview_position).get_score(preview_position.next_player())
                st.write(f"Score: {float(score):.3f}")

            with slider_container:
                st.caption("Step history will appear here after initialization.")
            return

        runtime = cast(dict[str, Any], runtime)
        self._advance_automatic_until_stop(runtime)

        if self._current_app_state() == StreamlitApplicationState.REVIEWING:
            with controls_tab:
                if self._handle_review_controls(runtime):
                    st.rerun()

        last_index = len(runtime["positions"]) - 1
        slider_container = cast(Any, layout["slider"])
        if last_index > 0:
            current_review_step = min(max(int(st.session_state.get(self._review_step_key, last_index)), 0), last_index)
            st.session_state[self._review_step_key] = current_review_step
            st.session_state[self._review_slider_key] = current_review_step
            with slider_container:
                selected_step = st.slider(
                    "Steps",
                    min_value=0,
                    max_value=last_index,
                    key=self._review_slider_key,
                )
        else:
            selected_step = 0
            with slider_container:
                if runtime["finished"]:
                    st.caption("No step history available for this match.")
                else:
                    st.caption("Step history will appear after the first movement.")
            st.session_state[self._review_slider_key] = 0
        self._sync_state_with_slider(runtime, selected_step)

        should_rerun = self._render_runtime_panels(runtime, layout)

        if self._process_autoplay(runtime):
            st.rerun()

        if should_rerun:
            st.rerun()
