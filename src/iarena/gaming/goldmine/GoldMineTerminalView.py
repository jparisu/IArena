"""Declares the terminal visualization contract for the GoldMine game."""

from __future__ import annotations

from typing import TYPE_CHECKING

from iarena.visualizing.terminal_frontend.TerminalView import TerminalView

if TYPE_CHECKING:
    from iarena.gaming.Movement import Movement
    from iarena.gaming.Position import Position
    from iarena.gaming.Rules import Rules

from iarena.gaming.goldmine.GoldMineMovement import GoldMineMovement
from iarena.gaming.goldmine.GoldMinePosition import GoldMinePosition
from iarena.gaming.goldmine.GoldMineRules import GoldMineRules
from iarena.utilizing.mapping.square_map.SquareMapCoordinate import SquareMapCoordinate
from iarena.utilizing.mapping.square_map.SquareMapDirection import SquareMapDirection


class GoldMineTerminalView(TerminalView):
    """Concrete terminal view implementation for the GoldMine game.

    Purpose:
        Provides text-based rendering and input parsing for GoldMine in terminal executions.
    How it works:
        Converts GoldMine domain objects into formatted strings and user commands into movements.
    Used for:
        Command-line gameplay and debugging-oriented textual visualization.
    Public Attributes:
        Inherits terminal I/O callables from `TerminalView`.
    """

    def _format_known_tile(self, position: GoldMinePosition, row: int, col: int) -> str:
        """Return one fixed-width token for the known-state map cell.

        Args:
            position: Current GoldMine position.
            row: Tile row index.
            col: Tile column index.

        Returns:
            str: Terminal token describing current, dug, or unknown tile.
        """
        coordinate_as_tuple = (row, col)
        if position._current.as_tuple() == coordinate_as_tuple:
            return "P"
        if coordinate_as_tuple in position._dug_tiles:
            coordinate = SquareMapCoordinate.from_tuple(coordinate_as_tuple)
            return f"{position.get_rules()._map[coordinate]:.1f}"
        return "?"

    def get_str_info(self, rules: Rules) -> str:
        """Return formatted static information for the current GoldMine match.

        Args:
            rules: Rules instance used to derive user-facing game metadata.

        Returns:
            str: Text block rendered in the terminal information area.
        """
        if not isinstance(rules, GoldMineRules):
            raise TypeError("rules must be an instance of GoldMineRules.")

        conf = rules._configuration
        return (
            "=== GoldMine ===\n"
            f"Map size: {conf.n_rows}x{conf.n_cols}\n"
            "Goal: reach the hidden gold tile minimizing accumulated digging cost.\n"
            "Input format: direction name (`up`, `right`, `down`, `left`) or alias (`u`, `r`, `d`, `l`)."
        )

    def get_str_state(self, position: Position) -> str:
        """Return formatted text representation of the current GoldMine position.

        Args:
            position: Position to transform into a terminal-friendly state string.

        Returns:
            str: Text block describing the known map state and legal movements.
        """
        if not isinstance(position, GoldMinePosition):
            raise TypeError("position must be an instance of GoldMinePosition.")

        rules = position.get_rules()
        if not isinstance(rules, GoldMineRules):
            raise TypeError("Position rules must be an instance of GoldMineRules.")

        current = position._current
        n_rows, n_cols = rules._map.size()
        dug_tiles = len(position._dug_tiles)
        score = float(rules.get_score(position).get_score(position.next_player()))

        header = "    " + " ".join(f"{col:>5}" for col in range(n_cols))
        known_map_lines = [header]
        for row in range(n_rows):
            tokens = [f"{self._format_known_tile(position, row, col):>5}" for col in range(n_cols)]
            known_map_lines.append(f"{row:>3} " + " ".join(tokens))

        possible_movements = list(rules.possible_movements(position))
        movement_lines: list[str] = []
        if not possible_movements:
            movement_lines = ["  No legal movements available."]
        else:
            for movement_index, movement in enumerate(possible_movements):
                if not isinstance(movement, GoldMineMovement):
                    continue
                cost = position.get_cost_from_direction(movement.direction)
                movement_lines.append(f"  [{movement_index}] {movement.direction.name} (cost {cost:.2f})")

        hint_lines: list[str] = []
        if rules._configuration.compass_activated:
            hint_lines.append(f"  - Compass: {position.get_compass().name}")
        if rules._configuration.proximity_activated:
            hint_lines.append(f"  - Proximity: {position.get_proximity()}")
        if rules._configuration.density_activated:
            hint_lines.append(f"  - Density: {position.get_density():.3f}")
        if not hint_lines:
            hint_lines.append("  - No active hints.")

        return "\n".join(
            [
                f"Current coordinate: ({current.x}, {current.y})",
                f"Dug tiles: {dug_tiles}",
                f"Score: {score:.3f}",
                "Known map (`P` current tile, `?` unknown):",
                *known_map_lines,
                "Hints:",
                *hint_lines,
                "Possible movements:",
                *movement_lines,
            ],
        )

    def capture_input(self, input: str) -> Movement:
        """Convert a terminal input line into a GoldMine movement instance.

        Args:
            input: Raw text entered by the terminal user.

        Returns:
            Movement: Parsed movement represented by the input text.
        """
        normalized = input.strip().lower()
        aliases = {
            "u": SquareMapDirection.UP,
            "up": SquareMapDirection.UP,
            "r": SquareMapDirection.RIGHT,
            "right": SquareMapDirection.RIGHT,
            "d": SquareMapDirection.DOWN,
            "down": SquareMapDirection.DOWN,
            "l": SquareMapDirection.LEFT,
            "left": SquareMapDirection.LEFT,
        }
        direction = aliases.get(normalized)
        if direction is None:
            raise ValueError("Expected one direction: up/right/down/left (or u/r/d/l).")
        return GoldMineMovement(direction=direction)
