"""GoldMine rules implementation."""

from __future__ import annotations

from collections.abc import Iterator
from typing import TYPE_CHECKING

from iarena.gaming.Rules import Rules
from iarena.playing.PlayerIndex import PlayerIndex
from iarena.scoring.Score import Score
from iarena.scoring.ScoreBoard import ScoreBoard
from iarena.utilizing.mapping.square_map.generators.MapFactory import MapFactory
from iarena.utilizing.mapping.square_map.SquareMap import SquareMap
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

    configuration: GoldMineConfiguration

    def __init__(self, configuration: GoldMineConfiguration) -> None:
        """Build one ruleset from one GoldMine configuration.

        Args:
            configuration: Static setup values for map, hints, and generation.
        """
        self.configuration = configuration
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
        conf = self.configuration
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
        if pos.map_data.size() != self._map.size():
            raise ValueError("Position map dimensions must match rule map dimensions.")
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
            map_data=self._map.copy(),
            start=self._start,
            target=self._target,
            current=self._start,
            dug_tiles={self._start.as_tuple()},
            compass_activated=self.configuration.compass_activated,
            proximity_activated=self.configuration.proximity_activated,
            density_activated=self.configuration.density_activated,
            heuristic_map=self._heuristic_map.copy(),
        )
        position._rules = self
        return position

    def next_position(self, pos: Position, mov: Movement) -> Position:
        """Apply one movement and return successor position."""
        gold_pos = self._require_position(pos)
        gold_mov = self._require_movement(mov)
        if self.is_finished(gold_pos):
            raise ValueError("Cannot play movement on a finished game.")

        valid_directions = set(gold_pos.get_valid_directions())
        if gold_mov.direction not in valid_directions:
            raise ValueError("Movement direction is not valid from current position.")

        next_coordinate = gold_pos.current.from_direction(gold_mov.direction)
        next_dug_tiles = set(gold_pos.dug_tiles)
        next_dug_tiles.add(next_coordinate.as_tuple())

        next_position = GoldMinePosition(
            map_data=gold_pos.map_data.copy(),
            start=gold_pos.start,
            target=gold_pos.target,
            current=next_coordinate,
            dug_tiles=next_dug_tiles,
            compass_activated=gold_pos.compass_activated,
            proximity_activated=gold_pos.proximity_activated,
            density_activated=gold_pos.density_activated,
            heuristic_map=gold_pos.heuristic_map.copy(),
        )
        next_position._rules = self
        return next_position

    def possible_movements(self, pos: Position) -> Iterator[Movement]:
        """Yield legal movements for one position."""
        gold_pos = self._require_position(pos)
        if self.is_finished(gold_pos):
            return
        for direction in gold_pos.get_valid_directions():
            yield GoldMineMovement(direction=direction)

    def is_finished(self, pos: Position) -> bool:
        """Return whether target tile has been dug."""
        gold_pos = self._require_position(pos)
        return gold_pos.target.as_tuple() in gold_pos.dug_tiles

    def get_score(self, pos: Position) -> ScoreBoard:
        """Return score board where score is negative accumulated cost."""
        gold_pos = self._require_position(pos)
        board = ScoreBoard()
        board._scores = {PlayerIndex(0): Score(-self.get_accumulated_cost(gold_pos))}
        return board

    def get_accumulated_cost(self, pos: GoldMinePosition) -> float:
        """Return cumulative cost of dug tiles.

        Args:
            pos: Position whose dug tiles are accumulated.

        Returns:
            float: Sum of costs over dug tiles.
        """
        total = 0.0
        for dug_as_tuple in pos.dug_tiles:
            coordinate = SquareMapCoordinate.from_tuple(dug_as_tuple)
            total += float(pos.map_data[coordinate])
        return total

    def get_compass_hint(self, pos: GoldMinePosition) -> SquareMapDirection:
        """Return compass hint from current position to target."""
        if not self.configuration.compass_activated:
            raise RuntimeError("Compass heuristic is not activated.")
        return pos.map_data.compass_direction(pos.current, pos.target)

    def get_proximity_hint(self, pos: GoldMinePosition) -> int:
        """Return Manhattan-distance hint to target."""
        if not self.configuration.proximity_activated:
            raise RuntimeError("Proximity heuristic is not activated.")
        return pos.current.manhattan_distance(pos.target)

    def get_density_hint(self, pos: GoldMinePosition) -> float:
        """Return density-map hint at current coordinate."""
        if not self.configuration.density_activated:
            raise RuntimeError("Density heuristic is not activated.")
        return float(pos.heuristic_map[pos.current])
