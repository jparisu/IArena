"""Interface to register and expose classes that compose a specific game."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from iarena.desining.gaming.GameConfiguration import GameConfiguration

if TYPE_CHECKING:
    from iarena.desining.gaming.GameGenerator import GameGenerator
    from iarena.desining.gaming.GameRules import GameRules, GameSolver
    from iarena.desining.gaming.Movement import Movement
    from iarena.desining.gaming.Position import Position
    from iarena.desining.playing.Player import Player
    from iarena.desining.visualing.StreamlitGame import StreamlitGame
    from iarena.desining.visualing.TerminalGame import TerminalGame
    from iarena.utilizing.protocoling import IPlotRenderable, ITextRenderable


class GameOrchestrator(ABC):
    """Describe which classes are used by one concrete game family."""

    @abstractmethod
    def game_rules_class(self) -> type[GameRules]:
        """Return the game rules class used by this game.

        Args:
            None.

        Returns:
            Game rules class.
        """
        raise NotImplementedError

    @abstractmethod
    def position_class(self) -> type[Position]:
        """Return the position class used by this game.

        Args:
            None.

        Returns:
            Position class.
        """
        raise NotImplementedError

    @abstractmethod
    def movement_class(self) -> type[Movement]:
        """Return the movement class used by this game.

        Args:
            None.

        Returns:
            Movement class.
        """
        raise NotImplementedError

    @abstractmethod
    def player_class(self) -> type[Player]:
        """Return the default player class used by this game.

        Args:
            None.

        Returns:
            Player class.
        """
        raise NotImplementedError

    def game_configuration_class(self) -> type[object] | None:
        """Return game configuration class when available.

        Args:
            None.

        Returns:
            Configuration class or ``None``.
        """
        return None

    def game_generator_class(self) -> type[GameGenerator] | None:
        """Return generator class when available.

        Args:
            None.

        Returns:
            Generator class or ``None``.
        """
        return None

    def game_solver_class(self) -> type[GameSolver] | None:
        """Return game solver class when available.

        Args:
            None.

        Returns:
            Solver class or ``None``.
        """
        return None

    def terminal_game_class(self) -> type[TerminalGame] | None:
        """Return terminal-visualization interface class when available.

        Args:
            None.

        Returns:
            Terminal visualization class or ``None``.
        """
        return None

    def streamlit_game_class(self) -> type[StreamlitGame] | None:
        """Return Streamlit-visualization interface class when available.

        Args:
            None.

        Returns:
            Streamlit visualization class or ``None``.
        """
        return None

    def text_renderable_class(self) -> type[ITextRenderable] | None:
        """Return text-renderable class when available.

        Args:
            None.

        Returns:
            Text-renderable class or ``None``.
        """
        return None

    def plot_renderable_class(self) -> type[IPlotRenderable] | None:
        """Return plot-renderable class when available.

        Args:
            None.

        Returns:
            Plot-renderable class or ``None``.
        """
        return None

    def has_game_configuration(self) -> bool:
        """Return whether this game exposes a configuration class.

        Args:
            None.

        Returns:
            ``True`` when a configuration class is exposed.
        """
        return self.game_configuration_class() is not None

    def has_game_generator(self) -> bool:
        """Return whether this game exposes a generator.

        Args:
            None.

        Returns:
            ``True`` when a generator class is exposed.
        """
        return self.game_generator_class() is not None

    def has_game_solver(self) -> bool:
        """Return whether this game exposes a solver.

        Args:
            None.

        Returns:
            ``True`` when a solver class is exposed.
        """
        return self.game_solver_class() is not None

    def has_terminal_interface(self) -> bool:
        """Return whether this game can be visualized in terminal.

        Args:
            None.

        Returns:
            ``True`` when terminal interface class is exposed.
        """
        return self.terminal_game_class() is not None

    def has_streamlit_interface(self) -> bool:
        """Return whether this game can be visualized in Streamlit.

        Args:
            None.

        Returns:
            ``True`` when Streamlit interface class is exposed.
        """
        return self.streamlit_game_class() is not None

    def has_text_rendering(self) -> bool:
        """Return whether this game exposes text-renderable state/actions.

        Args:
            None.

        Returns:
            ``True`` when a text-renderable class is exposed.
        """
        return self.text_renderable_class() is not None

    def has_plotting(self) -> bool:
        """Return whether this game exposes plot-renderable state/actions.

        Args:
            None.

        Returns:
            ``True`` when a plot-renderable class is exposed.
        """
        return self.plot_renderable_class() is not None
