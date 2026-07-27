"""Top-level package for IArena."""

from iarena._version import __version__
from iarena.engine import Engine
from iarena.game import (
    FullGameRules,
    GameConfig,
    GameGovernance,
    GameMove,
    GameRules,
    GameState,
    ParseableGameMove,
    ParseableStringifiableGameMove,
    StringifiableGameMove,
)
from iarena.interface import Interface, NullInterface
from iarena.player import AutomaticPlayer, HumanPlayer, Player
from iarena.view import View

__all__ = [
    "__version__",
    "AutomaticPlayer",
    "Engine",
    "FullGameRules",
    "GameConfig",
    "GameGovernance",
    "GameMove",
    "GameRules",
    "GameState",
    "HumanPlayer",
    "Interface",
    "NullInterface",
    "ParseableGameMove",
    "ParseableStringifiableGameMove",
    "Player",
    "StringifiableGameMove",
    "View",
]
