"""Tests for GoldMine game orchestrator wiring."""

from __future__ import annotations

from iarena.gaming.GoldMine.GoldMineGameGenerator import GoldMineGameGenerator
from iarena.gaming.GoldMine.GoldMineGameRules import GoldMineGameRules
from iarena.gaming.GoldMine.GoldMineMovement import GoldMineMovement
from iarena.gaming.GoldMine.GoldMineOrchestrator import GoldMineOrchestrator
from iarena.gaming.GoldMine.GoldMinePlayablePlayer import GoldMinePlayablePlayer
from iarena.gaming.GoldMine.GoldMinePlayer import GoldMinePlayer
from iarena.gaming.GoldMine.GoldMinePosition import GoldMinePosition


def test_orchestrator_returns_goldmine_component_classes() -> None:
    """Orchestrator should expose concrete GoldMine class references.

    Args:
        None.

    Returns:
        None.
    """
    orchestrator = GoldMineOrchestrator()

    assert orchestrator.game_rules_class() is GoldMineGameRules
    assert orchestrator.position_class() is GoldMinePosition
    assert orchestrator.movement_class() is GoldMineMovement
    assert orchestrator.player_class() is GoldMinePlayer
    assert orchestrator.graphical_player_class() is GoldMinePlayablePlayer
    assert orchestrator.game_generator_class() is GoldMineGameGenerator
    assert orchestrator.text_renderable_class() is GoldMinePosition
    assert orchestrator.plot_renderable_class() is GoldMinePosition


def test_orchestrator_capability_flags_match_exposed_classes() -> None:
    """Capability booleans should match optional classes returned by orchestrator.

    Args:
        None.

    Returns:
        None.
    """
    orchestrator = GoldMineOrchestrator()

    assert orchestrator.has_game_generator() is True
    assert orchestrator.has_text_rendering() is True
    assert orchestrator.has_plotting() is True
    assert orchestrator.has_terminal_player() is False
    assert orchestrator.has_graphical_player() is True
    assert orchestrator.has_game_solver() is False
