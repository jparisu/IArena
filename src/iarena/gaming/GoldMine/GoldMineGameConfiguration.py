"""Typed configuration model for GoldMine game generation."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from iarena.desining.gaming.GameConfiguration import GameConfiguration
from iarena.gaming.GoldMine.GoldMine import GoldMineCoordinate, GoldMineSquareMap
from iarena.gaming.GoldMine.GoldMineHintMode import GoldMineHintMode
from iarena.utilizing.square_map.SquareMap import Coordinate, SquareMap


@dataclass(frozen=True, slots=True)
class GoldMineGameConfiguration:
    """Store all typed values required to construct GoldMine rules."""

    cost_map: GoldMineSquareMap
    target: GoldMineCoordinate
    start: GoldMineCoordinate = Coordinate(0, 0)
    hint_mode: GoldMineHintMode = GoldMineHintMode.NONE
    heuristic_map: GoldMineSquareMap | None = None

    @staticmethod
    def _require(values: Mapping[str, Any], key: str) -> Any:
        """Read one required key from a mapping.

        Args:
            values: Source mapping.
            key: Required key.

        Returns:
            Value associated with ``key``.

        Raises:
            ValueError: If the key does not exist.
        """
        if key not in values:
            raise ValueError(f"missing required key '{key}'")
        return values[key]

    @staticmethod
    def _parse_coordinate(raw: Any, key: str) -> GoldMineCoordinate:
        """Parse one coordinate value.

        Args:
            raw: Raw coordinate value.
            key: Field name used in error messages.

        Returns:
            Parsed coordinate value.

        Raises:
            TypeError: If ``raw`` cannot be parsed as a coordinate.
        """
        if isinstance(raw, Coordinate):
            return raw
        if isinstance(raw, (tuple, list)) and len(raw) == 2:
            return Coordinate(int(raw[0]), int(raw[1]))
        if isinstance(raw, Mapping) and "x" in raw and "y" in raw:
            return Coordinate(int(raw["x"]), int(raw["y"]))
        raise TypeError(f"{key} must be Coordinate, (x, y), or {{'x': int, 'y': int}}")

    @staticmethod
    def _parse_map(raw: Any, key: str) -> GoldMineSquareMap:
        """Parse one map value.

        Args:
            raw: Raw map representation.
            key: Field name used in error messages.

        Returns:
            Parsed map value.

        Raises:
            TypeError: If ``raw`` cannot be parsed as a map.
        """
        if isinstance(raw, SquareMap):
            return raw.copy()
        if isinstance(raw, list):
            return SquareMap([[float(value) for value in row] for row in raw])
        raise TypeError(f"{key} must be a list of rows or SquareMap")

    @staticmethod
    def _parse_hint_mode(raw: Any) -> GoldMineHintMode:
        """Parse one hint-mode value.

        Args:
            raw: Raw hint-mode value.

        Returns:
            Parsed hint mode.

        Raises:
            TypeError: If ``raw`` has an unsupported type.
        """
        if isinstance(raw, GoldMineHintMode):
            return raw
        if raw is None or isinstance(raw, str):
            return GoldMineHintMode.from_value(raw)
        raise TypeError("hint_mode must be GoldMineHintMode or string")

    @classmethod
    def from_dict(cls, values: Mapping[str, Any]) -> GoldMineGameConfiguration:
        """Build GoldMine configuration from a dictionary-like payload.

        Args:
            values: Raw configuration mapping.

        Returns:
            Parsed ``GoldMineGameConfiguration``.
        """
        cost_map = cls._parse_map(cls._require(values, "map"), "map")
        target = cls._parse_coordinate(cls._require(values, "target"), "target")
        start = cls._parse_coordinate(values.get("start", (0, 0)), "start")
        hint_mode = cls._parse_hint_mode(values.get("hint_mode"))

        heuristic_map: GoldMineSquareMap | None = None
        if "heuristic_map" in values:
            heuristic_map = cls._parse_map(values["heuristic_map"], "heuristic_map")

        return cls(
            cost_map=cost_map,
            target=target,
            start=start,
            hint_mode=hint_mode,
            heuristic_map=heuristic_map,
        )

    @classmethod
    def from_game_configuration(cls, configuration: GameConfiguration) -> GoldMineGameConfiguration:
        """Build GoldMine configuration from generic game configuration.

        Args:
            configuration: Generic configuration object.

        Returns:
            Parsed ``GoldMineGameConfiguration``.
        """
        return cls.from_dict(configuration.to_dict())

    @classmethod
    def from_yaml(cls, yaml_content: str) -> GoldMineGameConfiguration:
        """Build GoldMine configuration from YAML text.

        Args:
            yaml_content: YAML content string.

        Returns:
            Parsed ``GoldMineGameConfiguration``.
        """
        configuration = GameConfiguration.from_yaml(yaml_content)
        return cls.from_game_configuration(configuration)

    @classmethod
    def from_yaml_file(cls, file_path: str | Path) -> GoldMineGameConfiguration:
        """Build GoldMine configuration from a YAML file.

        Args:
            file_path: Path to the YAML configuration file.

        Returns:
            Parsed ``GoldMineGameConfiguration``.
        """
        configuration = GameConfiguration.from_yaml_file(file_path)
        return cls.from_game_configuration(configuration)

    def to_dict(self) -> dict[str, Any]:
        """Serialize this configuration into a plain dictionary.

        Args:
            None.

        Returns:
            Dictionary with serializable configuration values.
        """
        values: dict[str, Any] = {
            "map": self.cost_map.copy(),
            "start": {"x": self.start.x, "y": self.start.y},
            "target": {"x": self.target.x, "y": self.target.y},
            "hint_mode": self.hint_mode.value,
        }
        if self.heuristic_map is not None:
            values["heuristic_map"] = self.heuristic_map.copy()
        return values
