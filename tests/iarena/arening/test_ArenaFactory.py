"""Tests for arena factory composition helpers."""

from __future__ import annotations

import pytest

from iarena.arening.ArenaFactory import ArenaFactory
from iarena.arening.ArenaExceptions import ArenaStoppedError
from iarena.arening.GenericArena import GenericArena
from iarena.arening.TerminalArena import TerminalArena
from ._dummy_game import DummyMovement, DummyRules, FixedMovementPlayer, TerminalCapablePlayer


def test_factory_builds_generic_arena_with_history_and_limits() -> None:
    """Factory should compose a generic arena with selected limits and observers.

    Args:
        None.

    Returns:
        None.
    """
    movement = DummyMovement(label="inc", amount=1.0)
    rules = DummyRules(n_players=1, max_turns=10, allowed_movements=(movement,))
    players = [FixedMovementPlayer(movement=movement)]
    arena = ArenaFactory.build(
        rules=rules,
        players=players,
        turn_limit=1,
        store_information=True,
        raise_on_stop=False,
    )

    result = arena.play()

    assert isinstance(arena, GenericArena)
    assert not isinstance(arena, TerminalArena)
    assert result.get_score(0) == -float("inf")
    assert arena.game_record() is not None


def test_factory_builds_terminal_arena_when_requested() -> None:
    """Factory should return terminal arena when terminal mode is enabled.

    Args:
        None.

    Returns:
        None.
    """
    outputs: list[str] = []
    movement = DummyMovement(label="inc", amount=1.0)
    rules = DummyRules(n_players=1, max_turns=1, allowed_movements=(movement,))
    players = [TerminalCapablePlayer(movement=movement)]
    arena = ArenaFactory.build(
        rules=rules,
        players=players,
        terminal=True,
        output_function=outputs.append,
    )

    result = arena.play()

    assert isinstance(arena, TerminalArena)
    assert result.get_score(0) == 1.0
    assert any(line.startswith("Rules:") for line in outputs)


def test_factory_raises_on_stop_by_default() -> None:
    """Factory-built arena should raise on stop unless disabled.

    Args:
        None.

    Returns:
        None.
    """
    movement = DummyMovement(label="inc", amount=1.0)
    rules = DummyRules(n_players=1, max_turns=10, allowed_movements=(movement,))
    players = [FixedMovementPlayer(movement=movement)]
    arena = ArenaFactory.build(
        rules=rules,
        players=players,
        turn_limit=1,
    )

    with pytest.raises(ArenaStoppedError):
        arena.play()
