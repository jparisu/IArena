"""Game module — abstract foundations for any turn-based game."""

from iarena.game.GameConfig import GameConfig
from iarena.game.GameGovernance import GameGovernance
from iarena.game.GameMove import (
    GameMove,
    ParseableGameMove,
    ParseableStringifiableGameMove,
    StringifiableGameMove,
)
from iarena.game.GameRules import FullGameRules, GameRules
from iarena.game.GameState import GameState

__all__ = [
    "GameConfig",
    "GameGovernance",
    "GameMove",
    "ParseableGameMove",
    "ParseableStringifiableGameMove",
    "StringifiableGameMove",
    "FullGameRules",
    "GameRules",
    "GameState",
]
