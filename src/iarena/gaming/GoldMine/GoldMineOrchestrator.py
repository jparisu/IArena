"""Game orchestrator for the GoldMine family."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from iarena.apping.AppingModels import OptimizationViewState
from iarena.gaming.GoldMine.GoldMineApping import build_goldmine_streamlit_page
from iarena.gaming.GoldMine.GoldMineGameGenerator import GoldMineGameGenerator
from iarena.gaming.GoldMine.GoldMineGameRules import GoldMineGameRules
from iarena.gaming.GoldMine.GoldMineMovement import GoldMineMovement
from iarena.gaming.GoldMine.GoldMinePlayablePlayer import GoldMinePlayablePlayer
from iarena.gaming.GoldMine.GoldMinePlayer import GoldMinePlayer
from iarena.gaming.GoldMine.GoldMinePosition import GoldMinePosition
from iarena.interfacing.IGameOrchestrator import IGameOrchestrator
from iarena.interfacing.IGameRules import IGameGenerator, IGameRules
from iarena.interfacing.IMovement import IMovement
from iarena.interfacing.IPlayer import IGraphicalPlayer, IPlayer
from iarena.interfacing.IPosition import IPosition
from iarena.interfacing.VisualGame import VisualGameState
from iarena.utilizing.protocoling import IPlotRenderable, ITextRenderable


class GoldMineOrchestrator(IGameOrchestrator):
    """Expose all GoldMine components through the orchestrator interface."""

    def _visual_page(self) -> Any:
        """Build a GoldMine visual page helper.

        Args:
            None.

        Returns:
            GoldMine optimization page object.
        """
        return build_goldmine_streamlit_page()

    def game_rules_class(self) -> type[IGameRules]:
        """Return the game-rules class used by GoldMine.

        Args:
            None.

        Returns:
            GoldMine rules class.
        """
        return GoldMineGameRules

    def position_class(self) -> type[IPosition]:
        """Return the position class used by GoldMine.

        Args:
            None.

        Returns:
            GoldMine position class.
        """
        return GoldMinePosition

    def movement_class(self) -> type[IMovement]:
        """Return the movement class used by GoldMine.

        Args:
            None.

        Returns:
            GoldMine movement class.
        """
        return GoldMineMovement

    def player_class(self) -> type[IPlayer]:
        """Return the default player class used by GoldMine.

        Args:
            None.

        Returns:
            GoldMine default player class.
        """
        return GoldMinePlayer

    def game_generator_class(self) -> type[IGameGenerator] | None:
        """Return the dictionary-based game-generator class.

        Args:
            None.

        Returns:
            GoldMine game generator class.
        """
        return GoldMineGameGenerator

    def graphical_player_class(self) -> type[IGraphicalPlayer] | None:
        """Return graphical-playable player class for GoldMine.

        Args:
            None.

        Returns:
            GoldMine Streamlit-playable player class.
        """
        return GoldMinePlayablePlayer

    def text_renderable_class(self) -> type[ITextRenderable] | None:
        """Return the text-renderable class used by GoldMine.

        Args:
            None.

        Returns:
            GoldMine position class.
        """
        return GoldMinePosition

    def plot_renderable_class(self) -> type[IPlotRenderable] | None:
        """Return the plot-renderable class used by GoldMine.

        Args:
            None.

        Returns:
            GoldMine position class.
        """
        return GoldMinePosition

    def visual_configuration(self, container: Any) -> Mapping[str, object]:
        """Render visual configuration controls for GoldMine.

        Args:
            container: Streamlit-like container for controls.

        Returns:
            Mapping with selected GoldMine configuration values.
        """
        return self._visual_page().visual_configuration(container)

    def visual_description(self, container: Any, configuration: Mapping[str, object]) -> None:
        """Render GoldMine description in configuration mode.

        Args:
            container: Streamlit-like container where description is rendered.
            configuration: Current game configuration values.

        Returns:
            None.
        """
        self._visual_page().visual_description(container, configuration)

    def visual_position(self, container: Any, view_state: OptimizationViewState) -> None:
        """Render GoldMine position in playing/reviewing modes.

        Args:
            container: Streamlit-like container where position is rendered.
            view_state: Current replay frame and metadata.

        Returns:
            None.
        """
        self._visual_page().visual_position(container, view_state)

    def visual_movements(
        self,
        container: Any,
        view_state: OptimizationViewState,
        state: VisualGameState,
    ) -> None:
        """Render GoldMine movement panel content.

        Args:
            container: Streamlit-like container where movement info is rendered.
            view_state: Current replay frame and metadata.
            state: Active visual UI state.

        Returns:
            None.
        """
        self._visual_page().visual_movements(container, view_state, state)

    def visual_scoreboard(self, container: Any, view_state: OptimizationViewState) -> None:
        """Render GoldMine scoreboard panel content.

        Args:
            container: Streamlit-like container where score info is rendered.
            view_state: Current replay frame and metadata.

        Returns:
            None.
        """
        self._visual_page().visual_scoreboard(container, view_state)
