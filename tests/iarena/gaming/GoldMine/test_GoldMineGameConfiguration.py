"""Tests for typed GoldMine game configuration parsing and serialization."""

from __future__ import annotations

from pathlib import Path

import pytest

from iarena.desining.gaming.GameConfiguration import GameConfiguration
from iarena.gaming.GoldMine.GoldMineGameConfiguration import GoldMineGameConfiguration
from iarena.gaming.GoldMine.GoldMineHintMode import GoldMineHintMode
from iarena.utilizing.square_map.SquareMap import Coordinate, SquareMap


def test_configuration_from_dict_parses_all_supported_shapes() -> None:
    """Configuration parser should accept all supported value shapes.

    Args:
        None.

    Returns:
        None.
    """
    configuration = GoldMineGameConfiguration.from_dict(
        {
            "map": [[1.0, 2.0], [3.0, 4.0]],
            "start": {"x": 0, "y": 1},
            "target": (1, 1),
            "hint_mode": "proximity",
            "heuristic_map": [[9.0, 8.0], [7.0, 6.0]],
        }
    )

    assert configuration.start == Coordinate(0, 1)
    assert configuration.target == Coordinate(1, 1)
    assert configuration.hint_mode is GoldMineHintMode.PROXIMITY
    assert configuration.heuristic_map is not None
    assert configuration.heuristic_map[(0, 0)] == 9.0


def test_configuration_from_dict_validates_required_and_types() -> None:
    """Configuration parser should reject missing and invalid values.

    Args:
        None.

    Returns:
        None.
    """
    with pytest.raises(ValueError):
        GoldMineGameConfiguration.from_dict({"target": (0, 0)})
    with pytest.raises(ValueError):
        GoldMineGameConfiguration.from_dict({"map": [[1.0]], "start": (0, 0)})
    with pytest.raises(TypeError):
        GoldMineGameConfiguration.from_dict({"map": 3, "target": (0, 0)})
    with pytest.raises(TypeError):
        GoldMineGameConfiguration.from_dict({"map": [[1.0]], "target": object()})
    with pytest.raises(TypeError):
        GoldMineGameConfiguration.from_dict({"map": [[1.0]], "target": (0, 0), "hint_mode": 1.2})


def test_configuration_from_generic_game_configuration() -> None:
    """GoldMine configuration should parse from generic game configuration.

    Args:
        None.

    Returns:
        None.
    """
    generic_configuration = GameConfiguration.from_dict(
        {
            "map": SquareMap([[1.0, 2.0], [3.0, 4.0]]),
            "start": (0, 0),
            "target": (1, 1),
            "hint_mode": GoldMineHintMode.DENSITY,
            "heuristic_map": [[4.0, 3.0], [2.0, 1.0]],
        }
    )

    parsed = GoldMineGameConfiguration.from_game_configuration(generic_configuration)

    assert parsed.hint_mode is GoldMineHintMode.DENSITY
    assert parsed.target == Coordinate(1, 1)
    assert parsed.heuristic_map is not None
    assert parsed.heuristic_map[(1, 1)] == 1.0


def test_configuration_yaml_helpers(tmp_path: Path) -> None:
    """YAML helpers should parse YAML text and YAML files.

    Args:
        tmp_path: Temporary directory injected by pytest.

    Returns:
        None.
    """
    pytest.importorskip("yaml")

    yaml_content = "\n".join(
        [
            "map:",
            "  - [1.0, 2.0]",
            "  - [3.0, 4.0]",
            "start: [0, 0]",
            "target: [1, 1]",
            "hint_mode: compass",
        ]
    )

    from_text = GoldMineGameConfiguration.from_yaml(yaml_content)
    assert from_text.hint_mode is GoldMineHintMode.COMPASS

    yaml_path = tmp_path / "goldmine.yaml"
    yaml_path.write_text(yaml_content, encoding="utf-8")
    from_file = GoldMineGameConfiguration.from_yaml_file(yaml_path)
    assert from_file.target == Coordinate(1, 1)


def test_configuration_to_dict_roundtrip_contains_key_fields() -> None:
    """Serialization should include all key fields.

    Args:
        None.

    Returns:
        None.
    """
    configuration = GoldMineGameConfiguration(
        cost_map=SquareMap([[1.0, 2.0], [3.0, 4.0]]),
        start=Coordinate(0, 0),
        target=Coordinate(1, 1),
        hint_mode=GoldMineHintMode.NONE,
    )

    serialized = configuration.to_dict()

    assert "map" in serialized
    assert serialized["start"] == {"x": 0, "y": 0}
    assert serialized["target"] == {"x": 1, "y": 1}
    assert serialized["hint_mode"] == "none"
