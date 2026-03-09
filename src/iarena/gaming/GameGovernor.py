"""Declares the singleton registry facade used to discover playable games."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, ClassVar

from iarena.gaming.Game import Game
from iarena.gaming.goldmine.GoldMineGame import GoldMineGame
from iarena.gaming.hanoi.HanoiGame import HanoiGame
from iarena.gaming.tictactoe.TicTacToeGame import TicTacToeGame
from iarena.utilizing.structuring.GenericRegistry import GenericRegistry
from iarena.utilizing.structuring.GenericSingleton import GenericSingleton


class GameGovernor(GenericRegistry[Game]):
    """Singleton registry responsible for discovering available game entries.

    Purpose:
        Centralizes game registration and lookup through one shared runtime
        object.
    How it works:
        Extends `GenericRegistry` with singleton access and registers built-in
        games once during first initialization.
    Used for:
        Application game selection flows and registry-backed game resolution.
    Public Attributes:
        None declared at class level in this base definition.
    """

    _singleton: ClassVar[GenericSingleton[GameGovernor] | None] = None

    def __init__(self) -> None:
        """Initialize one game-governor registry and register built-in games.

        Returns:
            None.
        """
        super().__init__()
        self.register_game(GoldMineGame.instance())
        self.register_game(HanoiGame.instance())
        self.register_game(TicTacToeGame.instance())

    @classmethod
    def instance(cls) -> GameGovernor:
        """Return the unique singleton instance of the game governor.

        Returns:
            GameGovernor: Shared singleton registry instance.
        """
        if cls._singleton is None:
            cls._singleton = GenericSingleton(cls)
        return cls._singleton()

    def register_game(self, game: Game, aliases: list[str] | None = None, overwrite: bool = False) -> str:
        """Register one game object in the governor registry.

        Args:
            game: Game instance to register.
            aliases: Optional aliases that can be used to retrieve the game.
            overwrite: Whether to overwrite an existing alias mapping.

        Returns:
            str: Canonical normalized name used as registry key.
        """
        return self.register(obj=game, name=game.name(), aliases=aliases, overwrite=overwrite)

    def games(self, requirement: Callable[[Any], bool]) -> list[Game]:
        """Return games that satisfy one requirement predicate.

        Args:
            requirement: Predicate used to keep compatible game objects.

        Returns:
            list[Game]: List of registered game objects accepted by `requirement`.
        """
        return [game for game in self._values.values() if requirement(game)]

    def game_names(self, requirement: Callable[[Any], bool]) -> list[str]:
        """Return canonical names for games satisfying one requirement predicate.

        Args:
            requirement: Predicate used to keep compatible game objects.

        Returns:
            list[str]: Sorted canonical names of compatible registered games.
        """
        compatible_names = [name for name, game in self._values.items() if requirement(game)]
        compatible_names.sort()
        return compatible_names

    @classmethod
    def add_game(cls, game: Game, aliases: list[str] | None = None, overwrite: bool = False) -> str:
        """Register one game object in the singleton governor.

        Args:
            game: Game instance to register.
            aliases: Optional aliases that can be used to retrieve the game.
            overwrite: Whether to overwrite an existing alias mapping.

        Returns:
            str: Canonical normalized name used as registry key.
        """
        return cls.instance().register_game(game=game, aliases=aliases, overwrite=overwrite)

    @classmethod
    def get_games(cls, requirement: Callable[[Any], bool] | None = None) -> list[Game]:
        """Return all registered games that satisfy one optional requirement.

        Args:
            requirement: Optional predicate used to filter game objects.

        Returns:
            list[Game]: Compatible registered game objects.
        """
        predicate = requirement if requirement is not None else (lambda _game: True)
        return cls.instance().games(requirement=predicate)

    @classmethod
    def get_game_names(cls, requirement: Callable[[Any], bool] | None = None) -> list[str]:
        """Return canonical names of registered games matching one requirement.

        Args:
            requirement: Optional predicate used to filter game objects.

        Returns:
            list[str]: Sorted canonical names for matching games.
        """
        predicate = requirement if requirement is not None else (lambda _game: True)
        return cls.instance().game_names(requirement=predicate)

    @classmethod
    def find_game(
        cls,
        name: str,
        requirement: Callable[[Any], bool],
        throw: bool = True,
    ) -> Game | None:
        """Find and return a registered game by name or alias.

        Args:
            name: Game name or alias to resolve from the registry.
            requirement: Predicate that the found game must satisfy.
            throw: Whether to raise when game is missing or incompatible.

        Returns:
            Game | None: Matching game object, or `None` when not found and
            `throw` is `False`.
        """
        game = cls.instance().get(name, strict=False)
        if game is None:
            if throw:
                raise KeyError(f"Unknown game '{name}'.")
            return None

        if not requirement(game):
            if throw:
                raise ValueError(f"Game '{name}' does not satisfy the required predicate.")
            return None

        return game
