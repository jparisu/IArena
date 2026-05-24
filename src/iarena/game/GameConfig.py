"""Abstract base class for game configuration."""

from abc import ABC


class GameConfig(ABC):  # noqa: B024
    """Static configuration for a concrete game.

    Each concrete game defines its own subclass of ``GameConfig`` to
    store the parameters required to initialise a specific game instance.

    Examples of information a subclass may contain:
    - Number of players.
    - Board dimensions.
    - Initial resources.
    - Game-mode variants.
    - Whether hidden information exists.
    - Maximum number of turns.
    """

    def __init_subclass__(cls, **kwargs: object) -> None:
        """Register subclasses normally; called automatically by Python."""
        super().__init_subclass__(**kwargs)

    def __new__(cls, *args: object, **kwargs: object) -> "GameConfig":
        """Prevent direct instantiation of the abstract base class."""
        if cls is GameConfig:
            raise TypeError("GameConfig is an abstract class and cannot be instantiated directly.")
        return super().__new__(cls)
