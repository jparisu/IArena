"""Defines a player base class that can be loaded dynamically from Python files."""

from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING

from iarena.utilizing.filing.Loader import Loader

from .Player import Player

if TYPE_CHECKING:
    from iarena.gaming.Movement import Movement
    from iarena.gaming.Position import Position
    from iarena.gaming.Rules import Rules
    from iarena.playing.PlayerIndex import PlayerIndex


class LoadPlayer(Player):
    """Abstract player with file-loading support for custom external strategies.

    Purpose:
        Provides the `LoadPlayer` type within the IArena architecture.
    How it works:
        Adds default metadata/setup hooks and a classmethod that loads one player from a Python file.
    Used for:
        Running user-defined players that are distributed as standalone Python scripts.
    Public Attributes:
        None declared at class level in this base definition.
    """

    @abstractmethod
    def play(self, pos: Position) -> Movement:
        """Choose and return the next movement for the given position.

        What it does:
            Declares the core decision method that produces one legal movement.
        How it works:
            Concrete subclasses evaluate the input position and select a movement.
        Args:
            pos (Position): Current game position where the player must act.
        Returns:
            Movement: Movement chosen by the player strategy.
        """
        raise NotImplementedError

    @abstractmethod
    def authors(self) -> list[str]:
        """Return the list of authors for this player implementation.

        What it does:
            Declares metadata used to identify who created the player.
        How it works:
            Concrete subclasses return one or more stable author names.
        Args:
            None.
        Returns:
            list[str]: Ordered list of author names.
        """
        raise NotImplementedError

    def starting_game(self, rules: Rules, player_index: PlayerIndex) -> None:
        """Initialize player state when a new game begins.

        What it does:
            Provides a default setup hook that intentionally performs no work.
        How it works:
            Accepts the game context and returns immediately.
        Args:
            rules (Rules): Rules instance associated with the game to be played.
            player_index (PlayerIndex): Player identifier assigned in the arena.
        Returns:
            None: This default implementation has no side effects.
        """
        _ = (rules, player_index)

    def name(self) -> str:
        """Return the default stable name for dynamically loaded players.

        What it does:
            Provides a canonical fallback identifier.
        How it works:
            Returns a constant string unless subclasses override it.
        Args:
            None.
        Returns:
            str: Default name used for loaded players.
        """
        return "load-player"

    @classmethod
    def from_file(cls, path: str) -> LoadPlayer:
        """Load one `LoadPlayer` instance from a Python file.

        What it does:
            Executes one Python module file and returns its `PLAYER` instance.
        How it works:
            Imports the module from disk, validates the `PLAYER` variable, and checks the resulting type.
        Args:
            path (str): Path to the Python file containing a `PLAYER` variable.
        Returns:
            LoadPlayer: Loaded player instance exposed by the module.
        Raises:
            FileNotFoundError: If `path` does not exist.
            IsADirectoryError: If `path` points to a directory.
            ImportError: If the module cannot be loaded or executed.
            ValueError: If the module does not define `PLAYER`.
            TypeError: If `PLAYER` is not an instance of `LoadPlayer`.
        """
        loaded_variables = Loader.load_file(filename=path, variable_names=["PLAYER"])
        loaded_player = loaded_variables["PLAYER"]
        if not isinstance(loaded_player, LoadPlayer):
            raise TypeError(
                f"PLAYER must be an instance of LoadPlayer, got {type(loaded_player).__name__} from {path}",
            )
        return loaded_player
