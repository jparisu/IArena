"""Factory helpers to compose arenas from reusable behavior blocks."""

from __future__ import annotations

from collections.abc import Sequence

from iarena.arening.ArenaBehaviors import (
    GameHistoryObserver,
    GameTimeLimitCondition,
    IArenaObserver,
    IArenaStopCondition,
    PerTurnTimeLimitCondition,
    ScoreLimitCondition,
    TurnLimitCondition,
)
from iarena.arening.GenericArena import GenericArena
from iarena.arening.TerminalArena import OutputFunction, TerminalArena
from iarena.interfacing.IGameRules import IGameRules
from iarena.interfacing.IPlayer import IPlayer
from iarena.interfacing.IPosition import IPosition


class ArenaFactory:
    """Build arenas by combining limits, observers, and rendering style."""

    @staticmethod
    def build(
        rules: IGameRules,
        players: Sequence[IPlayer],
        position: IPosition | None = None,
        *,
        per_turn_time_limit_seconds: float | None = None,
        game_time_limit_seconds: float | None = None,
        turn_limit: int | None = None,
        score_limit: float | None = None,
        store_information: bool = False,
        terminal: bool = False,
        penalty_score: float = -float("inf"),
        raise_on_stop: bool = True,
        output_function: OutputFunction = print,
    ) -> GenericArena:
        """Build one arena configured with requested limits and observers.

        Args:
            rules: Rules object that defines game mechanics.
            players: Ordered players participating in the game.
            position: Optional initial position override.
            per_turn_time_limit_seconds: Optional per-turn timeout in seconds.
            game_time_limit_seconds: Optional whole-game timeout in seconds.
            turn_limit: Optional maximum number of turns.
            score_limit: Optional score threshold that stops the game.
            store_information: Whether to attach game-history recorder.
            terminal: Whether to return terminal-rendering arena.
            penalty_score: Penalty score used by timeout/turn-limit conditions.
            raise_on_stop: Whether stop conditions raise ``ArenaStoppedError``.
            output_function: Writer used by terminal arenas.

        Returns:
            Configured arena instance.
        """
        stop_conditions: list[IArenaStopCondition] = []
        observers: list[IArenaObserver] = []

        if per_turn_time_limit_seconds is not None:
            stop_conditions.append(
                PerTurnTimeLimitCondition(
                    max_seconds_per_turn=per_turn_time_limit_seconds,
                    penalty_score=penalty_score,
                )
            )

        if game_time_limit_seconds is not None:
            stop_conditions.append(
                GameTimeLimitCondition(
                    max_game_seconds=game_time_limit_seconds,
                    penalty_score=penalty_score,
                )
            )

        if turn_limit is not None:
            stop_conditions.append(
                TurnLimitCondition(
                    max_turns=turn_limit,
                    penalty_score=penalty_score,
                )
            )

        if score_limit is not None:
            stop_conditions.append(ScoreLimitCondition(min_score=score_limit))

        if store_information:
            observers.append(GameHistoryObserver())

        if terminal:
            return TerminalArena(
                rules=rules,
                players=players,
                position=position,
                stop_conditions=stop_conditions,
                observers=observers,
                raise_on_stop=raise_on_stop,
                output_function=output_function,
            )

        return GenericArena(
            rules=rules,
            players=players,
            position=position,
            stop_conditions=stop_conditions,
            observers=observers,
            raise_on_stop=raise_on_stop,
        )
