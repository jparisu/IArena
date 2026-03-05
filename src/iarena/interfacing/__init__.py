"""Public interfaces used to define turn-based games in IArena.

The `interfacing` package contains protocol-like abstract classes that users extend
to model:
- game positions (`IPosition`),
- valid actions (`IMovement`),
- game rules (`IGameRules`),
- players (`IPlayer`),
- and score aggregation (`ScoreBoard`).

These interfaces are intentionally lightweight to keep custom game
implementations explicit and easy to test.
"""

from iarena.interfacing.IArena import IArena
from iarena.interfacing.IGameOrchestrator import IGameOrchestrator
from iarena.interfacing.IGameRules import IGameGenerator, IGameRules, IGameSolver
from iarena.interfacing.IMovement import IMovement
from iarena.interfacing.IPlayer import IGraphicalPlayer, IPlayer, ITerminalPlayer, PlayerIndex
from iarena.interfacing.IPosition import IPosition
from iarena.interfacing.VisualGame import VisualGame, VisualGameState
from iarena.interfacing.ScoreBoard import Score, ScoreBoard
from iarena.utilizing.protocoling import (
    IPlotRenderable,
    ITextRenderable,
    as_text,
    supports_plotting,
    supports_text_rendering,
)

__all__ = [
    "IArena",
    "IGameGenerator",
    "IGameOrchestrator",
    "IGameRules",
    "IGameSolver",
    "IGraphicalPlayer",
    "IMovement",
    "IPlayer",
    "IPlotRenderable",
    "IPosition",
    "ITerminalPlayer",
    "VisualGame",
    "VisualGameState",
    "ITextRenderable",
    "PlayerIndex",
    "Score",
    "ScoreBoard",
    "as_text",
    "supports_plotting",
    "supports_text_rendering",
]
