# pylint: disable=too-many-lines
"""Rule engine for the GoldMine game."""

from __future__ import annotations

from collections.abc import Iterable, Iterator, Sequence
from typing import Any

from iarena.desining.gaming.GameConfiguration import GameConfiguration
from iarena.desining.gaming.GameRules import GameRules
from iarena.desining.gaming.Movement import Movement
from iarena.desining.gaming.Position import Position
from iarena.desining.gaming.ScoreBoard import ScoreBoard
from iarena.desining.visualing import StreamlitGame, TerminalGame
from iarena.gaming.GoldMine.GoldMine import CostType, GoldMineCoordinate, GoldMineDirection, GoldMineSquareMap
from iarena.gaming.GoldMine.GoldMineHintMode import GoldMineHintMode
from iarena.gaming.GoldMine.GoldMineMovement import GoldMineMovement
from iarena.gaming.GoldMine.GoldMinePosition import GoldMinePosition
from iarena.utilizing.protocoling import ITextRenderable
from iarena.utilizing.square_map.draw_square_map import plot_square_map


class GoldMineGameRules(GameRules, ITextRenderable, TerminalGame, StreamlitGame):
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

    def _as_position(self, position: Position) -> GoldMinePosition:
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

    def next_position(self, movement: Movement, position: Position) -> GoldMinePosition:
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

    def possible_movements(self, position: Position) -> Iterator[GoldMineMovement]:
        """Yield legal movements for a position.

        Args:
            position: Current game position.

        Returns:
            Iterator with legal movements.
        """
        state = self._as_position(position)
        for direction in self.valid_directions(state.current_position):
            yield GoldMineMovement(direction=direction)

    def finished(self, position: Position) -> bool:
        """Return whether the target has been dug.

        Args:
            position: Position to evaluate.

        Returns:
            ``True`` when the game is terminal.
        """
        state = self._as_position(position)
        return self._target in state.dug_tiles

    def score(self, position: Position) -> ScoreBoard:
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

    def terminal_instructions(self) -> str | None:
        """Return terminal instructions for GoldMine games.

        Args:
            None.

        Returns:
            Multi-line textual description of game rules.
        """
        return self.to_text()

    def position_to_terminal(self, position: Position) -> str:
        """Convert one position into terminal-friendly text.

        Args:
            position: Position to convert.

        Returns:
            Multi-line text rendering for the provided position.
        """
        return self._as_position(position).to_text()

    def movement_from_terminal(self, raw_movement: str, possible_movements: Sequence[Movement]) -> Movement:
        """Parse a terminal input into a movement.

        GoldMine accepts either:
        - direction names (for example ``UP`` or ``Left``),
        - or a numeric index handled by the default terminal behavior.

        Args:
            raw_movement: Raw user input string.
            possible_movements: Legal movements for the current position.

        Returns:
            Selected movement.
        """
        normalized = raw_movement.strip().upper()
        for movement in possible_movements:
            if isinstance(movement, GoldMineMovement) and movement.direction.name == normalized:
                return movement
        return TerminalGame.movement_from_terminal(self, raw_movement, possible_movements)

    def movement_to_terminal(self, movement: Movement) -> str:
        """Convert one movement into terminal-friendly text.

        Args:
            movement: Movement to convert.

        Returns:
            String representation of ``movement``.
        """
        if isinstance(movement, GoldMineMovement):
            return movement.to_text()
        return str(movement)

    def streamlit_instructions(self, streamlit_container: Any) -> None:
        """Render game instructions in a Streamlit container.

        Args:
            streamlit_container: Streamlit container used to render content.

        Returns:
            None.
        """
        instructions = self.terminal_instructions() or ""
        if hasattr(streamlit_container, "markdown"):
            streamlit_container.markdown(f"```\\n{instructions}\\n```")
            return
        if hasattr(streamlit_container, "write"):
            streamlit_container.write(instructions)

    def render_streamlit_position(self, position: Position, streamlit_container: Any) -> None:
        """Render one position in a Streamlit container.

        Args:
            position: Position to render.
            streamlit_container: Streamlit container used to render content.

        Returns:
            None.
        """
        position_text = self.position_to_terminal(position)
        if hasattr(streamlit_container, "text"):
            streamlit_container.text(position_text)
            return
        if hasattr(streamlit_container, "markdown"):
            streamlit_container.markdown(f"```\\n{position_text}\\n```")
            return
        if hasattr(streamlit_container, "write"):
            streamlit_container.write(position_text)

    def render_streamlit_configuration(self, streamlit_container: Any) -> GameConfiguration:
        """Render Streamlit controls and return selected configuration values.

        Args:
            streamlit_container: Streamlit container used to render controls.

        Returns:
            Selected configuration object.
        """
        rows, cols = self._cost_map.size()
        configuration_values: dict[str, Any] = {
            "map": self._cost_map.copy(),
            "start": (self._start.x, self._start.y),
            "target": (self._target.x, self._target.y),
            "hint_mode": self._hint_mode.value,
        }
        if self._heuristic_map is not None:
            configuration_values["heuristic_map"] = self._heuristic_map.copy()

        if hasattr(streamlit_container, "number_input") and hasattr(streamlit_container, "selectbox"):
            start_x = int(
                streamlit_container.number_input(
                    "Start row",
                    min_value=0,
                    max_value=rows - 1,
                    value=int(self._start.x),
                    step=1,
                )
            )
            start_y = int(
                streamlit_container.number_input(
                    "Start column",
                    min_value=0,
                    max_value=cols - 1,
                    value=int(self._start.y),
                    step=1,
                )
            )
            target_x = int(
                streamlit_container.number_input(
                    "Target row",
                    min_value=0,
                    max_value=rows - 1,
                    value=int(self._target.x),
                    step=1,
                )
            )
            target_y = int(
                streamlit_container.number_input(
                    "Target column",
                    min_value=0,
                    max_value=cols - 1,
                    value=int(self._target.y),
                    step=1,
                )
            )
            hint_mode = streamlit_container.selectbox(
                "Hint mode",
                options=[mode.value for mode in GoldMineHintMode],
                index=[mode.value for mode in GoldMineHintMode].index(self._hint_mode.value),
            )
            configuration_values["start"] = (start_x, start_y)
            configuration_values["target"] = (target_x, target_y)
            configuration_values["hint_mode"] = str(hint_mode)
        elif hasattr(streamlit_container, "write"):
            streamlit_container.write("Interactive controls are unavailable. Using current game configuration.")

        return GameConfiguration.from_dict(configuration_values)

    def select_streamlit_movement(self, position: Position, streamlit_container: Any) -> Movement:
        """Render movement controls in Streamlit and return selected movement.

        Args:
            position: Current position.
            streamlit_container: Streamlit container used to render controls.

        Returns:
            Selected movement.
        """
        possible_movements = tuple(self.possible_movements(position))
        if not possible_movements:
            raise RuntimeError("no legal movement available for Streamlit selection")

        if hasattr(streamlit_container, "selectbox"):
            labels = [self.movement_to_terminal(movement) for movement in possible_movements]
            selected_label = streamlit_container.selectbox("Select movement", options=labels)
            selected_index = labels.index(str(selected_label))
            return possible_movements[selected_index]

        if hasattr(streamlit_container, "write"):
            streamlit_container.write(
                "Interactive movement controls are unavailable. Falling back to the first legal movement."
            )
        return possible_movements[0]
