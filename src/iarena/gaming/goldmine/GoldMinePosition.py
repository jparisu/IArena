"""GoldMine position model."""

from __future__ import annotations

from collections.abc import Iterator
from typing import TYPE_CHECKING

from iarena.gaming.Position import Position
from iarena.playing.PlayerIndex import PlayerIndex
from iarena.utilizing.mapping.square_map.SquareMap import SquareMap
from iarena.utilizing.mapping.square_map.SquareMapCoordinate import SquareMapCoordinate
from iarena.utilizing.mapping.square_map.SquareMapDirection import SquareMapDirection

if TYPE_CHECKING:
    from iarena.gaming.goldmine.GoldMineRules import GoldMineRules
    from iarena.gaming.Rules import Rules


class GoldMinePosition(Position):
    """Concrete GoldMine position containing player location and dug tiles."""

    map_data: SquareMap[float]
    start: SquareMapCoordinate
    target: SquareMapCoordinate
    current: SquareMapCoordinate
    dug_tiles: set[tuple[int, int]]
    compass_activated: bool
    proximity_activated: bool
    density_activated: bool
    heuristic_map: SquareMap[float]

    def __init__(
        self,
        map_data: SquareMap[float],
        start: SquareMapCoordinate,
        target: SquareMapCoordinate,
        current: SquareMapCoordinate,
        dug_tiles: set[tuple[int, int]],
        compass_activated: bool = False,
        proximity_activated: bool = False,
        density_activated: bool = False,
        heuristic_map: SquareMap[float] | None = None,
    ) -> None:
        """Create one GoldMine position.

        Args:
            map_data: Digging-cost map.
            start: Game start coordinate.
            target: Gold target coordinate.
            current: Current player coordinate.
            dug_tiles: Dug coordinates represented as `(x, y)` tuples.
            compass_activated: Enable compass hints.
            proximity_activated: Enable proximity hints.
            density_activated: Enable density hints.
            heuristic_map: Optional density-heuristic map.
        """
        for name, coordinate in (("start", start), ("target", target), ("current", current)):
            if not map_data.in_bounds(coordinate):
                raise ValueError(f"{name} must be inside map bounds.")

        if current.as_tuple() not in dug_tiles:
            raise ValueError("current coordinate must be present in dug_tiles.")
        if start.as_tuple() not in dug_tiles:
            raise ValueError("start coordinate must be present in dug_tiles.")

        for coordinate_as_tuple in dug_tiles:
            dug_coordinate = SquareMapCoordinate.from_tuple(coordinate_as_tuple)
            map_data.require_in_bounds(dug_coordinate, name="dug tile")

        self.map_data = map_data
        self.start = start
        self.target = target
        self.current = current
        self.dug_tiles = set(dug_tiles)
        self.compass_activated = bool(compass_activated)
        self.proximity_activated = bool(proximity_activated)
        self.density_activated = bool(density_activated)
        if heuristic_map is None:
            heuristic_map = SquareMap.zeros(self.map_data.n_rows(), self.map_data.n_cols())
        self.heuristic_map = heuristic_map
        self._rules: GoldMineRules | None = None

    def hash(self) -> int:
        """Return a stable hash representation of the position.

        Returns:
            int: Deterministic position hash.
        """
        return hash(
            (
                self.current.as_tuple(),
                tuple(sorted(self.dug_tiles)),
                self.target.as_tuple(),
                self.start.as_tuple(),
            ),
        )

    def __str__(self) -> str:
        """Return a compact textual representation of the position."""
        direction_text = ", ".join(
            f"{direction.name}:{self.get_cost_from_direction(direction)}" for direction in self.get_valid_directions()
        )
        return (
            "GoldMinePosition("
            f"current={self.current.as_tuple()}, "
            f"target={self.target.as_tuple()}, "
            f"dug={len(self.dug_tiles)}, "
            f"moves=[{direction_text}]"
            ")"
        )

    def next_player(self) -> PlayerIndex:
        """Return the next player index.

        Returns:
            PlayerIndex: Always `PlayerIndex(0)` for this single-player game.
        """
        return PlayerIndex(0)

    def get_rules(self) -> Rules:
        """Return rules associated with this position.

        Returns:
            Rules: GoldMine rules instance.
        """
        if self._rules is None:
            from iarena.gaming.goldmine.GoldMineConfiguration import GoldMineConfiguration
            from iarena.gaming.goldmine.GoldMineRules import GoldMineRules

            self._rules = GoldMineRules(
                GoldMineConfiguration(
                    n_rows=self.map_data.n_rows(),
                    n_cols=self.map_data.n_cols(),
                    start=self.start,
                    target=self.target,
                    map_data=self.map_data.to_numpy(dtype=float).tolist(),
                    compass_activated=self.compass_activated,
                    proximity_activated=self.proximity_activated,
                    density_activated=self.density_activated,
                    heuristic_map_data=self.heuristic_map.to_numpy(dtype=float).tolist(),
                ),
            )
        return self._rules

    def get_accumulated_cost(self) -> float:
        """Return cumulative digging cost for this position."""
        rules = self.get_rules()
        if not isinstance(rules, GoldMineRules):
            raise TypeError("rules must be GoldMineRules.")
        return rules.get_accumulated_cost(self)

    def get_compass(self) -> SquareMapDirection:
        """Return compass hint for current coordinate."""
        rules = self.get_rules()
        if not isinstance(rules, GoldMineRules):
            raise TypeError("rules must be GoldMineRules.")
        return rules.get_compass_hint(self)

    def get_proximity(self) -> int:
        """Return proximity hint for current coordinate."""
        rules = self.get_rules()
        if not isinstance(rules, GoldMineRules):
            raise TypeError("rules must be GoldMineRules.")
        return rules.get_proximity_hint(self)

    def get_density(self) -> float:
        """Return density hint for current coordinate."""
        rules = self.get_rules()
        if not isinstance(rules, GoldMineRules):
            raise TypeError("rules must be GoldMineRules.")
        return rules.get_density_hint(self)

    def get_valid_directions(self) -> Iterator[SquareMapDirection]:
        """Yield all valid directions from current coordinate."""
        yield from self.map_data.possible_directions(self.current)

    def get_cost_from_direction(self, direction: SquareMapDirection) -> float:
        """Return movement cost for one direction.

        Args:
            direction: Candidate direction.

        Returns:
            float: `0.0` when destination tile was already dug; map value otherwise.
        """
        next_coordinate = self.current.from_direction(direction)
        if next_coordinate.as_tuple() in self.dug_tiles:
            return 0.0
        return float(self.map_data[next_coordinate])

    def get_directions_with_cost(self) -> Iterator[tuple[SquareMapDirection, float]]:
        """Yield valid directions with movement costs."""
        for direction in self.get_valid_directions():
            yield direction, self.get_cost_from_direction(direction)
