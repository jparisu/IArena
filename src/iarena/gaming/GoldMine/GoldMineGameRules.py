# pylint: disable=too-many-lines
"""Rule engine for the GoldMine game."""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from typing import Any

from iarena.gaming.GoldMine.GoldMine import CostType, GoldMineCoordinate, GoldMineDirection, GoldMineSquareMap
from iarena.gaming.GoldMine.GoldMineHintMode import GoldMineHintMode
from iarena.gaming.GoldMine.GoldMineMovement import GoldMineMovement
from iarena.gaming.GoldMine.GoldMinePosition import GoldMinePosition
from iarena.interfacing.IGameRules import IGameRules
from iarena.interfacing.IMovement import IMovement
from iarena.interfacing.IPosition import IPosition
from iarena.interfacing.ScoreBoard import ScoreBoard
from iarena.utilizing.protocoling import ITextRenderable
from iarena.utilizing.square_map.draw_square_map import plot_square_map


class GoldMineGameRules(IGameRules, ITextRenderable):
    """Implement state transitions and scoring for GoldMine."""

    def __init__(
        self,
        cost_map: GoldMineSquareMap,
        target: GoldMineCoordinate,
        start: GoldMineCoordinate | None = None,
        hint_mode: GoldMineHintMode = GoldMineHintMode.NONE,
        heuristic_map: GoldMineSquareMap | None = None,
    ) -> None:
        """Initialize and validate GoldMine configuration.

        Args:
            cost_map: Digging-cost map.
            target: Gold coordinate.
            start: Optional starting coordinate.
            hint_mode: Enabled hint mode.
            heuristic_map: Optional density map.

        Returns:
            None.
        """
        self._cost_map = cost_map.copy()
        self._target = target
        self._start = start if start is not None else GoldMineCoordinate(0, 0)
        self._hint_mode = hint_mode
        if heuristic_map is None:
            rows, cols = self._cost_map.size()
            self._heuristic_map = GoldMineSquareMap.zeros(rows, cols)
        else:
            self._heuristic_map = heuristic_map.copy()

        self._cost_map.require_in_bounds(self._start, name="start")
        self._cost_map.require_in_bounds(self._target, name="target")
        self._cost_map.check(allow_zero=False, skip_coordinate_validation=[self._start])
        if self._heuristic_map.size() != self._cost_map.size():
            raise ValueError("heuristic_map must have the same shape as cost_map")

    def _as_position(self, position: IPosition) -> GoldMinePosition:
        """Validate and cast a generic position.

        Args:
            position: Position to validate.

        Returns:
            Same position typed as ``GoldMinePosition``.
        """
        if not isinstance(position, GoldMinePosition):
            raise TypeError(f"position must be GoldMinePosition, got {type(position).__name__}")
        return position

    def n_players(self) -> int:
        """Return number of players.

        Args:
            None.

        Returns:
            Always ``1``.
        """
        return 1

    def first_position(self) -> GoldMinePosition:
        """Create the initial position.

        Args:
            None.

        Returns:
            Initial GoldMine position.
        """
        return GoldMinePosition(rules=self, current_position=self._start, dug_tiles=frozenset({self._start}))

    def next_position(self, movement: IMovement, position: IPosition) -> GoldMinePosition:
        """Apply one movement and return the successor position.

        Args:
            movement: Player-selected movement.
            position: Current game position.

        Returns:
            Successor position.
        """
        if not isinstance(movement, GoldMineMovement):
            raise TypeError(f"movement must be GoldMineMovement, got {type(movement).__name__}")
        state = self._as_position(position)
        destination = state.current_position.moved(movement.direction)
        if not self._cost_map.in_bounds(destination):
            raise ValueError(f"movement {movement.direction.name} leaves map bounds")
        dug_tiles = set(state.dug_tiles)
        dug_tiles.add(destination)
        return GoldMinePosition(rules=self, current_position=destination, dug_tiles=frozenset(dug_tiles))

    def possible_movements(self, position: IPosition) -> Iterator[GoldMineMovement]:
        """Yield legal movements for a position.

        Args:
            position: Current game position.

        Returns:
            Iterator with legal movements.
        """
        state = self._as_position(position)
        for direction in self.valid_directions(state.current_position):
            yield GoldMineMovement(direction=direction)

    def finished(self, position: IPosition) -> bool:
        """Return whether the target has been dug.

        Args:
            position: Position to evaluate.

        Returns:
            ``True`` when the game is terminal.
        """
        state = self._as_position(position)
        return self._target in state.dug_tiles

    def score(self, position: IPosition) -> ScoreBoard:
        """Compute score board for a position.

        Args:
            position: Position to score.

        Returns:
            Scoreboard with negative accumulated cost.
        """
        state = self._as_position(position)
        board = ScoreBoard(self.n_players())
        board.define_score(0, -state.accumulated_cost())
        return board

    def hint_mode(self) -> GoldMineHintMode:
        """Return active hint mode.

        Args:
            None.

        Returns:
            Active hint mode.
        """
        return self._hint_mode

    def is_hint_enabled(self, mode: GoldMineHintMode) -> bool:
        """Check if a hint mode is active.

        Args:
            mode: Mode to evaluate.

        Returns:
            ``True`` when ``mode`` is active.
        """
        return self._hint_mode is mode

    def valid_directions(self, coordinate: GoldMineCoordinate) -> tuple[GoldMineDirection, ...]:
        """Return legal directions from one coordinate.

        Args:
            coordinate: Origin coordinate.

        Returns:
            Tuple with in-bounds directions.
        """
        return tuple(self._cost_map.possible_directions(coordinate))

    def cost_at(self, coordinate: GoldMineCoordinate) -> CostType:
        """Return digging cost at coordinate.

        Args:
            coordinate: Coordinate to evaluate.

        Returns:
            Digging cost.
        """
        self._cost_map.require_in_bounds(coordinate, name="coordinate")
        return float(self._cost_map[coordinate])

    def accumulated_cost(self, dug_tiles: Iterable[GoldMineCoordinate]) -> CostType:
        """Compute total cost over dug coordinates.

        Args:
            dug_tiles: Dug coordinates.

        Returns:
            Sum of costs.
        """
        return float(sum(self.cost_at(coordinate) for coordinate in dug_tiles))

    def compass_hint(self, coordinate: GoldMineCoordinate) -> GoldMineDirection:
        """Return compass hint toward target.

        Args:
            coordinate: Current coordinate.

        Returns:
            Dominant direction toward target.
        """
        if not self.is_hint_enabled(GoldMineHintMode.COMPASS):
            raise RuntimeError("compass hint mode is not enabled")
        return self._cost_map.compass_direction(coordinate, self._target)

    def proximity_hint(self, coordinate: GoldMineCoordinate) -> int:
        """Return Manhattan distance hint.

        Args:
            coordinate: Current coordinate.

        Returns:
            Manhattan distance to target.
        """
        if not self.is_hint_enabled(GoldMineHintMode.PROXIMITY):
            raise RuntimeError("proximity hint mode is not enabled")
        return coordinate.manhattan_distance(self._target)

    def density_hint(self, coordinate: GoldMineCoordinate) -> CostType:
        """Return density-map hint value.

        Args:
            coordinate: Current coordinate.

        Returns:
            Density heuristic value.
        """
        if not self.is_hint_enabled(GoldMineHintMode.DENSITY):
            raise RuntimeError("density hint mode is not enabled")
        self._heuristic_map.require_in_bounds(coordinate, name="coordinate")
        return float(self._heuristic_map[coordinate])

    def plot_step(self, axis: Any, position: GoldMinePosition, **kwargs: Any) -> Any:
        """Plot one game state.

        Args:
            axis: Plot backend target.
            position: Position to render.
            **kwargs: Extra plot options.

        Returns:
            Backend object returned by ``plot_square_map``.
        """
        return plot_square_map(
            axis=axis,
            square_map=self._cost_map,
            start=self._start,
            target=self._target,
            cost=position.accumulated_cost(),
            empty_tiles=set(position.dug_tiles),
            **kwargs,
        )

    def to_text(self) -> str:
        """Render rules configuration as terminal-friendly text.

        Args:
            None.

        Returns:
            Multi-line summary of GoldMine rules configuration.
        """
        rows, cols = self._cost_map.size()
        return "\n".join(
            [
                "GoldMine Rules:",
                f"  - map size: {rows} x {cols}",
                f"  - start: ({self._start.x}, {self._start.y})",
                f"  - target: ({self._target.x}, {self._target.y})",
                f"  - hint mode: {self._hint_mode.value}",
            ]
        )

    def __str__(self) -> str:
        """Render rules using the text-rendering protocol.

        Args:
            None.

        Returns:
            Same value as :meth:`to_text`.
        """
        return self.to_text()
