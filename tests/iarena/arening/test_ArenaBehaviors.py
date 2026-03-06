"""Tests for composable arena behavior classes."""

from __future__ import annotations

import pytest

from iarena.arening.ArenaBehaviors import (
    ArenaTurnRecord,
    GameHistoryObserver,
    GameTimeLimitCondition,
    PerTurnTimeLimitCondition,
    ScoreLimitCondition,
)
from iarena.arening.ArenaExceptions import ArenaStoppedError
from iarena.arening.GenericArena import GenericArena
from ._dummy_game import DummyMovement, DummyRules, FailingPlayer, FixedMovementPlayer


def test_per_turn_time_limit_raises_with_penalized_score() -> None:
    """Per-turn time limit should raise and penalize offending player.

    Args:
        None.

    Returns:
        None.
    """
    movement = DummyMovement(label="inc", amount=1.0)
    rules = DummyRules(n_players=2, max_turns=4, allowed_movements=(movement,))
    players = [
        FixedMovementPlayer(movement=movement, sleep_seconds=0.02),
        FixedMovementPlayer(movement=movement),
    ]
    arena = GenericArena(
        rules=rules,
        players=players,
        stop_conditions=[PerTurnTimeLimitCondition(max_seconds_per_turn=0.001)],
    )

    with pytest.raises(ArenaStoppedError) as error_info:
        arena.play()

    assert error_info.value.final_score.get_score(0) == -float("inf")
    assert error_info.value.final_score.get_score(1) == 0.0


def test_game_time_limit_raises_with_penalized_score_for_all() -> None:
    """Whole-game timeout should raise with penalized score for all.

    Args:
        None.

    Returns:
        None.
    """
    movement = DummyMovement(label="inc", amount=1.0)
    rules = DummyRules(n_players=2, max_turns=6, allowed_movements=(movement,))
    players = [
        FixedMovementPlayer(movement=movement, sleep_seconds=0.02),
        FixedMovementPlayer(movement=movement),
    ]
    arena = GenericArena(
        rules=rules,
        players=players,
        stop_conditions=[GameTimeLimitCondition(max_game_seconds=0.001)],
    )

    with pytest.raises(ArenaStoppedError) as error_info:
        arena.play()

    assert error_info.value.final_score.get_score(0) == -float("inf")
    assert error_info.value.final_score.get_score(1) == -float("inf")


def test_score_limit_raises_when_threshold_is_reached() -> None:
    """Score limit should raise once a player reaches configured threshold.

    Args:
        None.

    Returns:
        None.
    """
    movement = DummyMovement(label="inc", amount=2.0)
    rules = DummyRules(n_players=1, max_turns=10, allowed_movements=(movement,))
    players = [FixedMovementPlayer(movement=movement)]
    arena = GenericArena(
        rules=rules,
        players=players,
        stop_conditions=[ScoreLimitCondition(min_score=5.0)],
    )

    with pytest.raises(ArenaStoppedError) as error_info:
        arena.play()

    assert error_info.value.final_score.get_score(0) == 6.0
    assert arena.turns_played() == 3
    assert arena.end_reason() is not None
    assert "score limit reached" in arena.end_reason()


def test_game_history_observer_returns_none_before_game_finish() -> None:
    """History observer should return no record before any game is executed.

    Args:
        None.

    Returns:
        None.
    """
    observer = GameHistoryObserver()

    assert observer.record() is None


def test_game_history_observer_stores_replay_data() -> None:
    """History observer should store positions and movements for replay.

    Args:
        None.

    Returns:
        None.
    """
    movement = DummyMovement(label="inc", amount=1.0)
    rules = DummyRules(n_players=1, max_turns=2, allowed_movements=(movement,))
    players = [FixedMovementPlayer(movement=movement)]
    observer = GameHistoryObserver()
    arena = GenericArena(rules=rules, players=players, observers=[observer])

    arena.play()
    record = observer.record()

    assert record is not None
    assert len(record.turn_records) == 2
    assert len(record.positions()) == 3
    assert len(record.movements()) == 2
    assert isinstance(record.turn_records[0], ArenaTurnRecord)


def test_worker_thread_exception_is_propagated_to_main_thread() -> None:
    """Exceptions from timed worker-thread play call should propagate unchanged.

    Args:
        None.

    Returns:
        None.
    """
    movement = DummyMovement(label="inc", amount=1.0)
    rules = DummyRules(n_players=1, max_turns=1, allowed_movements=(movement,))
    players = [FailingPlayer(error_message="threaded play failed")]
    arena = GenericArena(
        rules=rules,
        players=players,
        stop_conditions=[PerTurnTimeLimitCondition(max_seconds_per_turn=1.0)],
    )

    with pytest.raises(RuntimeError, match="threaded play failed"):
        arena.play()
