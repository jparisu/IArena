"""GoldMine configuration model."""

from __future__ import annotations

from typing import Any

from iarena.gaming.Configuration import Configuration
from iarena.utilizing.mapping.square_map.SquareMapCoordinate import SquareMapCoordinate


class GoldMineConfiguration(Configuration):
    """Configuration used to build one GoldMine ruleset."""

    n_rows: int
    n_cols: int
    start: SquareMapCoordinate | None
    target: SquareMapCoordinate | None
    map_data: list[list[float]] | None
    map_generator: str
    map_generator_params: dict[str, Any]
    integer: bool
    seed: int | None
    compass_activated: bool
    proximity_activated: bool
    density_activated: bool
    heuristic_map_data: list[list[float]] | None

    def __init__(
        self,
        n_rows: int = 6,
        n_cols: int = 6,
        start: SquareMapCoordinate | None = None,
        target: SquareMapCoordinate | None = None,
        map_data: list[list[float]] | None = None,
        map_generator: str = "uniform",
        map_generator_params: dict[str, Any] | None = None,
        integer: bool = False,
        seed: int | None = 0,
        compass_activated: bool = False,
        proximity_activated: bool = False,
        density_activated: bool = False,
        heuristic_map_data: list[list[float]] | None = None,
    ) -> None:
        """Store validated GoldMine configuration values.

        Args:
            n_rows: Number of map rows.
            n_cols: Number of map columns.
            start: Optional explicit start coordinate.
            target: Optional explicit target coordinate.
            map_data: Optional explicit map values.
            map_generator: Generator name when `map_data` is absent.
            map_generator_params: Additional map-generator kwargs.
            integer: Whether generated map values are rounded.
            seed: Optional random seed.
            compass_activated: Enable compass hints.
            proximity_activated: Enable proximity hints.
            density_activated: Enable density hints.
            heuristic_map_data: Optional explicit density map.
        """
        if n_rows < 1 or n_cols < 1:
            raise ValueError("n_rows and n_cols must be at least 1.")
        if not map_generator.strip():
            raise ValueError("map_generator must not be empty.")

        self.n_rows = int(n_rows)
        self.n_cols = int(n_cols)
        self.start = start
        self.target = target
        self.map_data = map_data
        self.map_generator = map_generator.strip().lower()
        self.map_generator_params = dict(map_generator_params or {})
        self.integer = bool(integer)
        self.seed = seed
        self.compass_activated = bool(compass_activated)
        self.proximity_activated = bool(proximity_activated)
        self.density_activated = bool(density_activated)
        self.heuristic_map_data = heuristic_map_data

        self._validate_map_data(self.map_data, "map_data")
        self._validate_map_data(self.heuristic_map_data, "heuristic_map_data")
        self._validate_coordinate(self.start, "start")
        self._validate_coordinate(self.target, "target")

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> GoldMineConfiguration:
        """Build one configuration instance from a dictionary payload.

        Args:
            data: Mapping with optional map, generation, and hint keys.

        Returns:
            GoldMineConfiguration: Parsed configuration.
        """
        n_rows = int(data.get("n_rows", data.get("n", data.get("height", 6))))
        n_cols = int(data.get("n_cols", data.get("m", data.get("width", 6))))
        return cls(
            n_rows=n_rows,
            n_cols=n_cols,
            start=cls._parse_coordinate(data.get("start", data.get("starting_position"))),
            target=cls._parse_coordinate(data.get("target", data.get("target_position"))),
            map_data=data.get("map_data"),
            map_generator=str(data.get("map_generator", "uniform")),
            map_generator_params=dict(data.get("map_generator_params", data.get("map_configuration", {}))),
            integer=bool(data.get("integer", False)),
            seed=data.get("seed"),
            compass_activated=bool(data.get("compass_activated", data.get("compass", False))),
            proximity_activated=bool(data.get("proximity_activated", data.get("proximity", False))),
            density_activated=bool(data.get("density_activated", data.get("density", False))),
            heuristic_map_data=data.get("heuristic_map_data"),
        )

    @staticmethod
    def _parse_coordinate(raw: Any) -> SquareMapCoordinate | None:
        """Parse one raw coordinate payload."""
        if raw is None:
            return None
        if isinstance(raw, SquareMapCoordinate):
            return raw
        if isinstance(raw, (tuple, list)) and len(raw) == 2:
            return SquareMapCoordinate(int(raw[0]), int(raw[1]))
        if isinstance(raw, dict):
            return SquareMapCoordinate(int(raw["x"]), int(raw["y"]))
        raise TypeError("Coordinate must be SquareMapCoordinate, tuple/list of length 2, dict, or None.")

    def _validate_map_data(self, map_data: list[list[float]] | None, field_name: str) -> None:
        """Validate map-like payload dimensions.

        Args:
            map_data: Candidate map data.
            field_name: Name used in error messages.
        """
        if map_data is None:
            return
        if len(map_data) != self.n_rows:
            raise ValueError(f"{field_name} must contain exactly n_rows rows.")
        if any(len(row) != self.n_cols for row in map_data):
            raise ValueError(f"{field_name} rows must contain exactly n_cols values.")

    def _validate_coordinate(self, coordinate: SquareMapCoordinate | None, field_name: str) -> None:
        """Validate that one optional coordinate is in bounds.

        Args:
            coordinate: Coordinate to validate.
            field_name: Name used in error messages.
        """
        if coordinate is None:
            return
        if coordinate.x < 0 or coordinate.x >= self.n_rows:
            raise ValueError(f"{field_name}.x must be within [0, n_rows).")
        if coordinate.y < 0 or coordinate.y >= self.n_cols:
            raise ValueError(f"{field_name}.y must be within [0, n_cols).")
