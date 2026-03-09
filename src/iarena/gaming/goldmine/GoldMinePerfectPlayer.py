"""Declares a heuristic-guided high-quality player for the GoldMine game."""

from __future__ import annotations

from collections.abc import Iterable
from typing import TYPE_CHECKING

from iarena.playing.Player import Player
from iarena.utilizing.mapping.square_map.SquareMapCoordinate import SquareMapCoordinate
from iarena.utilizing.mapping.square_map.SquareMapDirection import SquareMapDirection
from iarena.utilizing.randoming.RandomGenerator import RandomGenerator

if TYPE_CHECKING:
    from iarena.gaming.Movement import Movement
    from iarena.gaming.Position import Position
    from iarena.gaming.Rules import Rules
    from iarena.playing.PlayerIndex import PlayerIndex

from iarena.gaming.goldmine.GoldMineMovement import GoldMineMovement
from iarena.gaming.goldmine.GoldMinePosition import GoldMinePosition
from iarena.gaming.goldmine.GoldMineRules import GoldMineRules


class GoldMinePerfectPlayer(Player):
    """High-quality stochastic player for GoldMine under hidden information.

    Purpose:
        Maintain a progressively discovered local map and combine known tile costs
        with heuristic readings to choose strong movements under uncertainty.
    How it works:
        Keeps relative coordinates anchored at the start tile, records compass and
        proximity observations per visited tile, estimates target candidates, and
        samples the next movement proportionally to a utility score.
    Used for:
        GoldMine benchmark play and oracle simulations.
    Public Attributes:
        None declared at class level in this class body.
    """

    _rules: GoldMineRules
    _player_index: PlayerIndex
    _rng: RandomGenerator
    _current_coordinate: SquareMapCoordinate
    _pending_direction: SquareMapDirection | None
    _visited_tiles: set[tuple[int, int]]
    _known_tile_costs: dict[tuple[int, int], float]
    _compass_readings: dict[tuple[int, int], SquareMapDirection]
    _proximity_readings: dict[tuple[int, int], int]
    _density_readings: dict[tuple[int, int], float]
    _candidate_coordinates: list[SquareMapCoordinate]
    _estimated_target: SquareMapCoordinate | None
    _cost_weight: float
    _heuristic_weight: float
    _exploration_bonus: float

    def __init__(
        self,
        seed: int | None = 0,
        cost_weight: float = 0.6,
        heuristic_weight: float = 0.4,
        exploration_bonus: float = 0.15,
    ) -> None:
        """Create one GoldMine perfect-player instance.

        Args:
            seed: Random seed used for weighted stochastic decisions.
            cost_weight: Relative importance of low movement costs.
            heuristic_weight: Relative importance of heuristic guidance.
            exploration_bonus: Bonus assigned to moving toward unvisited tiles.
        """
        if cost_weight < 0.0 or heuristic_weight < 0.0:
            raise ValueError("cost_weight and heuristic_weight must be non-negative.")
        if cost_weight + heuristic_weight <= 0.0:
            raise ValueError("At least one of cost_weight or heuristic_weight must be strictly positive.")
        if exploration_bonus < 0.0:
            raise ValueError("exploration_bonus must be non-negative.")

        self._rng = RandomGenerator(seed=seed)
        self._cost_weight = float(cost_weight)
        self._heuristic_weight = float(heuristic_weight)
        self._exploration_bonus = float(exploration_bonus)
        self._reset_tracking_state()

    def _reset_tracking_state(self) -> None:
        """Reset all runtime exploration and heuristic tracking containers."""
        self._current_coordinate = SquareMapCoordinate(0, 0)
        self._pending_direction = None
        self._visited_tiles = {(0, 0)}
        self._known_tile_costs = {(0, 0): 0.0}
        self._compass_readings = {}
        self._proximity_readings = {}
        self._density_readings = {}
        self._candidate_coordinates = [SquareMapCoordinate(0, 0)]
        self._estimated_target = None

    def name(self) -> str:
        """Return the canonical player name for displays and registries.

        Returns:
            str: Stable identifier for this strategy.
        """
        return "goldmine-perfect"

    def _iter_candidate_coordinates(self) -> Iterable[SquareMapCoordinate]:
        """Yield all relative coordinates considered as target candidates."""
        yield from self._candidate_coordinates

    def _apply_pending_direction(self) -> None:
        """Advance internal current coordinate using the last committed movement."""
        if self._pending_direction is None:
            return
        self._current_coordinate = self._current_coordinate.from_direction(self._pending_direction)
        self._visited_tiles.add(self._current_coordinate.as_tuple())
        self._known_tile_costs.setdefault(self._current_coordinate.as_tuple(), 0.0)
        self._pending_direction = None

    def _record_known_map_state(self, pos: GoldMinePosition) -> None:
        """Store known movement costs around the current tile."""
        for direction in pos.get_valid_directions():
            neighbor = self._current_coordinate.from_direction(direction)
            neighbor_key = neighbor.as_tuple()
            movement_cost = float(pos.get_cost_from_direction(direction))
            if movement_cost > 0.0:
                self._known_tile_costs[neighbor_key] = movement_cost
            else:
                self._known_tile_costs.setdefault(neighbor_key, 0.0)
                self._visited_tiles.add(neighbor_key)

    def _record_compass_reading(self, pos: GoldMinePosition) -> None:
        """Store compass reading at current tile when available."""
        try:
            compass_value = pos.get_compass()
        except RuntimeError:
            return
        self._compass_readings[self._current_coordinate.as_tuple()] = compass_value

    def _record_proximity_reading(self, pos: GoldMinePosition) -> None:
        """Store proximity reading at current tile when available."""
        try:
            proximity_value = int(pos.get_proximity())
        except RuntimeError:
            return
        self._proximity_readings[self._current_coordinate.as_tuple()] = proximity_value

    def _record_density_reading(self, pos: GoldMinePosition) -> None:
        """Store density reading at current tile when available."""
        try:
            density_value = float(pos.get_density())
        except RuntimeError:
            return
        self._density_readings[self._current_coordinate.as_tuple()] = density_value

    def _expected_compass_direction(
        self,
        from_coordinate: SquareMapCoordinate,
        to_coordinate: SquareMapCoordinate,
    ) -> SquareMapDirection:
        """Return expected compass direction between two relative coordinates."""
        dx = to_coordinate.x - from_coordinate.x
        dy = to_coordinate.y - from_coordinate.y
        if abs(dx) >= abs(dy):
            return SquareMapDirection.DOWN if dx > 0 else SquareMapDirection.UP
        return SquareMapDirection.RIGHT if dy > 0 else SquareMapDirection.LEFT

    def _is_consistent_with_compass(self, candidate_target: SquareMapCoordinate) -> bool:
        """Return whether a candidate target matches all stored compass readings."""
        for coord_key, observed_direction in self._compass_readings.items():
            source_coordinate = SquareMapCoordinate.from_tuple(coord_key)
            expected_direction = self._expected_compass_direction(source_coordinate, candidate_target)
            if expected_direction != observed_direction:
                return False
        return True

    def _target_candidates_from_compass(self) -> set[tuple[int, int]]:
        """Compute candidate target coordinates constrained by compass readings."""
        if not self._compass_readings:
            return set()
        return {
            coordinate.as_tuple()
            for coordinate in self._iter_candidate_coordinates()
            if self._is_consistent_with_compass(coordinate)
        }

    def _target_candidates_from_proximity(self) -> set[tuple[int, int]]:
        """Compute candidate target coordinates constrained by proximity readings."""
        if not self._proximity_readings:
            return set()

        candidates = {coordinate.as_tuple() for coordinate in self._iter_candidate_coordinates()}
        for coord_key, distance in self._proximity_readings.items():
            source_coordinate = SquareMapCoordinate.from_tuple(coord_key)
            candidates = {
                candidate
                for candidate in candidates
                if SquareMapCoordinate.from_tuple(candidate).manhattan_distance(source_coordinate) == distance
            }
            if not candidates:
                break
        return candidates

    def _estimate_target_from_proximity(self) -> SquareMapCoordinate | None:
        """Estimate one exact target location from proximity readings."""
        if len(self._proximity_readings) < 2:
            return None

        candidates = self._target_candidates_from_proximity()
        if not candidates:
            return None

        if len(candidates) > 1 and self._compass_readings:
            candidates = {candidate for candidate in candidates if self._is_consistent_with_compass(SquareMapCoordinate.from_tuple(candidate))}
            if not candidates:
                return None

        if len(candidates) == 1:
            return SquareMapCoordinate.from_tuple(next(iter(candidates)))

        # When multiple candidates remain, choose the closest one to keep an actionable target.
        return min(
            (SquareMapCoordinate.from_tuple(candidate) for candidate in candidates),
            key=lambda coordinate: coordinate.manhattan_distance(self._current_coordinate),
        )

    def _estimate_distance_from_compass(self, tile: SquareMapCoordinate) -> float | None:
        """Estimate tile-to-target distance using only compass constraints."""
        compass_candidates = self._target_candidates_from_compass()
        if not compass_candidates:
            return None
        distances = [tile.manhattan_distance(SquareMapCoordinate.from_tuple(candidate)) for candidate in compass_candidates]
        return float(sum(distances) / len(distances))

    def _estimate_distance_from_proximity(self, tile: SquareMapCoordinate) -> float | None:
        """Estimate tile-to-target distance using proximity-derived target estimation."""
        if self._estimated_target is not None:
            return float(tile.manhattan_distance(self._estimated_target))

        proximity_candidates = self._target_candidates_from_proximity()
        if not proximity_candidates:
            return None
        distances = [tile.manhattan_distance(SquareMapCoordinate.from_tuple(candidate)) for candidate in proximity_candidates]
        return float(sum(distances) / len(distances))

    def _estimate_tile_heuristic_distance(self, tile: SquareMapCoordinate) -> float | None:
        """Estimate distance-to-target for one tile combining available heuristics."""
        proximity_distance = self._estimate_distance_from_proximity(tile)
        compass_distance = self._estimate_distance_from_compass(tile)
        available_distances = [distance for distance in (proximity_distance, compass_distance) if distance is not None]
        if not available_distances:
            return None
        return float(sum(available_distances) / len(available_distances))

    def _directional_compass_bonus(self, direction: SquareMapDirection) -> float:
        """Return bonus for movement aligned with current-tile compass reading."""
        current_compass = self._compass_readings.get(self._current_coordinate.as_tuple())
        if current_compass is None:
            return 0.0
        return 0.1 if direction == current_compass else 0.0

    def _movement_utility(self, direction: SquareMapDirection, movement_cost: float) -> float:
        """Return utility score for moving in one direction."""
        candidate_tile = self._current_coordinate.from_direction(direction)
        heuristic_distance = self._estimate_tile_heuristic_distance(candidate_tile)

        cost_component = 1.0 / (1.0 + max(0.0, movement_cost))
        if heuristic_distance is None:
            heuristic_component = 0.5
        else:
            heuristic_component = 1.0 / (1.0 + max(0.0, heuristic_distance))

        exploration_component = self._exploration_bonus if candidate_tile.as_tuple() not in self._visited_tiles else 0.0
        compass_bonus = self._directional_compass_bonus(direction)
        utility = (
            self._cost_weight * cost_component
            + self._heuristic_weight * heuristic_component
            + exploration_component
            + compass_bonus
        )
        return max(1e-9, utility)

    def _weighted_direction_choice(self, weighted_directions: list[tuple[SquareMapDirection, float]]) -> SquareMapDirection:
        """Sample one direction proportionally to provided positive weights."""
        total_weight = sum(weight for _, weight in weighted_directions)
        threshold = self._rng.rand() * total_weight
        cumulative_weight = 0.0
        for direction, weight in weighted_directions:
            cumulative_weight += weight
            if cumulative_weight >= threshold:
                return direction
        return weighted_directions[-1][0]

    def _choose_next_direction(self, pos: GoldMinePosition) -> SquareMapDirection:
        """Choose one legal movement direction from the current position."""
        legal_directions = list(pos.get_valid_directions())
        if not legal_directions:
            raise ValueError("No legal movement is available from the current position.")

        weighted_directions = [
            (direction, self._movement_utility(direction, float(pos.get_cost_from_direction(direction))))
            for direction in legal_directions
        ]
        return self._weighted_direction_choice(weighted_directions)

    def _update_from_position(self, pos: GoldMinePosition) -> None:
        """Update all internal observations from the current position."""
        self._record_known_map_state(pos)
        self._record_compass_reading(pos)
        self._record_proximity_reading(pos)
        self._record_density_reading(pos)
        estimated_target = self._estimate_target_from_proximity()
        if estimated_target is not None:
            self._estimated_target = estimated_target

    def play(self, pos: Position) -> Movement:
        """Choose and return the next GoldMine movement.

        Args:
            pos: Current position where the player must act.

        Returns:
            Movement: Movement selected from legal directions.
        """
        if not isinstance(pos, GoldMinePosition):
            raise TypeError("pos must be an instance of GoldMinePosition.")
        if pos.get_rules() is not self._rules:
            raise ValueError("pos must be associated with the same rules seen in starting_game.")
        if self._rules.is_finished(pos):
            raise ValueError("No movement available: the game is already solved.")

        self._apply_pending_direction()
        self._update_from_position(pos)
        selected_direction = self._choose_next_direction(pos)
        self._pending_direction = selected_direction
        return GoldMineMovement(direction=selected_direction)

    def starting_game(self, rules: Rules, player_index: PlayerIndex) -> None:
        """Initialize runtime context before one GoldMine game starts.

        Args:
            rules: Rules object associated with the game.
            player_index: Index assigned to this player.
        """
        if not isinstance(rules, GoldMineRules):
            raise TypeError("rules must be an instance of GoldMineRules.")
        if int(player_index) != 0:
            raise ValueError("GoldMinePerfectPlayer supports only player index 0.")

        self._rules = rules
        self._player_index = player_index
        self._rng.set_seed(rules.configuration.seed if rules.configuration.seed is not None else 0)
        self._reset_tracking_state()

        max_dx = rules.configuration.n_rows - 1
        max_dy = rules.configuration.n_cols - 1
        self._candidate_coordinates = [
            SquareMapCoordinate(x, y)
            for x in range(-max_dx, max_dx + 1)
            for y in range(-max_dy, max_dy + 1)
        ]
