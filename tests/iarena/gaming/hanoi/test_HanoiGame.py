"""Tests for the Hanoi game registry implementation."""

from __future__ import annotations

import pytest

from iarena.gaming.hanoi.HanoiConfiguration import HanoiConfiguration
from iarena.gaming.hanoi.HanoiGame import HanoiGame
from iarena.gaming.hanoi.HanoiRules import HanoiRules
from iarena.playing.PolyvalentRandomPlayer import PolyvalentRandomPlayer
from iarena.playing.PolyvalentStreamlitPlayer import PolyvalentStreamlitPlayer
from iarena.playing.PolyvalentTerminalPlayer import PolyvalentTerminalPlayer


def test_name_returns_hanoi() -> None:
    game = HanoiGame()

    assert game.name() == "hanoi"


def test_get_component_methods_filter_by_requirement() -> None:
    game = HanoiGame()

    assert len(game.get_configurations(requirements=lambda cls: True)) == 1
    assert len(game.get_rules(requirements=lambda cls: True)) == 1
    assert len(game.get_oracles(requirements=lambda cls: True)) == 1
    assert len(game.get_players(requirements=lambda cls: True)) == 4
    assert len(game.get_renderers(requirements=lambda cls: True)) == 2

    assert game.get_rules(requirements=lambda _cls: False) == set()


def test_get_players_includes_generic_terminal_and_random_players() -> None:
    game = HanoiGame()

    players = game.get_players(requirements=lambda cls: True)

    assert PolyvalentTerminalPlayer in players
    assert PolyvalentRandomPlayer in players
    assert PolyvalentStreamlitPlayer in players


def test_instance_returns_singleton_hanoi_game() -> None:
    first = HanoiGame.instance()
    second = HanoiGame.instance()

    assert first is second


def test_default_configuration_returns_expected_hanoi_setup() -> None:
    configuration = HanoiGame.instance().default_configuration()

    assert configuration.n_pegs == 3
    assert configuration.disks == [0, 0, 0]


def test_terminal_prompt_configuration_uses_terminal_inputs() -> None:
    game = HanoiGame.instance()
    raw_inputs = iter(["4", "2"])
    outputs: list[str] = []

    configuration = game.terminal_prompt_configuration(
        input_fnc=lambda _prompt: next(raw_inputs),
        output_fnc=outputs.append,
    )

    assert configuration.n_pegs == 4
    assert configuration.disks == [0, 0]
    assert outputs[0] == "Guided Hanoi configuration."


def test_streamlit_prompt_configuration_builds_configuration_from_numeric_controls() -> None:
    game = HanoiGame.instance()

    configuration = game.streamlit_prompt_configuration(n_pegs=4, n_disks=2)

    assert configuration.n_pegs == 4
    assert configuration.disks == [0, 0]


def test_generate_rules_builds_hanoi_rules_from_hanoi_configuration() -> None:
    game = HanoiGame()

    rules = game.generate_rules(HanoiConfiguration(n_pegs=3, disks=[0, 0]))

    assert isinstance(rules, HanoiRules)
    assert rules.configuration.n_pegs == 3


def test_generate_rules_rejects_non_hanoi_configuration() -> None:
    game = HanoiGame()

    with pytest.raises(TypeError, match="HanoiConfiguration"):
        game.generate_rules(conf=object())
