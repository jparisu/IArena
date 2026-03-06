"""Public abstract contracts used to define IArena components."""

from iarena.desining.arening.Arena import Arena
from iarena.desining.gaming.GameConfiguration import GameConfiguration
from iarena.desining.gaming.GameGenerator import GameGenerator
from iarena.desining.gaming.GameOrchestrator import GameOrchestrator
from iarena.desining.gaming.GameRules import GameRules, GameSolver
from iarena.desining.gaming.Movement import Movement
from iarena.desining.playing.Player import Player, PlayerIndex
from iarena.desining.gaming.Position import Position
from iarena.desining.gaming.ScoreBoard import Score, ScoreBoard
from iarena.desining.visualing import StreamlitGame, TerminalGame
from iarena.utilizing.protocoling import (
    IPlotRenderable,
    ITextRenderable,
    as_text,
    supports_plotting,
    supports_text_rendering,
)

__all__ = [
    "Arena",
    "GameConfiguration",
    "GameGenerator",
    "GameOrchestrator",
    "GameRules",
    "GameSolver",
    "Movement",
    "Player",
    "PlayerIndex",
    "Position",
    "Score",
    "ScoreBoard",
    "StreamlitGame",
    "TerminalGame",
    "IPlotRenderable",
    "ITextRenderable",
    "as_text",
    "supports_plotting",
    "supports_text_rendering",
]
