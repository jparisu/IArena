"""Internal helpers for Streamlit visual game states and transitions."""

from __future__ import annotations

import time
from collections.abc import Mapping, MutableMapping
from dataclasses import dataclass
from typing import Any, cast

from iarena.apping.AppingEngine import (
    PlaybackController,
    load_player_class_from_python_source,
    read_uploaded_python_source,
    run_single_player_optimization_game,
)
from iarena.apping.AppingModels import (
    ConfigurationValues,
    OptimizationGamePage,
    OptimizationReplay,
    OptimizationReplayFrame,
    OptimizationViewState,
)
from iarena.arening.ArenaBehaviors import clone_score_board
from iarena.interfacing.IGameRules import IGameRules
from iarena.interfacing.IMovement import IMovement
from iarena.interfacing.IPlayer import IGraphicalPlayer, IPlayer
from iarena.interfacing.IPosition import IPosition
from iarena.interfacing.VisualGame import VisualGameState


@dataclass(slots=True)
class InteractiveArenaState:
    """Store mutable runtime state while a visual game is being played."""

    rules: IGameRules
    player: IPlayer
    position: IPosition
    frames: list[OptimizationReplayFrame]
    turn_limit: int | None

    def as_replay(self, end_reason: str | None = None) -> OptimizationReplay:
        """Build an immutable replay snapshot from interactive state.

        Args:
            end_reason: Optional game-end reason.

        Returns:
            Replay object with current frames and score.
        """
        return OptimizationReplay(
            rules=self.rules,
            frames=tuple(self.frames),
            final_score=clone_score_board(self.rules.current_score(self.position)),
            end_reason=end_reason,
        )


def build_player_from_selection(
    selected_factory: Any,
    uploaded_file: object | None,
) -> IPlayer:
    """Build player from selected factory and optional uploaded source.

    Args:
        selected_factory: Factory selected in UI.
        uploaded_file: Optional uploaded Python file.

    Returns:
        Instantiated player.
    """
    player = cast(IPlayer, selected_factory())
    if uploaded_file is None:
        return player
    player_class = load_player_class_from_python_source(read_uploaded_python_source(uploaded_file))
    return player_class()


def reset_game_state(
    mutable_state: MutableMapping[str, object],
    replay_key: str,
    controller_key: str,
    interactive_key: str,
    state_key: str,
) -> None:
    """Clear replay, interactive, and UI-state keys.

    Args:
        mutable_state: Streamlit session-state mapping.
        replay_key: Replay storage key.
        controller_key: Replay-controller key.
        interactive_key: Interactive-mode key.
        state_key: UI-state key.

    Returns:
        None.
    """
    mutable_state.pop(replay_key, None)
    mutable_state.pop(controller_key, None)
    mutable_state.pop(interactive_key, None)
    mutable_state[state_key] = VisualGameState.CONFIGURING.value


def start_game(
    mutable_state: MutableMapping[str, object],
    page: OptimizationGamePage,
    selected_factory: Any,
    uploaded_file: object | None,
    configuration: ConfigurationValues,
    replay_key: str,
    controller_key: str,
    interactive_key: str,
    state_key: str,
    turn_limit: int | None,
) -> None:
    """Start one game in autonomous or interactive visual mode.

    Args:
        mutable_state: Streamlit session-state mapping.
        page: Page definition for selected game.
        selected_factory: Selected player factory.
        uploaded_file: Optional uploaded player source file.
        configuration: Configuration values.
        replay_key: Replay storage key.
        controller_key: Replay-controller key.
        interactive_key: Interactive-mode key.
        state_key: UI-state key.
        turn_limit: Active turn limit from general configuration.

    Returns:
        None.
    """
    rules = page.build_rules(configuration)
    player = build_player_from_selection(selected_factory=selected_factory, uploaded_file=uploaded_file)
    reset_game_state(
        mutable_state,
        replay_key=replay_key,
        controller_key=controller_key,
        interactive_key=interactive_key,
        state_key=state_key,
    )

    if isinstance(player, IGraphicalPlayer):
        initial_position = rules.first_position()
        player.starting_game(rules=rules, player_index=0)
        initial_frame = OptimizationReplayFrame(
            turn_index=0,
            position=initial_position,
            score=clone_score_board(rules.current_score(initial_position)),
            movement_to_next=None,
        )
        mutable_state[interactive_key] = InteractiveArenaState(
            rules=rules,
            player=player,
            position=initial_position,
            frames=[initial_frame],
            turn_limit=turn_limit,
        )
        mutable_state[state_key] = VisualGameState.PLAYING.value
        return

    generated_replay = run_single_player_optimization_game(
        rules=rules,
        player=player,
        turn_limit=turn_limit if turn_limit is not None else page.turn_limit,
    )
    mutable_state[replay_key] = generated_replay
    mutable_state[controller_key] = PlaybackController(total_frames=len(generated_replay.frames))
    mutable_state[state_key] = VisualGameState.REVIEWING.value


def _ui_state_from_session(mutable_state: MutableMapping[str, object], state_key: str) -> VisualGameState:
    """Resolve current visual UI state from session storage.

    Args:
        mutable_state: Session-state mapping.
        state_key: Session key that stores current UI state.

    Returns:
        Current visual UI state.
    """
    raw_value = mutable_state.get(state_key, VisualGameState.CONFIGURING.value)
    if isinstance(raw_value, VisualGameState):
        return raw_value
    if isinstance(raw_value, str):
        try:
            return VisualGameState(raw_value)
        except ValueError:
            return VisualGameState.CONFIGURING
    return VisualGameState.CONFIGURING


def _build_interactive_view_state(interactive_state: InteractiveArenaState) -> OptimizationViewState:
    """Build view state object for the current interactive frame.

    Args:
        interactive_state: Mutable interactive game state.

    Returns:
        View state for rendering callbacks.
    """
    frame = interactive_state.frames[-1]
    replay_snapshot = interactive_state.as_replay()
    possible_movements = tuple(interactive_state.rules.possible_movements(interactive_state.position))
    return OptimizationViewState(
        replay=replay_snapshot,
        frame_index=frame.turn_index,
        frame=frame,
        possible_movements=possible_movements,
    )


def _apply_movement(interactive_state: InteractiveArenaState, movement: IMovement) -> None:
    """Apply one legal movement to interactive state and append new frame.

    Args:
        interactive_state: Mutable interactive game state.
        movement: Movement to apply.

    Returns:
        None.
    """
    rules = interactive_state.rules
    current_frame = interactive_state.frames[-1]
    interactive_state.frames[-1] = OptimizationReplayFrame(
        turn_index=current_frame.turn_index,
        position=current_frame.position,
        score=current_frame.score,
        movement_to_next=movement,
    )
    next_position = rules.next_position(movement, interactive_state.position)
    interactive_state.position = next_position
    interactive_state.frames.append(
        OptimizationReplayFrame(
            turn_index=current_frame.turn_index + 1,
            position=next_position,
            score=clone_score_board(rules.current_score(next_position)),
            movement_to_next=None,
        )
    )


def _interactive_finished(interactive_state: InteractiveArenaState) -> tuple[bool, str | None]:
    """Return whether the interactive session should transition to replay.

    Args:
        interactive_state: Mutable interactive game state.

    Returns:
        Tuple ``(finished, reason)``.
    """
    if interactive_state.rules.finished(interactive_state.position):
        return True, None
    if interactive_state.turn_limit is not None and (len(interactive_state.frames) - 1) >= interactive_state.turn_limit:
        return True, "turn_limit_reached"
    return False, None


def render_playing_mode(
    streamlit_api: Any,
    page: OptimizationGamePage,
    mutable_state: MutableMapping[str, object],
    interactive_key: str,
    replay_key: str,
    controller_key: str,
    state_key: str,
    position_container: Any,
    movement_container: Any,
    scoreboard_container: Any,
) -> bool:
    """Render and advance playing mode when a graphical player is active.

    Args:
        streamlit_api: Streamlit module-like API.
        page: Selected game page.
        mutable_state: Session-state mapping.
        interactive_key: Interactive-state key.
        replay_key: Replay-state key.
        controller_key: Controller-state key.
        state_key: UI-state key.
        position_container: Position panel container.
        movement_container: Movement panel container.
        scoreboard_container: Scoreboard panel container.

    Returns:
        ``True`` when playing mode is active; otherwise ``False``.
    """
    if _ui_state_from_session(mutable_state, state_key) is not VisualGameState.PLAYING:
        return False
    interactive_state = cast(InteractiveArenaState | None, mutable_state.get(interactive_key))
    if interactive_state is None:
        mutable_state[state_key] = VisualGameState.CONFIGURING.value
        return False
    if not isinstance(interactive_state.player, IGraphicalPlayer):
        raise TypeError("interactive state requires a graphical player")

    view_state = _build_interactive_view_state(interactive_state)
    page.visual_position(position_container, view_state)
    page.visual_movements(movement_container, view_state, VisualGameState.PLAYING)
    page.visual_scoreboard(scoreboard_container, view_state)

    movement: IMovement | None = None
    try:
        movement = interactive_state.player.play_from_ui(
            interactive_state.position,
            ui_context={
                "container": movement_container,
                "possible_movements": view_state.possible_movements,
                "key_prefix": f"{page.key}.playing.{view_state.frame_index}",
                "view_state": view_state,
            },
        )
    except RuntimeError as error:
        if "not selected yet" not in str(error):
            raise

    if movement is None:
        return True
    if not interactive_state.rules.is_movement_possible(movement, interactive_state.position):
        raise ValueError(f"illegal movement {movement!r} returned by graphical player")

    _apply_movement(interactive_state=interactive_state, movement=movement)
    mutable_state[interactive_key] = interactive_state

    finished, reason = _interactive_finished(interactive_state)
    if finished:
        replay = interactive_state.as_replay(end_reason=reason)
        mutable_state[replay_key] = replay
        mutable_state[controller_key] = PlaybackController(total_frames=len(replay.frames))
        mutable_state.pop(interactive_key, None)
        mutable_state[state_key] = VisualGameState.REVIEWING.value

    if hasattr(streamlit_api, "rerun"):
        streamlit_api.rerun()
    return True


def render_reviewing_mode(
    streamlit_api: Any,
    page: OptimizationGamePage,
    mutable_state: MutableMapping[str, object],
    replay_key: str,
    controller_key: str,
    state_key: str,
    position_container: Any,
    movement_container: Any,
    scoreboard_container: Any,
    frame_delay_seconds: float,
) -> bool:
    """Render replay controls and position/movement panels in reviewing mode.

    Args:
        streamlit_api: Streamlit module-like API.
        page: Selected game page.
        mutable_state: Session-state mapping.
        replay_key: Replay-state key.
        controller_key: Controller-state key.
        state_key: UI-state key.
        position_container: Position panel container.
        movement_container: Movement panel container.
        scoreboard_container: Scoreboard panel container.
        frame_delay_seconds: Delay used for autoplay.

    Returns:
        ``True`` when reviewing mode is active; otherwise ``False``.
    """
    if _ui_state_from_session(mutable_state, state_key) is not VisualGameState.REVIEWING:
        return False
    replay = cast(OptimizationReplay | None, mutable_state.get(replay_key))
    controller = cast(PlaybackController | None, mutable_state.get(controller_key))
    if replay is None or controller is None:
        mutable_state[state_key] = VisualGameState.CONFIGURING.value
        return False

    requested_frame = cast(
        int,
        position_container.slider(
            "Turn",
            min_value=0,
            max_value=replay.total_turns(),
            value=controller.current_index(),
        ),
    )
    if requested_frame != controller.current_index():
        controller.seek(requested_frame)
    position_container.progress(controller.progress_ratio())

    frame = replay.frame_at(controller.current_index())
    view_state = OptimizationViewState(
        replay=replay,
        frame_index=controller.current_index(),
        frame=frame,
        possible_movements=tuple(replay.rules.possible_movements(frame.position)),
    )
    page.visual_position(position_container, view_state)
    page.visual_movements(movement_container, view_state, VisualGameState.REVIEWING)
    page.visual_scoreboard(scoreboard_container, view_state)

    if controller.is_playing():
        controller.step_forward()
        if hasattr(streamlit_api, "rerun"):
            time.sleep(frame_delay_seconds)
            streamlit_api.rerun()
    return True


def ui_state(mutable_state: MutableMapping[str, object], state_key: str) -> VisualGameState:
    """Return current visual UI state from session mapping.

    Args:
        mutable_state: Session-state mapping.
        state_key: Session key for UI state.

    Returns:
        Current visual state.
    """
    return _ui_state_from_session(mutable_state, state_key)
