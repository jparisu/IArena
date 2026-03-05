"""Interface to register and expose classes that compose a specific game."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from iarena.interfacing.IGameRules import IGameGenerator, IGameRules, IGameSolver
    from iarena.interfacing.IMovement import IMovement
    from iarena.interfacing.IPlayer import IGraphicalPlayer, IPlayer, ITerminalPlayer
    from iarena.interfacing.IPosition import IPosition
    from iarena.utilizing.protocoling import IPlotRenderable, ITextRenderable


class IGameOrchestrator(ABC):
    """Describe which classes are used by one concrete game family.

    This interface returns class objects only (never instances), so external
    code can inspect available components and optional capabilities before
    creating objects.
    """

    @abstractmethod
    def game_rules_class(self) -> type[IGameRules]:
        """Return the game rules class used by this game."""
        ...

    @abstractmethod
    def position_class(self) -> type[IPosition]:
        """Return the position class used by this game."""
        ...

    @abstractmethod
    def movement_class(self) -> type[IMovement]:
        """Return the movement class used by this game."""
        ...

    @abstractmethod
    def player_class(self) -> type[IPlayer]:
        """Return the default player class used by this game."""
        ...

    def terminal_player_class(self) -> type[ITerminalPlayer] | None:
        """Return terminal-playable player class when available."""
        return None

    def graphical_player_class(self) -> type[IGraphicalPlayer] | None:
        """Return GUI-playable player class when available."""
        return None

    def game_generator_class(self) -> type[IGameGenerator] | None:
        """Return dictionary-based game-generator class when available."""
        return None

    def game_solver_class(self) -> type[IGameSolver] | None:
        """Return game-solver class when available."""
        return None

    def text_renderable_class(self) -> type[ITextRenderable] | None:
        """Return text-renderable class when available."""
        return None

    def plot_renderable_class(self) -> type[IPlotRenderable] | None:
        """Return plot-renderable class when available."""
        return None

    def has_terminal_player(self) -> bool:
        """Return whether this game exposes a terminal-playable player class."""
        return self.terminal_player_class() is not None

    def has_graphical_player(self) -> bool:
        """Return whether this game exposes a GUI-playable player class."""
        return self.graphical_player_class() is not None

    def has_game_generator(self) -> bool:
        """Return whether this game exposes a dictionary-based generator."""
        return self.game_generator_class() is not None

    def has_game_solver(self) -> bool:
        """Return whether this game exposes a solver."""
        return self.game_solver_class() is not None

    def has_text_rendering(self) -> bool:
        """Return whether this game exposes text-renderable state/actions."""
        return self.text_renderable_class() is not None

    def has_plotting(self) -> bool:
        """Return whether this game exposes plot-renderable state/actions."""
        return self.plot_renderable_class() is not None
