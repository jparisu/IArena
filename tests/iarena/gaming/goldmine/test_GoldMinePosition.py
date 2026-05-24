"""Tests for the GoldMine position model."""

from __future__ import annotations

from iarena.gaming.goldmine.GoldMineConfiguration import GoldMineConfiguration
from iarena.gaming.goldmine.GoldMinePosition import GoldMinePosition
from iarena.gaming.goldmine.GoldMineRules import GoldMineRules
from iarena.playing.PlayerIndex import PlayerIndex
from iarena.utilizing.mapping.square_map.SquareMapCoordinate import SquareMapCoordinate


def _position() -> GoldMinePosition:
    rules = GoldMineRules(
        GoldMineConfiguration(
            n_rows=2,
            n_cols=2,
            start=SquareMapCoordinate(0, 0),
            target=SquareMapCoordinate(1, 1),
            map_data=[[0.0, 2.0], [3.0, 4.0]],
        ),
    )
    return GoldMinePosition(rules=rules, current=SquareMapCoordinate(0, 0), dug_tiles={(0, 0)})


def test_init_exposes_rules_link() -> None:
    position = _position()

    assert isinstance(position.get_rules(), GoldMineRules)


def test_hash_changes_with_position_state() -> None:
    first = _position()
    rules = first.get_rules()
    second = GoldMinePosition(
        rules=rules,
        current=SquareMapCoordinate(0, 1),
        dug_tiles={(0, 0), (0, 1)},
    )

    assert first.hash() != second.hash()


def test_next_player_returns_single_player_index_zero() -> None:
    assert _position().next_player() == PlayerIndex(0)


def test_get_rules_returns_goldmine_rules() -> None:
    position = _position()

    rules = position.get_rules()

    assert isinstance(rules, GoldMineRules)
    assert isinstance(rules.configuration, GoldMineConfiguration)
