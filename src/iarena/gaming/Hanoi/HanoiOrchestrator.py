"""Game orchestrator for the Hanoi family."""

from __future__ import annotations

from iarena.desining.gaming.GameGenerator import GameGenerator
from iarena.desining.gaming.GameOrchestrator import GameOrchestrator
from iarena.desining.gaming.GameRules import GameRules
from iarena.desining.gaming.Movement import Movement
from iarena.desining.gaming.Position import Position
from iarena.desining.playing.Player import Player
from iarena.desining.visualing import StreamlitGame, TerminalGame
from iarena.gaming.Hanoi.HanoiGameConfiguration import HanoiGameConfiguration
from iarena.gaming.Hanoi.HanoiGameGenerator import HanoiGameGenerator
from iarena.gaming.Hanoi.HanoiGameRules import HanoiGameRules
from iarena.gaming.Hanoi.HanoiMovement import HanoiMovement
from iarena.gaming.Hanoi.HanoiPlayer import HanoiPlayer
from iarena.gaming.Hanoi.HanoiPosition import HanoiPosition
from iarena.utilizing.protocoling import IPlotRenderable, ITextRenderable


class HanoiOrchestrator(GameOrchestrator):
    """Expose all Hanoi components through the orchestrator interface."""

    def game_rules_class(self) -> type[GameRules]:
        """Return the game-rules class used by Hanoi.

        Args:
            None.

        Returns:
            Hanoi rules class.
        """
        return HanoiGameRules

    def position_class(self) -> type[Position]:
        """Return the position class used by Hanoi.

        Args:
            None.

        Returns:
            Hanoi position class.
        """
        return HanoiPosition

    def movement_class(self) -> type[Movement]:
        """Return the movement class used by Hanoi.

        Args:
            None.

        Returns:
            Hanoi movement class.
        """
        return HanoiMovement

    def player_class(self) -> type[Player]:
        """Return the default player class used by Hanoi.

        Args:
            None.

        Returns:
            Hanoi default player class.
        """
        return HanoiPlayer

    def game_generator_class(self) -> type[GameGenerator] | None:
        """Return the dictionary-based game-generator class.

        Args:
            None.

        Returns:
            Hanoi game generator class.
        """
        return HanoiGameGenerator

    def game_configuration_class(self) -> type[object] | None:
        """Return the Hanoi configuration class.

        Args:
            None.

        Returns:
            Hanoi typed configuration class.
        """
        return HanoiGameConfiguration

    def terminal_game_class(self) -> type[TerminalGame] | None:
        """Return terminal visualization class if available.

        Args:
            None.

        Returns:
            ``None`` because visual layer is not implemented yet.
        """
        return None

    def streamlit_game_class(self) -> type[StreamlitGame] | None:
        """Return Streamlit visualization class if available.

        Args:
            None.

        Returns:
            ``None`` because visual layer is not implemented yet.
        """
        return None

    def text_renderable_class(self) -> type[ITextRenderable] | None:
        """Return the text-renderable class used by Hanoi.

        Args:
            None.

        Returns:
            Hanoi position class.
        """
        return HanoiPosition

    def plot_renderable_class(self) -> type[IPlotRenderable] | None:
        """Return plot-renderable class if available.

        Args:
            None.

        Returns:
            ``None`` because plotting layer is not implemented yet.
        """
        return None
