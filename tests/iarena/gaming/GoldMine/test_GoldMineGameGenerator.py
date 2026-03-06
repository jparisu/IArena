"""Tests for GoldMine dictionary-based game generation."""

from __future__ import annotations

import pytest

from iarena.desining.gaming.GameConfiguration import GameConfiguration
from iarena.gaming.GoldMine.GoldMineGameConfiguration import GoldMineGameConfiguration
from iarena.gaming.GoldMine.GoldMineGameGenerator import GoldMineGameGenerator
from iarena.gaming.GoldMine.GoldMineGameRules import GoldMineGameRules
from iarena.gaming.GoldMine.GoldMineHintMode import GoldMineHintMode
from iarena.utilizing.square_map.SquareMap import Coordinate, SquareMap


def test_generator_builds_rules_from_list_map_and_tuple_coordinates() -> None:
    """Generator should accept raw lists for map and tuple coordinates.

    Args:
        None.

    Returns:
        None.
    """
    generator = GoldMineGameGenerator()

    rules = generator.build_game(
        {
            "map": [[1.0, 2.0], [3.0, 4.0]],
            "start": (0, 0),
            "target": (1, 1),
            "hint_mode": "proximity",
        }
    )

    assert isinstance(rules, GoldMineGameRules)
    assert rules.hint_mode() is GoldMineHintMode.PROXIMITY
    assert rules.first_position().current_position == Coordinate(0, 0)


def test_generator_supports_coordinate_dict_and_square_map_inputs() -> None:
    """Generator should parse dict coordinates and prebuilt ``SquareMap`` objects.

    Args:
        None.

    Returns:
        None.
    """
    generator = GoldMineGameGenerator()

    rules = generator.build_game(
        {
            "map": SquareMap([[1.0, 2.0], [3.0, 4.0]]),
            "start": {"x": 0, "y": 0},
            "target": {"x": 1, "y": 1},
            "hint_mode": GoldMineHintMode.DENSITY,
            "heuristic_map": [[9.0, 8.0], [7.0, 6.0]],
        }
    )

    assert isinstance(rules, GoldMineGameRules)
    assert rules.hint_mode() is GoldMineHintMode.DENSITY
    assert rules.density_hint(Coordinate(0, 0)) == 9.0


def test_generator_accepts_generic_and_typed_configuration_objects() -> None:
    """Generator should support both generic and game-specific configuration classes.

    Args:
        None.

    Returns:
        None.
    """
    generator = GoldMineGameGenerator()

    generic_configuration = GameConfiguration.from_dict(
        {
            "map": [[1.0, 2.0], [3.0, 4.0]],
            "start": (0, 0),
            "target": (1, 1),
            "hint_mode": "none",
        }
    )
    typed_configuration = GoldMineGameConfiguration.from_dict(
        {
            "map": [[1.0, 2.0], [3.0, 4.0]],
            "start": (0, 0),
            "target": (1, 1),
            "hint_mode": GoldMineHintMode.COMPASS,
        }
    )

    rules_from_generic = generator.build_game(generic_configuration)
    rules_from_typed = generator.build_game(typed_configuration)

    assert isinstance(rules_from_generic, GoldMineGameRules)
    assert isinstance(rules_from_typed, GoldMineGameRules)
    assert rules_from_generic.hint_mode() is GoldMineHintMode.NONE
    assert rules_from_typed.hint_mode() is GoldMineHintMode.COMPASS


def test_generator_validates_required_and_typed_inputs() -> None:
    """Generator should raise clear errors for invalid configurations.

    Args:
        None.

    Returns:
        None.
    """
    generator = GoldMineGameGenerator()

    with pytest.raises(ValueError):
        generator.build_game({"target": (1, 1)})
    with pytest.raises(ValueError):
        generator.build_game({"map": [[1.0]], "start": (0, 0)})
    with pytest.raises(TypeError):
        generator.build_game({"map": 123, "target": (0, 0)})
    with pytest.raises(TypeError):
        generator.build_game({"map": [[1.0]], "target": object()})
    with pytest.raises(TypeError):
        generator.build_game({"map": [[1.0]], "target": (0, 0), "hint_mode": 3})


def test_generator_private_parsing_helpers() -> None:
    """Private helper methods should parse and validate all supported formats.

    Args:
        None.

    Returns:
        None.
    """
    generator = GoldMineGameGenerator()

    assert generator._require({"a": 1}, "a") == 1
    with pytest.raises(ValueError):
        generator._require({}, "missing")

    assert generator._parse_coordinate((2, 3), "coord") == Coordinate(2, 3)
    assert generator._parse_coordinate({"x": 1, "y": 4}, "coord") == Coordinate(1, 4)
    with pytest.raises(TypeError):
        generator._parse_coordinate("bad", "coord")

    parsed_map = generator._parse_map([[1, 2], [3, 4]], "map")
    assert isinstance(parsed_map, SquareMap)
    assert parsed_map[(1, 1)] == 4.0
    with pytest.raises(TypeError):
        generator._parse_map("bad", "map")

    assert generator._parse_hint_mode("none") is GoldMineHintMode.NONE
    assert generator._parse_hint_mode(GoldMineHintMode.COMPASS) is GoldMineHintMode.COMPASS
    with pytest.raises(TypeError):
        generator._parse_hint_mode(123)
