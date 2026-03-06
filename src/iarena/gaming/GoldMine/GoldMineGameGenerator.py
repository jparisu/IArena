"""Dictionary-driven rules generator for GoldMine."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from iarena.desining.gaming.GameConfiguration import GameConfiguration
from iarena.desining.gaming.GameGenerator import GameGenerator
from iarena.desining.gaming.GameRules import GameRules
from iarena.gaming.GoldMine.GoldMine import GoldMineCoordinate, GoldMineSquareMap
from iarena.gaming.GoldMine.GoldMineGameConfiguration import GoldMineGameConfiguration
from iarena.gaming.GoldMine.GoldMineGameRules import GoldMineGameRules
from iarena.gaming.GoldMine.GoldMineHintMode import GoldMineHintMode
from iarena.utilizing.square_map.SquareMap import Coordinate, SquareMap


class GoldMineGameGenerator(GameGenerator):
    """Build GoldMine rules from a plain dictionary configuration."""

    def _require(self, values: Mapping[str, Any], key: str) -> Any:
        """Read one required key from the configuration mapping.

        Args:
            values: Configuration dictionary.
            key: Required key.

        Returns:
            Value associated with ``key``.
        """
        if key not in values:
            raise ValueError(f"missing required key '{key}'")
        return values[key]

    def _parse_coordinate(self, raw: Any, key: str) -> GoldMineCoordinate:
        """Parse coordinate values used by game generation.

        Args:
            raw: Raw coordinate representation.
            key: Field name for error messages.

        Returns:
            Parsed coordinate.
        """
        if isinstance(raw, Coordinate):
            return raw
        if isinstance(raw, (tuple, list)) and len(raw) == 2:
            return Coordinate(int(raw[0]), int(raw[1]))
        if isinstance(raw, Mapping) and "x" in raw and "y" in raw:
            return Coordinate(int(raw["x"]), int(raw["y"]))
        raise TypeError(f"{key} must be Coordinate, (x, y), or {{'x': int, 'y': int}}")

    def _parse_map(self, raw: Any, key: str) -> GoldMineSquareMap:
        """Parse cost-map style values.

        Args:
            raw: Raw map representation.
            key: Field name for error messages.

        Returns:
            Parsed square map.
        """
        if isinstance(raw, SquareMap):
            return raw.copy()
        if isinstance(raw, list):
            return SquareMap([[float(value) for value in row] for row in raw])
        raise TypeError(f"{key} must be a list of rows or SquareMap")

    def _parse_hint_mode(self, raw: Any) -> GoldMineHintMode:
        """Parse hint mode values.

        Args:
            raw: Raw hint mode value.

        Returns:
            Parsed hint mode.
        """
        if isinstance(raw, GoldMineHintMode):
            return raw
        if raw is None or isinstance(raw, str):
            return GoldMineHintMode.from_value(raw)
        raise TypeError("hint_mode must be GoldMineHintMode or string")

    def _as_goldmine_configuration(
        self,
        configuration: GameConfiguration | GoldMineGameConfiguration | Mapping[str, Any],
    ) -> GoldMineGameConfiguration:
        """Normalize supported configuration values into GoldMine configuration.

        Args:
            configuration: Generic or game-specific configuration value.

        Returns:
            Parsed GoldMine configuration instance.
        """
        if isinstance(configuration, GoldMineGameConfiguration):
            return configuration
        if isinstance(configuration, GameConfiguration):
            return GoldMineGameConfiguration.from_game_configuration(configuration)
        return GoldMineGameConfiguration.from_dict(configuration)

    def build_game(
        self,
        configuration: GameConfiguration | GoldMineGameConfiguration | Mapping[str, Any],
    ) -> GameRules:
        """Build a ``GoldMineGameRules`` object from a configuration payload.

        Args:
            configuration: Generic or game-specific configuration payload.

        Returns:
            Configured GoldMine rules object.
        """
        parsed_configuration = self._as_goldmine_configuration(configuration)

        return GoldMineGameRules(
            cost_map=parsed_configuration.cost_map,
            target=parsed_configuration.target,
            start=parsed_configuration.start,
            hint_mode=parsed_configuration.hint_mode,
            heuristic_map=parsed_configuration.heuristic_map,
        )
