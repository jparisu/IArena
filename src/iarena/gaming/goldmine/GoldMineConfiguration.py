"""GoldMine configuration model."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from iarena.gaming.Configuration import Configuration
from iarena.utilizing.mapping.square_map.SquareMap import SquareMap
from iarena.utilizing.mapping.square_map.SquareMapCoordinate import SquareMapCoordinate
from iarena.utilizing.randoming.RandomGenerator import RandomGenerator


class GoldMineConfiguration(Configuration):
    """Configuration used to build one GoldMine ruleset."""

    n_rows: int
    n_cols: int
    start: SquareMapCoordinate | None
    target: SquareMapCoordinate | None
    map_data: SquareMap[float] | list[list[float]] | None
    map_generator: str
    map_generator_params: dict[str, Any]
    integer: bool
    seed: int | None
    compass_activated: bool
    proximity_activated: bool
    density_activated: bool
    heuristic_map_data: SquareMap[float] | list[list[float]] | None

    def __init__(
        self,
        n_rows: int | None = None,
        n_cols: int | None = None,
        start: SquareMapCoordinate | tuple[int, int] | list[int] | dict[str, int] | None = None,
        target: SquareMapCoordinate | tuple[int, int] | list[int] | dict[str, int] | None = None,
        map_data: SquareMap[float] | Iterable[Iterable[float]] | None = None,
        map_generator: str = "uniform",
        map_generator_params: dict[str, Any] | None = None,
        integer: bool = False,
        seed: int | None = 0,
        compass_activated: bool = False,
        proximity_activated: bool = False,
        density_activated: bool = False,
        heuristic_map_data: SquareMap[float] | Iterable[Iterable[float]] | None = None,
    ) -> None:
        """Store validated GoldMine configuration values.

        Args:
            n_rows: Number of map rows. If omitted, inferred from provided map when available.
            n_cols: Number of map columns. If omitted, inferred from provided map when available.
            start: Optional explicit start coordinate.
            target: Optional explicit target coordinate.
            map_data: Optional explicit map values as `SquareMap` or matrix.
            map_generator: Generator name when `map_data` is absent.
            map_generator_params: Additional map-generator kwargs.
            integer: Whether generated map values are rounded.
            seed: Optional random seed.
            compass_activated: Enable compass hints.
            proximity_activated: Enable proximity hints.
            density_activated: Enable density hints.
            heuristic_map_data: Optional explicit density map as `SquareMap` or matrix.
        """
        if not map_generator.strip():
            raise ValueError("map_generator must not be empty.")

        parsed_map_data = self._parse_map_data(map_data)
        parsed_heuristic_map_data = self._parse_map_data(heuristic_map_data)
        resolved_n_rows, resolved_n_cols = self._resolve_dimensions(
            n_rows=n_rows,
            n_cols=n_cols,
            map_data=parsed_map_data,
            heuristic_map_data=parsed_heuristic_map_data,
        )
        if resolved_n_rows < 1 or resolved_n_cols < 1:
            raise ValueError("n_rows and n_cols must be at least 1.")

        self.n_rows = resolved_n_rows
        self.n_cols = resolved_n_cols
        self.seed = seed
        parsed_start = self._parse_coordinate(start)
        parsed_target = self._parse_coordinate(target)
        self.start, self.target = self._resolve_coordinates(parsed_start, parsed_target)
        self.map_data = parsed_map_data
        self.map_generator = map_generator.strip().lower()
        self.map_generator_params = dict(map_generator_params or {})
        self.integer = bool(integer)
        self.compass_activated = bool(compass_activated)
        self.proximity_activated = bool(proximity_activated)
        self.density_activated = bool(density_activated)
        self.heuristic_map_data = parsed_heuristic_map_data

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
        n_rows_raw = data.get("n_rows", data.get("n", data.get("height")))
        n_cols_raw = data.get("n_cols", data.get("m", data.get("width")))
        return cls(
            n_rows=int(n_rows_raw) if n_rows_raw is not None else None,
            n_cols=int(n_cols_raw) if n_cols_raw is not None else None,
            start=cls._parse_coordinate(data.get("start", data.get("starting_position"))),
            target=cls._parse_coordinate(data.get("target", data.get("target_position"))),
            map_data=data.get("map_data", data.get("map")),
            map_generator=str(data.get("map_generator", "uniform")),
            map_generator_params=dict(data.get("map_generator_params", data.get("map_configuration", {}))),
            integer=bool(data.get("integer", False)),
            seed=data.get("seed"),
            compass_activated=bool(data.get("compass_activated", data.get("compass", False))),
            proximity_activated=bool(data.get("proximity_activated", data.get("proximity", False))),
            density_activated=bool(data.get("density_activated", data.get("density", False))),
            heuristic_map_data=data.get("heuristic_map_data", data.get("heuristic_map")),
        )

    def _resolve_dimensions(
        self,
        n_rows: int | None,
        n_cols: int | None,
        map_data: SquareMap[float] | list[list[float]] | None,
        heuristic_map_data: SquareMap[float] | list[list[float]] | None,
    ) -> tuple[int, int]:
        """Resolve map dimensions from explicit arguments or map payloads."""
        source_map = map_data if map_data is not None else heuristic_map_data
        inferred_n_rows: int | None = None
        inferred_n_cols: int | None = None
        if source_map is not None:
            inferred_n_rows, inferred_n_cols = self._map_size(source_map)

        resolved_n_rows = int(n_rows) if n_rows is not None else inferred_n_rows if inferred_n_rows is not None else 6
        resolved_n_cols = int(n_cols) if n_cols is not None else inferred_n_cols if inferred_n_cols is not None else 6
        return resolved_n_rows, resolved_n_cols

    def _resolve_coordinates(
        self,
        start: SquareMapCoordinate | None,
        target: SquareMapCoordinate | None,
    ) -> tuple[SquareMapCoordinate, SquareMapCoordinate]:
        """Resolve start and target coordinates from special/default values."""
        rng = RandomGenerator(self.seed)
        if start is None:
            resolved_start = SquareMapCoordinate(0, 0)
        elif start.x == -1 and start.y == -1:
            resolved_start = self._generate_random_coordinate(rng)
        else:
            resolved_start = start

        resolved_target = target if target is not None else self._generate_random_coordinate(rng)
        return resolved_start, resolved_target

    def _generate_random_coordinate(self, rng: RandomGenerator) -> SquareMapCoordinate:
        """Generate one random in-bounds coordinate."""
        return SquareMapCoordinate(rng.randint(self.n_rows), rng.randint(self.n_cols))

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

    @staticmethod
    def _parse_map_data(raw: SquareMap[float] | Iterable[Iterable[float]] | None) -> SquareMap[float] | list[list[float]] | None:
        """Parse one raw map payload.

        Args:
            raw: Candidate map data as `SquareMap`, matrix-like iterable, or `None`.

        Returns:
            SquareMap[float] | list[list[float]] | None: Parsed map payload.
        """
        if raw is None:
            return None
        if isinstance(raw, SquareMap):
            return raw
        return [list(row) for row in raw]

    def _map_size(self, map_data: SquareMap[float] | list[list[float]]) -> tuple[int, int]:
        """Return row and column dimensions for one map payload."""
        if isinstance(map_data, SquareMap):
            return map_data.size()
        return len(map_data), len(map_data[0]) if map_data else 0

    def _validate_map_data(self, map_data: SquareMap[float] | list[list[float]] | None, field_name: str) -> None:
        """Validate map-like payload dimensions.

        Args:
            map_data: Candidate map data.
            field_name: Name used in error messages.
        """
        if map_data is None:
            return
        n_rows, n_cols = self._map_size(map_data)
        if n_rows != self.n_rows:
            raise ValueError(f"{field_name} must contain exactly n_rows rows.")
        if n_cols != self.n_cols:
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
