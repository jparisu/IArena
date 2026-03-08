"""Tests for the TicTacToe game registry implementation."""

from __future__ import annotations

import pytest

from iarena.gaming.tictactoe.TicTacToeConfiguration import TicTacToeConfiguration
from iarena.gaming.tictactoe.TicTacToeGame import TicTacToeGame
from iarena.gaming.tictactoe.TicTacToeRules import TicTacToeRules
from iarena.playing.PolyvalentRandomPlayer import PolyvalentRandomPlayer
from iarena.playing.PolyvalentTerminalPlayer import PolyvalentTerminalPlayer


def test_name_returns_tictactoe() -> None:
    game = TicTacToeGame()

    assert game.name() == "tictactoe"


def test_get_component_methods_filter_by_requirement() -> None:
    game = TicTacToeGame()

    assert len(game.get_configurations(requirements=lambda cls: True)) == 1
    assert len(game.get_rules(requirements=lambda cls: True)) == 1
    assert len(game.get_oracles(requirements=lambda cls: True)) == 0
    assert len(game.get_players(requirements=lambda cls: True)) == 2
    assert len(game.get_renderers(requirements=lambda cls: True)) == 1

    assert game.get_rules(requirements=lambda _cls: False) == set()


def test_get_players_includes_generic_terminal_and_random_players() -> None:
    game = TicTacToeGame()

    players = game.get_players(requirements=lambda cls: True)

    assert PolyvalentTerminalPlayer in players
    assert PolyvalentRandomPlayer in players


def test_instance_returns_singleton_tictactoe_game() -> None:
    first = TicTacToeGame.instance()
    second = TicTacToeGame.instance()

    assert first is second


def test_default_configuration_returns_expected_tictactoe_setup() -> None:
    configuration = TicTacToeGame.instance().default_configuration()

    assert configuration.board_size == 3
    assert configuration.win_length == 3


def test_terminal_prompt_configuration_uses_terminal_inputs() -> None:
    game = TicTacToeGame.instance()
    raw_inputs = iter(["4", "3"])
    outputs: list[str] = []

    configuration = game.terminal_prompt_configuration(
        input_fnc=lambda _prompt: next(raw_inputs),
        output_fnc=outputs.append,
    )

    assert configuration.board_size == 4
    assert configuration.win_length == 3
    assert outputs[0] == "Guided TicTacToe configuration."


def test_generate_rules_builds_tictactoe_rules_from_tictactoe_configuration() -> None:
    game = TicTacToeGame()

    rules = game.generate_rules(TicTacToeConfiguration(board_size=3, win_length=3))

    assert isinstance(rules, TicTacToeRules)
    assert rules.configuration.board_size == 3


def test_generate_rules_rejects_non_tictactoe_configuration() -> None:
    game = TicTacToeGame()

    with pytest.raises(TypeError, match="TicTacToeConfiguration"):
        game.generate_rules(conf=object())
