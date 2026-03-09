"""GoldMine rules implementation."""

from __future__ import annotations

from collections.abc import Iterator
from typing import TYPE_CHECKING, Any

from iarena.gaming.Rules import Rules
from iarena.playing.PlayerIndex import PlayerIndex
from iarena.scoring.Score import Score
from iarena.scoring.ScoreBoard import ScoreBoard
from iarena.utilizing.mapping.square_map.generators.MapFactory import MapFactory
from iarena.utilizing.mapping.square_map.SquareMap import SquareMap
from iarena.utilizing.mapping.square_map.draw_square_map import generate_plot_map
from iarena.utilizing.mapping.square_map.SquareMapCoordinate import SquareMapCoordinate
from iarena.utilizing.mapping.square_map.SquareMapDirection import SquareMapDirection
from iarena.utilizing.randoming.RandomGenerator import RandomGenerator

if TYPE_CHECKING:
    from iarena.gaming.goldmine.GoldMineConfiguration import GoldMineConfiguration
    from iarena.gaming.Movement import Movement
    from iarena.gaming.Position import Position

from iarena.gaming.goldmine.GoldMineMovement import GoldMineMovement
from iarena.gaming.goldmine.GoldMinePosition import GoldMinePosition


class GoldMineRules(Rules):
    """Concrete rules for the GoldMine exploration game."""

    _configuration: GoldMineConfiguration

    def __init__(self, configuration: GoldMineConfiguration) -> None:
        """Build one ruleset from one GoldMine configuration.

        Args:
            configuration: Static setup values for map, hints, and generation.
        """
        self._configuration = configuration
        self._map, self._start, self._target = self._build_map_and_coordinates()
        if configuration.heuristic_map_data is None:
            self._heuristic_map = SquareMap.zeros(self._map.n_rows(), self._map.n_cols())
        else:
            self._heuristic_map = SquareMap(configuration.heuristic_map_data)
        self._map.check(allow_zero=False, skip_coordinate_validation=[self._start])

    def _build_map_and_coordinates(
        self,
    ) -> tuple[SquareMap[float], SquareMapCoordinate, SquareMapCoordinate]:
        """Build the playable map and resolved start/target coordinates."""
        conf = self._configuration
        rng = RandomGenerator(conf.seed)
        start = conf.start if conf.start is not None else SquareMapCoordinate(0, 0)

        target = conf.target
        while target is None or target == start:
            target = SquareMapCoordinate(rng.randint(conf.n_rows), rng.randint(conf.n_cols))

        if conf.map_data is None:
            raw_map = MapFactory.generate(
                name=conf.map_generator,
                n=conf.n_rows,
                m=conf.n_cols,
                start=start,
                target=target,
                rng=rng,
                integer=conf.integer,
                **conf.map_generator_params,
            )
            square_map = SquareMap.from_numpy(raw_map)
        else:
            square_map = SquareMap(conf.map_data)

        square_map[start] = 0.0
        return square_map, start, target

    def _require_position(self, pos: Position) -> GoldMinePosition:
        """Validate and return one GoldMine position."""
        if not isinstance(pos, GoldMinePosition):
            raise TypeError("pos must be an instance of GoldMinePosition.")
        if pos.get_rules() is not self:
            raise ValueError("Position must be associated with this rules instance.")
        return pos

    def _require_movement(self, mov: Movement) -> GoldMineMovement:
        """Validate and return one GoldMine movement."""
        if not isinstance(mov, GoldMineMovement):
            raise TypeError("mov must be an instance of GoldMineMovement.")
        return mov

    def n_players(self) -> int:
        """Return number of players supported by this ruleset."""
        return 1

    def first_position(self) -> Position:
        """Return initial game position."""
        position = GoldMinePosition(
            rules=self,
            current=self._start,
            dug_tiles={self._start.as_tuple()},
        )
        return position

    def next_position(self, pos: Position, mov: Movement) -> Position:
        """Apply one movement and return successor position."""
        gold_pos = self._require_position(pos)
        gold_mov = self._require_movement(mov)
        if self.is_finished(gold_pos):
            raise ValueError("Cannot play movement on a finished game.")

        valid_directions = set(self._get_valid_directions(gold_pos))
        if gold_mov.direction not in valid_directions:
            raise ValueError("Movement direction is not valid from current position.")

        next_coordinate = gold_pos._current.from_direction(gold_mov.direction)
        next_dug_tiles = set(gold_pos._dug_tiles)
        next_dug_tiles.add(next_coordinate.as_tuple())

        next_position = GoldMinePosition(
            rules=self,
            current=next_coordinate,
            dug_tiles=next_dug_tiles,
        )
        return next_position

    def possible_movements(self, pos: Position) -> Iterator[Movement]:
        """Yield legal movements for one position."""
        gold_pos = self._require_position(pos)
        if self.is_finished(gold_pos):
            return
        for direction in self._get_valid_directions(gold_pos):
            yield GoldMineMovement(direction=direction)

    def is_finished(self, pos: Position) -> bool:
        """Return whether target tile has been dug."""
        gold_pos = self._require_position(pos)
        return self._target.as_tuple() in gold_pos._dug_tiles

    def get_score(self, pos: Position) -> ScoreBoard:
        """Return score board where score is negative accumulated cost."""
        gold_pos = self._require_position(pos)
        board = ScoreBoard()
        board._scores = {PlayerIndex(0): Score(-self._get_accumulated_cost(gold_pos))}
        return board

    def _validate_position_state(
        self,
        current: SquareMapCoordinate,
        dug_tiles: set[tuple[int, int]],
    ) -> None:
        """Validate one position payload against this ruleset."""
        if not self._map.in_bounds(current):
            raise ValueError("current coordinate must be inside map bounds.")
        if current.as_tuple() not in dug_tiles:
            raise ValueError("current coordinate must be present in dug_tiles.")
        if self._start.as_tuple() not in dug_tiles:
            raise ValueError("start coordinate must be present in dug_tiles.")
        for coordinate_as_tuple in dug_tiles:
            dug_coordinate = SquareMapCoordinate.from_tuple(coordinate_as_tuple)
            self._map.require_in_bounds(dug_coordinate, name="dug tile")

    def _get_valid_directions(self, pos: GoldMinePosition) -> Iterator[SquareMapDirection]:
        """Yield valid directions from the current coordinate."""
        self._require_position(pos)
        yield from self._map.possible_directions(pos._current)

    def _get_cost_from_direction(self, pos: GoldMinePosition, direction: SquareMapDirection) -> float:
        """Return the movement cost from one position following one direction."""
        self._require_position(pos)
        next_coordinate = pos._current.from_direction(direction)
        self._map.require_in_bounds(next_coordinate, name="next coordinate")
        if next_coordinate.as_tuple() in pos._dug_tiles:
            return 0.0
        return float(self._map[next_coordinate])

    def _get_accumulated_cost(self, pos: GoldMinePosition) -> float:
        """Return cumulative cost of dug tiles.

        Args:
            pos: Position whose dug tiles are accumulated.

        Returns:
            float: Sum of costs over dug tiles.
        """
        self._require_position(pos)
        total = 0.0
        for dug_as_tuple in pos._dug_tiles:
            coordinate = SquareMapCoordinate.from_tuple(dug_as_tuple)
            total += float(self._map[coordinate])
        return total

    def _get_compass_hint(self, pos: GoldMinePosition) -> SquareMapDirection:
        """Return compass hint from current position to target."""
        self._require_position(pos)
        if not self._configuration.compass_activated:
            raise RuntimeError("Compass heuristic is not activated.")
        return self._map.compass_direction(pos._current, self._target, fail_on_same=False)

    def _get_proximity_hint(self, pos: GoldMinePosition) -> int:
        """Return Manhattan-distance hint to target."""
        self._require_position(pos)
        if not self._configuration.proximity_activated:
            raise RuntimeError("Proximity heuristic is not activated.")
        return pos._current.manhattan_distance(self._target)

    def _get_density_hint(self, pos: GoldMinePosition) -> float:
        """Return density-map hint at current coordinate."""
        self._require_position(pos)
        if not self._configuration.density_activated:
            raise RuntimeError("Density heuristic is not activated.")
        return float(self._heuristic_map[pos._current])

    def _generate_plot_position(self, pos: GoldMinePosition) -> Any:
        """Plot one position on the map for debugging."""
        return generate_plot_map(
            square_map=self._map,
            start=pos._current,
            target=self._target,
            empty_tiles=pos._dug_tiles,
            colorbar=True,
            cost=self._get_accumulated_cost(pos),
        )


    def compass_activated(self) -> bool:
        """Return whether compass hint is activated."""
        return self._configuration.compass_activated

    def proximity_activated(self) -> bool:
        """Return whether proximity hint is activated."""
        return self._configuration.proximity_activated

    def density_activated(self) -> bool:
        """Return whether density hint is activated."""
        return self._configuration.density_activated
