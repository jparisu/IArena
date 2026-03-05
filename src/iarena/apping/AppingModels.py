"""Data models used by Streamlit-based single-player optimization apps."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from typing import Any

from iarena.interfacing.IGameRules import IGameRules
from iarena.interfacing.IMovement import IMovement
from iarena.interfacing.IPlayer import IPlayer
from iarena.interfacing.IPosition import IPosition
from iarena.interfacing.ScoreBoard import ScoreBoard
from iarena.interfacing.VisualGame import VisualGame, VisualGameState
from iarena.playing.RandomPlayer import RandomPlayer
from iarena.playing.VisualPlayer import VisualPlayer

PlayerFactory = Callable[[], IPlayer]
ConfigurationValues = Mapping[str, object]
RenderConfigurationFunction = Callable[[Any], ConfigurationValues]
BuildRulesFunction = Callable[[ConfigurationValues], IGameRules]
RenderViewFunction = Callable[[Any, "OptimizationViewState"], None]
RenderDescriptionFunction = Callable[[Any, ConfigurationValues], None]
RenderMovementsFunction = Callable[[Any, "OptimizationViewState", VisualGameState], None]
RenderScoreboardFunction = Callable[[Any, "OptimizationViewState"], None]


@dataclass(frozen=True, slots=True)
class OptimizationReplayFrame:
    """Store one frame in a replayable optimization run."""

    turn_index: int
    position: IPosition
    score: ScoreBoard
    movement_to_next: IMovement | None


@dataclass(frozen=True, slots=True)
class OptimizationReplay:
    """Store full replay information for one completed game."""

    rules: IGameRules
    frames: tuple[OptimizationReplayFrame, ...]
    final_score: ScoreBoard
    end_reason: str | None

    def total_turns(self) -> int:
        """Return number of completed turns represented by this replay.

        Args:
            None.

        Returns:
            Number of turns.
        """
        if not self.frames:
            return 0
        return len(self.frames) - 1

    def frame_at(self, frame_index: int) -> OptimizationReplayFrame:
        """Return one replay frame by index.

        Args:
            frame_index: Requested frame index.

        Returns:
            Replay frame at the requested index.
        """
        if frame_index < 0 or frame_index >= len(self.frames):
            raise IndexError(f"frame index {frame_index} out of range [0, {len(self.frames) - 1}]")
        return self.frames[frame_index]


@dataclass(frozen=True, slots=True)
class OptimizationViewState:
    """Container passed to game-specific render callbacks."""

    replay: OptimizationReplay
    frame_index: int
    frame: OptimizationReplayFrame
    possible_movements: tuple[IMovement, ...]


@dataclass(frozen=True, slots=True)
class OptimizationGamePage(VisualGame):
    """Describe how one game is configured, executed, and rendered in Streamlit."""

    key: str
    title: str
    render_configuration: RenderConfigurationFunction
    build_rules: BuildRulesFunction
    render_position: RenderViewFunction
    default_player_factory: PlayerFactory
    extra_player_factories: Mapping[str, PlayerFactory] = field(default_factory=dict)
    render_description: RenderDescriptionFunction | None = None
    render_movements: RenderMovementsFunction | None = None
    render_scoreboard: RenderScoreboardFunction | None = None
    render_secret_information: RenderViewFunction | None = None
    turn_limit: int | None = 5_000
    autoplay_delay_seconds: float = 0.2

    def available_player_factories(self) -> dict[str, PlayerFactory]:
        """Return all selectable player factories for this page.

        Args:
            None.

        Returns:
            Dictionary keyed by display name.
        """
        factories: dict[str, PlayerFactory] = {
            "Game default": self.default_player_factory,
            "Random": lambda: RandomPlayer(),
            "Visual (generic)": lambda: VisualPlayer(),
        }
        factories.update(dict(self.extra_player_factories))
        return factories

    def visual_configuration(self, container: Any) -> ConfigurationValues:
        """Render game-specific configuration controls.

        Args:
            container: Streamlit-like container where controls are rendered.

        Returns:
            Mapping with validated configuration values.
        """
        return self.render_configuration(container)

    def visual_description(self, container: Any, configuration: ConfigurationValues) -> None:
        """Render game description during configuration mode.

        Args:
            container: Streamlit-like container where description is rendered.
            configuration: Current game configuration.

        Returns:
            None.
        """
        if self.render_description is None:
            container.write("Configure the game and press Start to begin.")
            return
        self.render_description(container, configuration)

    def visual_position(self, container: Any, view_state: OptimizationViewState) -> None:
        """Render game position for playing/reviewing modes.

        Args:
            container: Streamlit-like container where position is rendered.
            view_state: Current view state.

        Returns:
            None.
        """
        self.render_position(container, view_state)

    def visual_movements(
        self,
        container: Any,
        view_state: OptimizationViewState,
        state: VisualGameState,
    ) -> None:
        """Render movement panel details for the active UI state.

        Args:
            container: Streamlit-like container where movement info is rendered.
            view_state: Current view state.
            state: Current UI state.

        Returns:
            None.
        """
        if self.render_movements is not None:
            self.render_movements(container, view_state, state)
            return

        if state is VisualGameState.REVIEWING:
            if view_state.frame.movement_to_next is None:
                container.write("Movement taken: <none>")
            else:
                container.write(f"Movement taken: {view_state.frame.movement_to_next}")
            return

        if view_state.possible_movements:
            container.write("Available movements:")
            for movement in view_state.possible_movements:
                container.write(f"- {movement}")
        else:
            container.write("Available movements: <none>")

    def visual_scoreboard(self, container: Any, view_state: OptimizationViewState) -> None:
        """Render score information for the current frame.

        Args:
            container: Streamlit-like container where score is rendered.
            view_state: Current view state.

        Returns:
            None.
        """
        if self.render_scoreboard is not None:
            self.render_scoreboard(container, view_state)
            return
        container.write(f"Current score: {view_state.frame.score.get_score(0):.2f}")
