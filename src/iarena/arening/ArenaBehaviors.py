"""Backwards-compatible exports for arena behavior types and implementations."""

from iarena.arening.ArenaCommon import (
    PENALTY_SCORE,
    ArenaContext,
    ArenaStopCondition,
    ArenaStopDecision,
    ArenaTurnRecord,
    IArenaObserver,
    IArenaStopCondition,
    clone_score_board,
    penalty_for_all_players,
)
from iarena.arening.ArenaHistory import ArenaGameRecord, GameHistoryObserver
from iarena.arening.ArenaLimits import (
    GameTimeLimitCondition,
    PerTurnTimeLimitCondition,
    ScoreLimitCondition,
    TurnLimitCondition,
)

__all__ = [
    "PENALTY_SCORE",
    "ArenaContext",
    "ArenaGameRecord",
    "ArenaStopCondition",
    "ArenaStopDecision",
    "ArenaTurnRecord",
    "GameHistoryObserver",
    "GameTimeLimitCondition",
    "IArenaObserver",
    "IArenaStopCondition",
    "PerTurnTimeLimitCondition",
    "ScoreLimitCondition",
    "TurnLimitCondition",
    "clone_score_board",
    "penalty_for_all_players",
]
