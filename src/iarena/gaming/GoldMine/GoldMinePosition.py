"""Position model for the GoldMine game."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from iarena.desining.gaming.Position import Position
from iarena.desining.playing.Player import PlayerIndex
from iarena.gaming.GoldMine.GoldMine import CostType, GoldMineCoordinate, GoldMineDirection
from iarena.gaming.GoldMine.GoldMineHintMode import GoldMineHintMode
from iarena.utilizing.protocoling import IPlotRenderable, ITextRenderable

if TYPE_CHECKING:
    from iarena.gaming.GoldMine.GoldMineGameRules import GoldMineGameRules


@dataclass(frozen=True, slots=True)
class GoldMinePosition(Position, ITextRenderable, IPlotRenderable):
    """Store one full GoldMine state."""

    rules: GoldMineGameRules = field(compare=False, repr=False)
    current_position: GoldMineCoordinate
    dug_tiles: frozenset[GoldMineCoordinate]

    def next_player(self) -> PlayerIndex:
        """Return the active player index for this turn.

        Args:
            None.

        Returns:
            Always ``0`` because GoldMine is single-player.
        """
        return 0

    def accumulated_cost(self) -> CostType:
        """Compute the cumulative digging cost for this position.

        Args:
            None.

        Returns:
            Sum of all dug-tile costs.
        """
        return self.rules.accumulated_cost(self.dug_tiles)

    def movement_cost(self, direction: GoldMineDirection) -> CostType:
        """Return the immediate cost of taking a direction.

        Args:
            direction: Direction to evaluate from the current position.

        Returns:
            ``0.0`` for already-dug tiles, otherwise map digging cost.
        """
        destination = self.current_position.moved(direction)
        if destination in self.dug_tiles:
            return 0.0
        return self.rules.cost_at(destination)

    def directions_with_cost(self) -> tuple[tuple[GoldMineDirection, CostType], ...]:
        """Return legal directions paired with immediate movement costs.

        Args:
            None.

        Returns:
            Tuple of ``(direction, cost)`` entries for legal movements.
        """
        return tuple(
            (direction, self.movement_cost(direction))
            for direction in self.rules.valid_directions(self.current_position)
        )

    def compass_hint(self) -> GoldMineDirection:
        """Return the compass hint for the current coordinate.

        Args:
            None.

        Returns:
            Dominant direction pointing toward the target.
        """
        return self.rules.compass_hint(self.current_position)

    def proximity_hint(self) -> int:
        """Return the Manhattan distance hint for the current coordinate.

        Args:
            None.

        Returns:
            Manhattan distance to the target coordinate.
        """
        return self.rules.proximity_hint(self.current_position)

    def density_hint(self) -> CostType:
        """Return the density hint for the current coordinate.

        Args:
            None.

        Returns:
            Heuristic density score for the current coordinate.
        """
        return self.rules.density_hint(self.current_position)

    def to_text(self) -> str:
        """Render this position as terminal-friendly text.

        Args:
            None.

        Returns:
            Multi-line textual description with legal movements and hints.
        """
        lines: list[str] = [
            f"Position: ({self.current_position.x}, {self.current_position.y})",
            f"Accumulated cost: {self.accumulated_cost():.2f}",
            "Possible moves:",
        ]

        options = self.directions_with_cost()
        if options:
            lines.extend(f"  - {direction.name} (cost: {cost:.2f})" for direction, cost in options)
        else:
            lines.append("  - <none>")

        if self.rules.is_hint_enabled(GoldMineHintMode.COMPASS) and not self.rules.finished(self):
            lines.append(f"Compass hint: {self.compass_hint().name}")
        if self.rules.is_hint_enabled(GoldMineHintMode.PROXIMITY):
            lines.append(f"Proximity hint: {self.proximity_hint()}")
        if self.rules.is_hint_enabled(GoldMineHintMode.DENSITY):
            lines.append(f"Density hint: {self.density_hint():.2f}")

        return "\n".join(lines)

    def __str__(self) -> str:
        """Render this position using the text-rendering protocol.

        Args:
            None.

        Returns:
            Same value as :meth:`to_text`.
        """
        return self.to_text()

    def plot(self, target: Any | None = None) -> Any:
        """Render this position in a plotting backend.

        Args:
            target: Plotting target (for example, a matplotlib axis).

        Returns:
            Backend-specific plotting object returned by game rules.
        """
        if target is None:
            raise ValueError("target plotting axis is required")
        return self.rules.plot_step(axis=target, position=self)
