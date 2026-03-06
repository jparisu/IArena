"""Default baseline player for GoldMine."""

from __future__ import annotations

from iarena.desining.gaming.Movement import Movement
from iarena.desining.gaming.Position import Position
from iarena.desining.playing.Player import Player
from iarena.gaming.GoldMine.GoldMineMovement import GoldMineMovement
from iarena.gaming.GoldMine.GoldMinePosition import GoldMinePosition


class GoldMinePlayer(Player):
    """Greedy baseline player that minimizes immediate digging cost."""

    def play(self, position: Position) -> Movement:
        """Choose one legal movement from the provided position.

        Args:
            position: Current game position.

        Returns:
            Selected GoldMine movement.
        """
        if not isinstance(position, GoldMinePosition):
            raise TypeError(f"position must be GoldMinePosition, got {type(position).__name__}")

        options = position.directions_with_cost()
        if not options:
            raise RuntimeError("no legal movement available for GoldMinePlayer")

        direction, _ = min(options, key=lambda item: (item[1], item[0].name))
        return GoldMineMovement(direction=direction)
