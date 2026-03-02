from __future__ import annotations

from typing import Dict, Iterator, List, Set, Tuple
from enum import Enum
from dataclasses import dataclass
from copy import deepcopy

from IArena.interfaces.IPosition import IPosition
from IArena.interfaces.IMovement import IMovement
from IArena.interfaces.IGameRules import IGameRules
from IArena.interfaces.PlayerIndex import PlayerIndex
from IArena.interfaces.ScoreBoard import ScoreBoard
from IArena.utils.decorators import override
from IArena.utils.printing import matrix_map_to_str

"""
This game represents a Treasure hunt over a grid map.

The map is unknown to the player, and the tiles must be dug one by one to discover if there is a treasure or not.
The tiles to dig are those close to an already dug tile. These are called visible tiles.
Each tile has a digging cost, only known when the tile is visible.
Each tile have an heuristic indicating some clues about the presence of treasures in adjacent tiles.

There are different modes for the game:

- Navigation mode:
    - OFF: every visible tile can be dug directly.
    - ON: the player must move over already dug tiles to reach other areas of the map.

. Hint mode:
    - OFF: no hints are provided.
    - Distance: each dug tile counts with the minimum number of tiles to reach the treasure.
    - Probability: each dug tile counts with a consistent probability of having a treasure in adjacent tiles.
"""

class Direction(Enum):
    """Possible movement directions in the grid."""
    Up = 0
    Down = 1
    Left = 2
    Right = 3


@dataclass
class Coordinate:
    """Represents a coordinate in the grid."""
    x: int
    y: int

    def up(self) -> "Coordinate":
        """Return the coordinate above the given one."""
        return Coordinate(self.x - 1, self.y)

    def down(self) -> "Coordinate":
        """Return the coordinate below the given one."""
        return Coordinate(self.x + 1, self.y)

    def left(self) -> "Coordinate":
        """Return the coordinate to the left of the given one."""
        return Coordinate(self.x, self.y - 1)

    def right(self) -> "Coordinate":
        """Return the coordinate to the right of the given one."""
        return Coordinate(self.x, self.y + 1)

    def from_direction(self) -> "Coordinate":
        """Return a new coordinate moved in the given direction."""
        if self == Direction.Up:
            return self.up()
        elif self == Direction.Down:
            return self.down()
        elif self == Direction.Left:
            return self.left()
        elif self == Direction.Right:
            return self.right()
        else:
            raise ValueError("Invalid direction provided.")


# Alias for a movement cost type
CostType = float


class SquareMap:
    """
    Represents the grid of the game.

    Attributes:
        map: List[List[CostType]] - The grid represented as a matrix of values.
    """

    def __init__(self, map: List[List[CostType]]):
        """Initialize the map wrapper with a 2D matrix of costs/values."""
        self.map_ = map

    def __str__(self):
        """Return a human-readable string representation of the map matrix."""
        return matrix_map_to_str(self.map_)

    def size(self) -> Tuple[int, int]:
        """Return (n_rows, n_cols) of the map."""
        return len(self.map_), len(self.map_[0])

    def __len__(self):
        """Return number of rows (so `len(map)` works)."""
        return len(self.map_)

    def __getitem__(self, index: Coordinate) -> CostType:
        """Return the cost/value at a given Coordinate (row=x, col=y)."""
        return self.map_[index.x][index.y]

    def in_bounds(self, coord: Coordinate) -> bool:
        """Check whether a coordinate is inside the map boundaries."""
        rows, cols = self.size()
        return 0 <= coord.x < rows and 0 <= coord.y < cols

    def possible_direction_neighbor(self, coord: Coordinate) -> Iterator[Direction, Coordinate]:
        """Yield (direction, neighbor_coordinate) pairs for all in-bounds 4-neighbors."""
        if self.in_bounds(Coordinate(coord.x - 1, coord.y)):
            yield (Direction.Up, Coordinate(coord.x - 1, coord.y))
        if self.in_bounds(Coordinate(coord.x + 1, coord.y)):
            yield (Direction.Down, Coordinate(coord.x + 1, coord.y))
        if self.in_bounds(Coordinate(coord.x, coord.y - 1)):
            yield (Direction.Left, Coordinate(coord.x, coord.y - 1))
        if self.in_bounds(Coordinate(coord.x, coord.y + 1)):
            yield (Direction.Right, Coordinate(coord.x, coord.y + 1))

    def possible_directions(self, coord: Coordinate) -> Iterator[Direction]:
        """Yield the directions that have an in-bounds neighbor from the given coordinate."""
        for direction, _ in self.possible_direction_neighbor(coord):
            yield direction

    def possible_neighbors(self, coord: Coordinate) -> Iterator[Coordinate]:
        """Yield all in-bounds neighboring coordinates (4-neighborhood)."""
        for _, neighbor in self.possible_direction_neighbor(coord):
            yield neighbor

    def check(self, allow_zero: bool = True):
        """
        Validate map shape and values.

        - Must have at least one row.
        - All rows must have the same length.
        - Values must be positive (or non-negative if allow_zero=True).
        """
        if len(self.map_) == 0:
            raise ValueError("The map must have at least one row.")
        n_cols = len(self.map_[0])
        for row in self.map_:
            if len(row) != n_cols:
                raise ValueError("All rows must have the same length.")
            for value in row:
                if allow_zero:
                    if value < 0:
                        raise ValueError("All values must be non-negative.")
                else:
                    if value <= 0:
                        raise ValueError("All values must be positive.")

    @classmethod
    def zeros(cls, n_rows: int, n_cols: int) -> "SquareMap":
        """Create a SquareMap of given size filled with zeros."""
        return SquareMap([[0.0 for _ in range(n_cols)] for _ in range(n_rows)])

    def zeros_like(self) -> "SquareMap":
        """Create a SquareMap of the same size as this one, filled with zeros."""
        n_rows, n_cols = self.size()
        return SquareMap.zeros(n_rows, n_cols)


class TreasureHuntMovement(IMovement):
    """
    Represent a movement in the Treasure Hunt game.

    If the direction points to a free space, the player can move to that coordinate.
    Otherwise, the movement digs the tile at the coordinate.
    """
    def __init__(self, coordinate: Coordinate):
        """Create a movement that targets a specific coordinate (move-to or dig-at)."""
        self.__coordinate = coordinate

    def __eq__(self, other: "TreasureHuntMovement"):
        """Compare movements by their target coordinate."""
        return self.__coordinate == other.__coordinate

    def _get_coordinate(self) -> Coordinate:
        """Return the target coordinate of this movement."""
        return self.__coordinate


class TreasureHuntPosition(IPosition):
    """
    Treasure Hunt game state (position) representation.

    A `TreasureHuntPosition` encapsulates the *entire* mutable game state required by the IArena
    framework to:
      - determine the next player to act,
      - enumerate legal actions (movements),
      - compute costs / heuristic values,
      - and detect terminal states.

    This implementation is single-player and models a grid exploration / digging process.

    Notes
    -----
    - The state is defined by:
        (1) the current player coordinate,
        (2) the set of already dug tiles,
    - The position delegates rules-specific computations (movement generation, cost, heuristic)
      to `TreasureHuntGameRules`.
    """

    def __init__(
        self,
        rules: "TreasureHuntGameRules",
        current_position: Coordinate,
        digged_tiles: Set[Coordinate],
    ):
        """
        Create a new `TreasureHuntPosition`.

        Parameters
        ----------
        rules : TreasureHuntGameRules
            The rules object governing the game logic. This is stored and used to compute:
            - legal movements from this position,
            - accumulated cost,
            - heuristic values,
            - and state transitions.
        current_position : Coordinate
            Current player coordinate on the map.
        digged_tiles : Set[Coordinate]
            Set of tiles already dug (discovered). Must include at least the start tile.
            The set is treated as part of the position state; callers should pass an
            immutable or safely-owned set to avoid unintended side effects.

        Side Effects
        ------------
        - Calls `IPosition.__init__(rules)` to initialize the IArena base class.

        Raises
        ------
        TypeError
            If the provided arguments have incompatible types (depending on runtime checks).
        """
        super().__init__(rules)
        self.__rules: TreasureHuntGameRules = rules
        self.__current_position = current_position
        self.__digged_tiles = digged_tiles


    ##################################################################################################################
    # STD METHODS

    @override
    def next_player(self) -> PlayerIndex:
        """
        Return the player index that must act next.

        Returns
        -------
        PlayerIndex
            Always `PlayerIndex.FirstPlayer`, since this game is single-player.

        Notes
        -----
        IArena uses this method to determine whose turn it is. For single-player games,
        the value is constant.
        """
        return PlayerIndex.FirstPlayer

    def __eq__(self, other: TreasureHuntPosition) -> bool:
        """
        Equality comparison for positions.

        Two positions are considered equal if they represent the same game state, i.e.:
          - same current coordinate, and
          - same set of dug tiles.

        Parameters
        ----------
        other : TreasureHuntPosition
            The position to compare against.

        Returns
        -------
        bool
            True if both positions encode the same state; False otherwise.
        """
        return (
            self.__current_position == other.__current_position
            and self.__digged_tiles == other.__digged_tiles
        )

    def __str__(self) -> str:
        """
        Return a human-readable representation of the position.

        Returns
        -------
        str
            A string describing this position, typically including:
            - current coordinate,
            - number of dug tiles,
            - finished flag.

        Notes
        -----
        Currently unimplemented (returns empty string). Implementing this is useful for:
        debugging, logging, and visualization of search traces.
        """
        return ""  # TODO

    def get_accumulated_cost(self) -> CostType:
        """
        Compute the cumulative digging cost for this state.

        Returns
        -------
        CostType
            Total cost accumulated by digging all tiles contained in `__digged_tiles`.

        Complexity
        ----------
        O(|digged_tiles|), assuming constant-time cost lookup per tile.
        """
        return self.__rules.accumulated_cost(self.__digged_tiles)

    def get_heuristic(self) -> CostType:
        """
        Return the heuristic estimate for the current state.

        Returns
        -------
        CostType
            Heuristic value at `__current_position`, or 0.0 if heuristic mode is disabled.

        Typical Use
        -----------
        Used by informed search algorithms as `h(n)` to guide exploration.
        """
        return self.__rules.get_heuristic(self.__current_position)

    ##################################################################################################################


    ##################################################################################################################
    # OMNIPRESENT MODE

    def omnipresent_mode(self) -> bool:
        """
        Return whether the game is in omnipresent mode.

        Returns
        -------
        bool
            True if omnipresent mode is enabled; False otherwise.

        Notes
        -----
        In omnipresent mode, the player can dig any tile adjacent to already dug tiles,
        not just those adjacent to the current position.
        """
        return self.__rules.omnipresent_mode()

    def get_omnipresent_dig(self) -> Iterator[Tuple[TreasureHuntMovement, CostType]]:
        """
        Generate all legal diggable tiles from this position.

        Returns
        -------
        Iterator[Tuple[TreasureHuntMovement, CostType]]
            An iterator yielding movement-cost pairs:
            - movement : TreasureHuntMovement
                The movement object describing the action (target coordinate).
            - cost : CostType
                The action cost of taking that movement.

        Complexity
        ----------
        Typically O(degree) where degree <= 4 in grid mode, but may be larger in
        omnipresent mode depending on visible frontier size.

        Warning
        -------
        This method is only meaningful in omnipresent mode. In standard mode,
        use direction methods instead.
        """
        for _, movement, cost in self.get_movements():
            yield (movement, cost)

    ##################################################################################################################


    ##################################################################################################################
    # PROTECTED INTERNAL METHODS

    def _already_dig(self, coordinate: Coordinate) -> bool:
        """
        Check if a tile has already been dug.
        """
        return coordinate in self.__digged_tiles

    def _generate_new_position_from_movement(
        self,
        movement: TreasureHuntMovement,
        final_tile: Coordinate
    ) -> "TreasureHuntPosition":
        """
        Produce the successor position after applying a movement.
        """

        # Extract new coordinate from movement
        new_coordinate = movement._get_coordinate()

        new_digged_tiles = deepcopy(self.__digged_tiles)
        new_digged_tiles.add(new_coordinate)

        return TreasureHuntPosition(
            self.__rules,
            new_coordinate,
            new_digged_tiles,
            final_tile in new_digged_tiles
        )

    ##################################################################################################################


    ##################################################################################################################
    # DIRECTION BASED METHODS

    def get_valid_directions(self) -> Iterator[Direction]:
        """
        Generate all legal directions from this position.

        Returns
        -------
        Iterator[Direction]
            An iterator yielding legal movement directions (Up/Down/Left/Right).

        Complexity
        ----------
        Typically O(degree) where degree <= 4 in grid mode, but may be larger in
        omnipresent mode depending on visible frontier size.
        """
        return self.__rules.get_valid_directions(
            self.__current_position,
        )

    def get_movement_from_direction(
        self,
        direction: Direction
    ) -> TreasureHuntMovement:
        """
        Get the movement object corresponding to a given direction.

        Parameters
        ----------
        direction : Direction
            The direction for which to obtain the movement.

        Returns
        -------
        TreasureHuntMovement
            The movement object corresponding to the specified direction.
        """
        return TreasureHuntMovement(self.__current_position.from_direction(direction))

    def get_cost_from_direction(
        self,
        direction: Direction
    ) -> CostType:
        """
        Get the cost associated with moving in a given direction.

        Parameters
        ----------
        direction : Direction
            The direction for which to obtain the cost.

        Returns
        -------
        CostType
            The cost associated with the specified direction.
        """
        new_coordinate = self.__current_position.from_direction(direction)
        if new_coordinate in self.__digged_tiles:
            return 0.0
        else:
            return self.__rules._get_cost(self.__current_position.from_direction(direction))

    ##################################################################################################################





class TreasureHuntGameRules(IGameRules):
    """
    Represents the rules of the Treasure Hunt game.

    In this implementation, the rules define the map, the target coordinate and the starting coordinate.
    The logic of digged tiles and movement is handled in the Position class.
    """

    def __init__(
        self,
        map: SquareMap,
        target: Coordinate,
        start: Coordinate = Coordinate(0, 0),
        omnipresent_mode: bool = False,
        heuristic_map: SquareMap = None
    ):
        """Initialize rules: map/target/start plus optional omnipresent and heuristic modes."""
        self.__map = deepcopy(map)
        self.__target = deepcopy(target)
        self.__start = deepcopy(start)

        self.__omnipresent_mode = omnipresent_mode

        self.__heuristic_map = heuristic_map if heuristic_map is not None else self.__map.zeros_like()

        # Check map
        self.__map.check(allow_zero=False)

    @override
    def n_players(self) -> int:
        """Return number of players (Treasure Hunt is single-player here)."""
        return 1

    @override
    def first_position(self) -> TreasureHuntPosition:
        """Return the initial position for a new game instance."""
        return TreasureHuntPosition(self, self.__start, [self.__start])

    @override
    def next_position(
        self,
        movement: TreasureHuntMovement,
        position: TreasureHuntPosition
    ) -> TreasureHuntPosition:
        """Apply a movement to a position and return the resulting successor position."""
        return position._generate_new_position(
            movement.coordinate,
            self.__target
        )

    @override
    def possible_movements(
        self,
        position: TreasureHuntPosition
    ) -> Iterator[TreasureHuntMovement]:
        """Yield the legal movement objects from the given position (dropping direction/cost)."""
        moves = position.get_movements()
        for _, move, _ in moves:
            yield move

    @override
    def finished(self, position: TreasureHuntPosition) -> bool:
        """Return True if the game is finished in this position (target already dug)."""
        return position._already_dig(self.__target)

    @override
    def score(self, position: TreasureHuntPosition) -> ScoreBoard:
        """Return a scoreboard value for terminal evaluation (negative cost => lower is worse)."""
        sb = ScoreBoard()
        sb.define_score(PlayerIndex.FirstPlayer, -position.accumulated_cost())
        return sb

    def accumulated_cost(self, digged_tiles: List[Coordinate]) -> CostType:
        """Compute total cost over all dug tiles using the underlying cost map."""
        total_cost = 0.0
        for coord in digged_tiles:
            total_cost += self.__map[coord.x, coord.y]
        return total_cost

    def get_heuristic(self, coordinate: Coordinate) -> CostType:
        """Return heuristic value for a coordinate if enabled, otherwise 0."""
        if not self.__heuristic_activated:
            return 0.0
        return self.__heuristic_map[coordinate.x, coordinate.y]

    def get_movements(
        self,
        coordinate: Coordinate,
        digged_tiles: Set[Coordinate]
    ) -> Iterator[Tuple[Direction, TreasureHuntMovement, CostType]]:
        """
        Yield available moves from a coordinate and dug set.

        - Omnipresent mode: any neighbor of any dug tile is diggable (cost = tile cost).
        - Otherwise: 4-neighbors of current coordinate are available; already-dug neighbors cost 0.
        """
        if self.__omnipresent_mode:
            # Every tile touching a digged tile can be dug
            checked_tiles = set()
            for digged_tile in digged_tiles:
                for neighbor in self.__map.possible_neighbors(digged_tile):
                    if neighbor not in digged_tiles and neighbor not in checked_tiles:
                        checked_tiles.add(neighbor)
                        yield (
                            None,
                            TreasureHuntMovement(neighbor),
                            self.__map[neighbor.x, neighbor.y]
                        )

        else:
            # Only tiles touching the current one. If already digged, their cost is 0.
            for direction, neighbor in self.__map.possible_direction_neighbor(coordinate):

                if neighbor in digged_tiles:
                    yield (
                        direction,
                        TreasureHuntMovement(neighbor),
                        0.0
                    )

                else:
                    yield (
                        direction,
                        TreasureHuntMovement(neighbor),
                        self.__map[neighbor.x, neighbor.y]
                    )

    def omnipresent_mode(self) -> bool:
        """Return whether omnipresent mode is enabled."""
        return self.__omnipresent_mode

    def _get_cost(
        self,
        coordinate: Coordinate
    ) -> CostType:
        """Return the cost of digging at the given coordinate."""
        return self.__map[coordinate.x, coordinate.y]
