"""Core abstractions and registries for game definitions in IArena."""

from iarena.gaming import goldmine, hanoi, tictactoe
from iarena.gaming.BestPlayerOracle import BestPlayerOracle
from iarena.gaming.Configuration import Configuration
from iarena.gaming.ConfigurationSuite import ConfigurationSuite
from iarena.gaming.Game import Game
from iarena.gaming.GameGovernor import GameGovernor
from iarena.gaming.Movement import Movement
from iarena.gaming.Oracle import Oracle
from iarena.gaming.Position import Position
from iarena.gaming.Rules import Rules

__all__ = [
    "Movement",
    "Position",
    "Configuration",
    "ConfigurationSuite",
    "Rules",
    "Oracle",
    "BestPlayerOracle",
    "Game",
    "GameGovernor",
    "goldmine",
    "hanoi",
    "tictactoe",
]
