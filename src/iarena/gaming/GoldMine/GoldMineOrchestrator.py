"""Game orchestrator for the GoldMine family."""

from __future__ import annotations

from iarena.desining.gaming.GameGenerator import GameGenerator
from iarena.desining.gaming.GameOrchestrator import GameOrchestrator
from iarena.desining.gaming.GameRules import GameRules
from iarena.desining.gaming.Movement import Movement
from iarena.desining.gaming.Position import Position
from iarena.desining.playing.Player import Player
from iarena.desining.visualing import StreamlitGame, TerminalGame
from iarena.gaming.GoldMine.GoldMineGameConfiguration import GoldMineGameConfiguration
from iarena.gaming.GoldMine.GoldMineGameGenerator import GoldMineGameGenerator
from iarena.gaming.GoldMine.GoldMineGameRules import GoldMineGameRules
from iarena.gaming.GoldMine.GoldMineMovement import GoldMineMovement
from iarena.gaming.GoldMine.GoldMinePlayer import GoldMinePlayer
from iarena.gaming.GoldMine.GoldMinePosition import GoldMinePosition
from iarena.utilizing.protocoling import IPlotRenderable, ITextRenderable


class GoldMineOrchestrator(GameOrchestrator):
    """Expose all GoldMine components through the orchestrator interface."""

    def game_rules_class(self) -> type[GameRules]:
        """Return the game-rules class used by GoldMine.

        Args:
            None.

        Returns:
            GoldMine rules class.
        """
        return GoldMineGameRules

    def position_class(self) -> type[Position]:
        """Return the position class used by GoldMine.

        Args:
            None.

        Returns:
            GoldMine position class.
        """
        return GoldMinePosition

    def movement_class(self) -> type[Movement]:
        """Return the movement class used by GoldMine.

        Args:
            None.

        Returns:
            GoldMine movement class.
        """
        return GoldMineMovement

    def player_class(self) -> type[Player]:
        """Return the default player class used by GoldMine.

        Args:
            None.

        Returns:
            GoldMine default player class.
        """
        return GoldMinePlayer

    def game_generator_class(self) -> type[GameGenerator] | None:
        """Return the dictionary-based game-generator class.

        Args:
            None.

        Returns:
            GoldMine game generator class.
        """
        return GoldMineGameGenerator

    def game_configuration_class(self) -> type[object] | None:
        """Return the GoldMine configuration class.

        Args:
            None.

        Returns:
            GoldMine typed configuration class.
        """
        return GoldMineGameConfiguration

    def terminal_game_class(self) -> type[TerminalGame] | None:
        """Return the terminal-visualization class used by GoldMine.

        Args:
            None.

        Returns:
            GoldMine game-rules class.
        """
        return GoldMineGameRules

    def streamlit_game_class(self) -> type[StreamlitGame] | None:
        """Return the Streamlit-visualization class used by GoldMine.

        Args:
            None.

        Returns:
            GoldMine game-rules class.
        """
        return GoldMineGameRules

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
