"""Default baseline player for GoldMine."""

from __future__ import annotations

from iarena.gaming.GoldMine.GoldMineMovement import GoldMineMovement
from iarena.gaming.GoldMine.GoldMinePosition import GoldMinePosition
from iarena.interfacing.IMovement import IMovement
from iarena.interfacing.IPlayer import IPlayer
from iarena.interfacing.IPosition import IPosition


class GoldMinePlayer(IPlayer):
    """Greedy baseline player that minimizes immediate digging cost."""

    def play(self, position: IPosition) -> IMovement:
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
