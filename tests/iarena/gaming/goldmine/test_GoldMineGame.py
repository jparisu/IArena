"""Tests for the GoldMine game registry implementation."""

from __future__ import annotations

import pytest

from iarena.gaming.goldmine.GoldMineConfiguration import GoldMineConfiguration
from iarena.gaming.goldmine.GoldMineGame import GoldMineGame
from iarena.gaming.goldmine.GoldMineRules import GoldMineRules
from iarena.playing.PolyvalentRandomPlayer import PolyvalentRandomPlayer


def test_name_returns_goldmine() -> None:
    game = GoldMineGame()

    assert game.name() == "goldmine"


def test_get_component_methods_filter_by_requirement() -> None:
    game = GoldMineGame()

    assert len(game.get_configurations(requirements=lambda cls: True)) == 1
    assert len(game.get_rules(requirements=lambda cls: True)) == 1
    assert len(game.get_oracles(requirements=lambda cls: True)) == 0
    assert len(game.get_players(requirements=lambda cls: True)) == 1
    assert len(game.get_renderers(requirements=lambda cls: True)) == 0

    assert game.get_rules(requirements=lambda _cls: False) == set()


def test_get_players_includes_random_player() -> None:
    game = GoldMineGame()

    players = game.get_players(requirements=lambda cls: True)

    assert PolyvalentRandomPlayer in players


def test_instance_returns_singleton_goldmine_game() -> None:
    first = GoldMineGame.instance()
    second = GoldMineGame.instance()

    assert first is second


def test_default_configuration_returns_expected_goldmine_setup() -> None:
    configuration = GoldMineGame.instance().default_configuration()

    assert configuration.n_rows == 6
    assert configuration.n_cols == 6


def test_terminal_prompt_configuration_uses_terminal_inputs() -> None:
    game = GoldMineGame.instance()
    raw_inputs = iter(["4", "5"])
    outputs: list[str] = []

    configuration = game.terminal_prompt_configuration(
        input_fnc=lambda _prompt: next(raw_inputs),
        output_fnc=outputs.append,
    )

    assert configuration.n_rows == 4
    assert configuration.n_cols == 5
    assert outputs[0] == "Guided GoldMine configuration."


def test_generate_rules_builds_goldmine_rules_from_goldmine_configuration() -> None:
    game = GoldMineGame()

    rules = game.generate_rules(GoldMineConfiguration(n_rows=3, n_cols=3))

    assert isinstance(rules, GoldMineRules)
    assert rules.configuration.n_rows == 3


def test_generate_rules_rejects_non_goldmine_configuration() -> None:
    game = GoldMineGame()

    with pytest.raises(TypeError, match="GoldMineConfiguration"):
        game.generate_rules(conf=object())
