"""GoldMine position model."""

from __future__ import annotations

from collections.abc import Iterator
from typing import TYPE_CHECKING

from iarena.gaming.Position import Position
from iarena.playing.PlayerIndex import PlayerIndex
from iarena.utilizing.mapping.square_map.SquareMapCoordinate import SquareMapCoordinate
from iarena.utilizing.mapping.square_map.SquareMapDirection import SquareMapDirection

if TYPE_CHECKING:
    from iarena.gaming.goldmine.GoldMineRules import GoldMineRules
    from iarena.gaming.Rules import Rules


class GoldMinePosition(Position):
    """Concrete GoldMine position exposing only player-visible information."""

    _rules: GoldMineRules
    _current: SquareMapCoordinate
    _dug_tiles: set[tuple[int, int]]

    def __init__(
        self,
        rules: GoldMineRules,
        current: SquareMapCoordinate,
        dug_tiles: set[tuple[int, int]],
    ) -> None:
        """Create one GoldMine position.

        Args:
            rules: Rules object associated with this position.
            current: Current player coordinate.
            dug_tiles: Dug coordinates represented as `(x, y)` tuples.
        """
        rules._validate_position_state(current=current, dug_tiles=dug_tiles)
        self._rules = rules
        self._current = current
        self._dug_tiles = set(dug_tiles)

    def hash(self) -> int:
        """Return a stable hash representation of the position.

        Returns:
            int: Deterministic position hash.
        """
        return hash(
            (
                self._current.as_tuple(),
                tuple(sorted(self._dug_tiles)),
            ),
        )

    def __str__(self) -> str:
        """Return a compact textual representation of the position."""
        direction_text = ", ".join(
            f"{direction.name}:{self.get_cost_from_direction(direction)}" for direction in self.get_valid_directions()
        )
        return f"GoldMinePosition(moves=[{direction_text}])"

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
        return self._rules

    def get_compass(self) -> SquareMapDirection:
        """Return compass hint for current coordinate."""
        return self._rules._get_compass_hint(self)

    def get_proximity(self) -> int:
        """Return proximity hint for current coordinate."""
        return self._rules._get_proximity_hint(self)

    def get_density(self) -> float:
        """Return density hint for current coordinate."""
        return self._rules._get_density_hint(self)

    def get_valid_directions(self) -> Iterator[SquareMapDirection]:
        """Yield all valid directions from current coordinate."""
        yield from self._rules._get_valid_directions(self)

    def get_cost_from_direction(self, direction: SquareMapDirection) -> float:
        """Return movement cost for one direction.

        Args:
            direction: Candidate direction.

        Returns:
            float: `0.0` when destination tile was already dug; map value otherwise.
        """
        return self._rules._get_cost_from_direction(self, direction)

    def get_directions_with_cost(self) -> Iterator[tuple[SquareMapDirection, float]]:
        """Yield valid directions with movement costs."""
        for direction in self.get_valid_directions():
            yield direction, self.get_cost_from_direction(direction)

    def get_current_cost(self) -> float:
        """Return movement cost for current coordinate."""
        return self._rules._get_accumulated_cost(self)
