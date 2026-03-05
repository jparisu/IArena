"""Game orchestrator for the GoldMine family."""

from __future__ import annotations

from iarena.gaming.GoldMine.GoldMineGameGenerator import GoldMineGameGenerator
from iarena.gaming.GoldMine.GoldMineGameRules import GoldMineGameRules
from iarena.gaming.GoldMine.GoldMineMovement import GoldMineMovement
from iarena.gaming.GoldMine.GoldMinePlayer import GoldMinePlayer
from iarena.gaming.GoldMine.GoldMinePosition import GoldMinePosition
from iarena.interfacing.IGameOrchestrator import IGameOrchestrator
from iarena.interfacing.IGameRules import IGameGenerator, IGameRules
from iarena.interfacing.IMovement import IMovement
from iarena.interfacing.IPlayer import IPlayer
from iarena.interfacing.IPosition import IPosition
from iarena.utilizing.protocoling import IPlotRenderable, ITextRenderable


class GoldMineOrchestrator(IGameOrchestrator):
    """Expose all GoldMine components through the orchestrator interface."""

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
