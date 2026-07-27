"""Abstract base class for game governance."""

from abc import ABC, abstractmethod

from iarena.game.GameConfig import GameConfig
from iarena.game.GameRules import GameRules


class GameGovernance(ABC):
    """Registry and factory for a concrete game's rule variants and configurations.

    Acts as the top-level entry point for a specific game implementation.
    Knows which configuration types the game supports and how to construct
    a matching GameRules object from a given configuration.

    Notes
    -----
    # TODO: add supported_player_types and supported_interface_types
    # once the player and interface modules are designed.
    """

    @abstractmethod
    def create_rules(self, config: GameConfig) -> GameRules:
        """Construct and return a GameRules instance for config.

        Parameters
        ----------
        config:
            A game configuration object whose type must be one of the
            values returned by supported_configs.

        Returns
        -------
        GameRules
            The rules object initialised from config.

        Raises
        ------
        TypeError
            If config is not an instance of a supported configuration type.
        """

    @abstractmethod
    def supported_configs(self) -> list[type[GameConfig]]:
        """Return the list of GameConfig subclasses this governance accepts.

        Returns
        -------
        list[type[GameConfig]]
            Supported configuration classes. create_rules must accept any
            instance whose type appears in this list.
        """
