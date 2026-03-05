"""Abstract player interface used by the arena to request movements."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    from iarena.interfacing.IGameRules import IGameRules
    from iarena.interfacing.IMovement import IMovement
    from iarena.interfacing.IPosition import IPosition

# Type for the index of a player in the game.
PlayerIndex = int


class IPlayer(ABC):
    """Represents an agent able to choose movements in a game.

    Concrete implementations can be human-driven, heuristic, search-based, or
    ML-based, as long as they return a legal `IMovement` for a provided
    position.
    """

    def __init__(self, name: str | None = None) -> None:
        """Initialize player identity used in logs and reports.

        Args:
            name: Optional display name. If omitted, an auto-generated
                class-based identifier is used.
        """
        if name is None:
            name = f"{self.__class__.__name__}_{id(self)}"
        self._name = name

    def name(self) -> str:
        """Return the human-readable name of this player."""
        return self._name

    @abstractmethod
    def play(self, position: IPosition) -> IMovement:
        """Choose a movement for the current position.

        Args:
            position: Current game position.

        Returns:
            Selected movement to be applied by the arena.
        """
        ...

    def starting_game(self, rules: IGameRules, player_index: PlayerIndex) -> None:
        """Lifecycle hook called once before a game starts.

        Implementations may override this to reset internal state, cache rules,
        or configure strategies according to assigned turn order.

        Args:
            rules: Rules object that governs the upcoming game.
            player_index: Index assigned to this player in the match.
        """
        return None


@runtime_checkable
class ITerminalPlayer(Protocol):
    """Opt-in capability for players that interact via terminal I/O."""

    def play_from_terminal(self, position: IPosition) -> IMovement:
        """Select a movement by interacting through the terminal."""
        ...


@runtime_checkable
class IGraphicalPlayer(Protocol):
    """Opt-in capability for players that interact via a graphical UI."""

    def play_from_ui(self, position: IPosition, ui_context: Any | None = None) -> IMovement:
        """Select a movement by interacting through a UI backend."""
        ...
