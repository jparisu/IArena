"""Tests for the game governor singleton registry behavior."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import pytest

from iarena.gaming.Game import Game
from iarena.gaming.GameGovernor import GameGovernor
from iarena.gaming.hanoi.HanoiGame import HanoiGame


class _DummyGame(Game):
    """Minimal concrete game used to test governor registration behavior."""

    def name(self) -> str:
        return "dummy-test-game"

    def get_configurations(self, requirements: Callable[[Any], bool]) -> set[type[object]]:
        _ = requirements
        return set()

    def get_rules(self, requirements: Callable[[Any], bool]) -> set[type[object]]:
        _ = requirements
        return set()

    def get_oracles(self, requirements: Callable[[Any], bool]) -> set[type[object]]:
        _ = requirements
        return set()

    def get_players(self, requirements: Callable[[Any], bool]) -> set[type[object]]:
        _ = requirements
        return set()

    def get_renderers(self, requirements: Callable[[Any], bool]) -> set[type[object]]:
        _ = requirements
        return set()

    def generate_rules(self, conf: object) -> object:
        _ = conf
        raise NotImplementedError


def test_instance_returns_singleton() -> None:
    first = GameGovernor.instance()
    second = GameGovernor.instance()

    assert first is second


def test_get_game_names_includes_hanoi() -> None:
    assert "goldmine" in GameGovernor.get_game_names()
    assert "hanoi" in GameGovernor.get_game_names()
    assert "tictactoe" in GameGovernor.get_game_names()


def test_find_game_returns_hanoi_singleton_for_matching_requirement() -> None:
    game = GameGovernor.find_game(
        name="hanoi",
        requirement=lambda candidate: bool(candidate.get_renderers(lambda cls: "Terminal" in cls.__name__)),
    )

    assert game is HanoiGame.instance()


def test_find_game_returns_none_when_requirement_fails_and_throw_is_false() -> None:
    result = GameGovernor.find_game(
        name="hanoi",
        requirement=lambda _candidate: False,
        throw=False,
    )

    assert result is None


def test_find_game_raises_key_error_for_unknown_game() -> None:
    with pytest.raises(KeyError, match="Unknown game"):
        GameGovernor.find_game(name="not-a-game", requirement=lambda _candidate: True, throw=True)


def test_add_game_registers_game_and_exposes_its_name() -> None:
    game = _DummyGame()
    GameGovernor.add_game(game)
    try:
        names = GameGovernor.get_game_names()
        assert game.name() in names
        assert GameGovernor.find_game(name=game.name(), requirement=lambda _candidate: True) is game
    finally:
        GameGovernor.instance().remove_value(game.name())
