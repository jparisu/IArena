"""Generic Streamlit rendering helpers for single-player optimization games."""

from __future__ import annotations

from collections.abc import MutableMapping, Sequence
from typing import Any, cast

from iarena.apping.AppingEngine import PlaybackController
from iarena.apping.AppingModels import OptimizationGamePage
from iarena.apping.StreamlitPlayModes import (
    render_playing_mode,
    render_reviewing_mode,
    reset_game_state,
    start_game,
    ui_state,
)
from iarena.interfacing.VisualGame import VisualGameState


class StreamlitGameIndex:
    """Store game pages exposed in the Streamlit app index."""

    def __init__(self, pages: Sequence[OptimizationGamePage]) -> None:
        """Initialize game index with unique page keys.

        Args:
            pages: Game pages to expose.

        Returns:
            None.
        """
        if not pages:
            raise ValueError("pages must contain at least one game")
        self._pages_by_key: dict[str, OptimizationGamePage] = {}
        for page in pages:
            if page.key in self._pages_by_key:
                raise ValueError(f"duplicate game key '{page.key}'")
            self._pages_by_key[page.key] = page

    def keys(self) -> tuple[str, ...]:
        """Return registered game keys in insertion order.

        Args:
            None.

        Returns:
            Tuple of game keys.
        """
        return tuple(self._pages_by_key.keys())

    def page_for(self, key: str) -> OptimizationGamePage:
        """Return one registered page by key.

        Args:
            key: Game key.

        Returns:
            Registered game page.
        """
        if key not in self._pages_by_key:
            available = ", ".join(self._pages_by_key.keys())
            raise KeyError(f"unknown game key '{key}'. Available: {available}")
        return self._pages_by_key[key]


def build_default_game_index() -> StreamlitGameIndex:
    """Build default game index shipped with the framework.

    Args:
        None.

    Returns:
        Game index including built-in games.
    """
    from iarena.gaming.GoldMine.GoldMineApping import build_goldmine_streamlit_page

    return StreamlitGameIndex(pages=[build_goldmine_streamlit_page()])


def _session_keys(session_namespace: str, game_key: str) -> tuple[str, str, str, str, str, str]:
    """Build state keys used by the Streamlit visual game lifecycle.

    Args:
        session_namespace: Prefix namespace for state keys.
        game_key: Selected game key.

    Returns:
        Tuple ``(replay_key, controller_key, interactive_key, state_key,
        selected_player_key, frame_delay_key)``.
    """
    prefix = f"{session_namespace}.{game_key}"
    return (
        f"{prefix}.replay",
        f"{prefix}.controller",
        f"{prefix}.interactive",
        f"{prefix}.state",
        f"{prefix}.selected_player",
        f"{prefix}.frame_delay_ms",
    )


def render_single_player_optimization_page(
    streamlit_api: Any,
    page: OptimizationGamePage,
    session_namespace: str = "iarena.apping",
) -> None:
    """Render one game page with visual states and panelized layout.

    Args:
        streamlit_api: Streamlit module-like API.
        page: Game page definition.
        session_namespace: Prefix namespace for Streamlit session state keys.

    Returns:
        None.
    """
    replay_key, controller_key, interactive_key, state_key, selected_player_key, frame_delay_key = _session_keys(
        session_namespace=session_namespace,
        game_key=page.key,
    )
    mutable_state = cast(MutableMapping[str, object], streamlit_api.session_state)

    if state_key not in mutable_state:
        mutable_state[state_key] = VisualGameState.CONFIGURING.value
    if frame_delay_key not in mutable_state:
        mutable_state[frame_delay_key] = int(page.autoplay_delay_seconds * 1_000)

    streamlit_api.subheader(page.title)
    configuration_column, position_column, movement_column = streamlit_api.columns([1, 2, 1])
    current_ui_state = ui_state(mutable_state=mutable_state, state_key=state_key)

    configuration_panel = configuration_column.expander("Configuration", expanded=True)
    general_panel = configuration_panel.expander("General configuration", expanded=True)
    configured_turn_limit = cast(
        int,
        general_panel.number_input(
            "Turn limit",
            min_value=1,
            max_value=500_000,
            value=page.turn_limit if page.turn_limit is not None else 5_000,
            step=1,
        ),
    )

    game_config_panel = configuration_panel.expander("Game configuration", expanded=True)
    configuration = page.visual_configuration(game_config_panel)
    player_factories = page.available_player_factories()
    player_options = tuple(player_factories.keys())
    selected_player_raw = mutable_state.get(selected_player_key, player_options[0])
    default_player_name = str(selected_player_raw) if selected_player_raw in player_options else player_options[0]
    default_player_index = player_options.index(default_player_name)

    player_panel = configuration_panel.expander("Player configuration", expanded=True)
    selected_player_name = cast(
        str,
        player_panel.selectbox("Player", options=player_options, index=default_player_index),
    )
    mutable_state[selected_player_key] = selected_player_name
    uploaded_file = player_panel.file_uploader("Upload player (.py)", type=["py"])

    controls_panel = configuration_panel.expander("Controls", expanded=True)
    if controls_panel.button("Reset"):
        reset_game_state(
            mutable_state,
            replay_key=replay_key,
            controller_key=controller_key,
            interactive_key=interactive_key,
            state_key=state_key,
        )
        if hasattr(streamlit_api, "rerun"):
            streamlit_api.rerun()
        return

    if current_ui_state is VisualGameState.CONFIGURING and controls_panel.button("Start"):
        start_game(
            mutable_state=mutable_state,
            page=page,
            selected_factory=player_factories[selected_player_name],
            uploaded_file=uploaded_file,
            configuration=configuration,
            replay_key=replay_key,
            controller_key=controller_key,
            interactive_key=interactive_key,
            state_key=state_key,
            turn_limit=configured_turn_limit,
        )
        if hasattr(streamlit_api, "rerun"):
            streamlit_api.rerun()
        return

    controller = cast(PlaybackController | None, mutable_state.get(controller_key))
    if current_ui_state is VisualGameState.REVIEWING and controller is not None:
        if controls_panel.button("Play"):
            controller.play()
        if controls_panel.button("Pause"):
            controller.pause()
        if controls_panel.button("Step backward"):
            controller.step_backward()
        if controls_panel.button("Step forward"):
            controller.step_forward()
        frame_delay_ms = cast(
            int,
            controls_panel.number_input(
                "Frame delay (ms)",
                min_value=10,
                max_value=10_000,
                value=cast(int, mutable_state[frame_delay_key]),
                step=10,
            ),
        )
        mutable_state[frame_delay_key] = frame_delay_ms

    movement_panel = movement_column.expander("Movements", expanded=True)
    scoreboard_panel = movement_column.expander("Scoreboard", expanded=False)
    current_ui_state = ui_state(mutable_state=mutable_state, state_key=state_key)

    if current_ui_state is VisualGameState.CONFIGURING:
        page.visual_description(position_column, configuration)
        movement_panel.write("Movement options will be shown once the game starts.")
        return

    if render_playing_mode(
        streamlit_api=streamlit_api,
        page=page,
        mutable_state=mutable_state,
        interactive_key=interactive_key,
        replay_key=replay_key,
        controller_key=controller_key,
        state_key=state_key,
        position_container=position_column,
        movement_container=movement_panel,
        scoreboard_container=scoreboard_panel,
    ):
        return

    if render_reviewing_mode(
        streamlit_api=streamlit_api,
        page=page,
        mutable_state=mutable_state,
        replay_key=replay_key,
        controller_key=controller_key,
        state_key=state_key,
        position_container=position_column,
        movement_container=movement_panel,
        scoreboard_container=scoreboard_panel,
        frame_delay_seconds=cast(int, mutable_state[frame_delay_key]) / 1_000.0,
    ):
        return

    page.visual_description(position_column, configuration)


def render_games_index_page(
    streamlit_api: Any,
    game_index: StreamlitGameIndex,
    session_namespace: str = "iarena.apping",
) -> None:
    """Render the main app page with one sidebar selector across games.

    Args:
        streamlit_api: Streamlit module-like API.
        game_index: Registered game pages.
        session_namespace: Prefix namespace for Streamlit session state keys.

    Returns:
        None.
    """
    selected_key = cast(
        str,
        streamlit_api.sidebar.radio(
            "Games",
            options=game_index.keys(),
            format_func=lambda game_key: game_index.page_for(game_key).title,
        ),
    )
    selected_page = game_index.page_for(selected_key)
    render_single_player_optimization_page(
        streamlit_api=streamlit_api,
        page=selected_page,
        session_namespace=session_namespace,
    )
