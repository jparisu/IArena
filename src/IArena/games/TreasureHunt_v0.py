
from typing import Iterator, List, Tuple, Dict, Optional, Set
from enum import Enum
from dataclasses import dataclass
from copy import deepcopy

from IArena.interfaces.IPosition import IPosition
from IArena.interfaces.IMovement import IMovement
from IArena.interfaces.IGameRules import IGameRules
from IArena.interfaces.PlayerIndex import PlayerIndex
from IArena.interfaces.ScoreBoard import ScoreBoard
from IArena.utils.decorators import override
from IArena.utils.SquareMap import SquareMapCoordinate, SquareMapMovement, SquareMap
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


# Alias for a movement cost type
CostType = float



class SquareMap:
    """
    Represents the grid of the game.

    Attributes:
        map: List[List[CostType]] - The grid represented as a matrix of values.
    """

    def __init__(
            self,
            map: List[List[CostType]]):
        self.map_ = map

    def __str__(self):
        return matrix_map_to_str(self.map_)

    def size(self) -> Tuple[int, int]:
        return len(self.map_), len(self.map_[0])

    def __len__(self):
        return len(self.map_)

    def __getitem__(self, index: Coordinate) -> CostType:
        return self.map_[index.x][index.y]

    def in_bounds(self, coord: Coordinate) -> bool:
        rows, cols = self.size()
        return 0 <= coord.x < rows and 0 <= coord.y < cols

    def possible_direction_neighbor(
            self,
            coord: Coordinate) -> Iterator[Direction, Coordinate]:
        if self.in_bounds(Coordinate(coord.x - 1, coord.y)):
            yield (Direction.Up, Coordinate(coord.x - 1, coord.y))
        if self.in_bounds(Coordinate(coord.x + 1, coord.y)):
            yield (Direction.Down, Coordinate(coord.x + 1, coord.y))
        if self.in_bounds(Coordinate(coord.x, coord.y - 1)):
            yield (Direction.Left, Coordinate(coord.x, coord.y - 1))
        if self.in_bounds(Coordinate(coord.x, coord.y + 1)):
            yield (Direction.Right, Coordinate(coord.x, coord.y + 1))

    def possible_directions(
            self,
            coord: Coordinate) -> Iterator[Direction]:
        for direction, _ in self.possible_direction_neighbor(coord):
            yield direction

    def possible_neighbors(self, coord: Coordinate) -> Iterator[Coordinate]:
        for _, neighbor in self.possible_direction_neighbor(coord):
            yield neighbor


    def modify_tile(
            self,
            coord: Coordinate,
            new_value: CostType):
        self.map_[coord.x][coord.y] = new_value

    def check(self, allow_zero: bool = False):
        """
        Check if the map is valid.

        It may have at least one row and one column.
        Every row must have the same length.
        Every value must be positive.
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


class TreasureHuntMovement(IMovement):
    """
    Represent a movement in the Treasure Hunt game.

    If the direction points to a free space, the player can move to that coordinate.
    Otherwise, the movement digs the tile at the coordinate.
    """
    def __init__(
            self,
            coordinate: Coordinate):
        self.__coordinate = coordinate

    def __eq__(
            self,
            other: "TreasureHuntMovement"):
        return self.__coordinate == other.__coordinate



class TreasureHuntPosition(IPosition):
    """
    Represents a position in the Treasure Hunt game.

    It have access to the movements possible and their costs.

    In this implementation, the position keeps track of the current coordinate and the set of digged tiles.
    """

    def __init__(
            self,
            rules: "TreasureHuntGameRules",
            current_position: Coordinate,
            digged_tiles: Set[Coordinate],
            finished: bool = False):
        super().__init__(rules)
        self.__rules: TreasureHuntGameRules = rules
        self.__current_position = current_position
        self.__digged_tiles = digged_tiles
        self.__finished = finished

    @override
    def next_player(
            self) -> PlayerIndex:
        return PlayerIndex.FirstPlayer

    def __eq__(
            self,
            other: "TreasureHuntPosition"):
        return self.__current_position == other.__current_position \
            and self.__digged_tiles == other.__digged_tiles

    def __str__(self):
        return "" #TODO

    def get_accumulated_cost(self) -> int:
        return self.__rules.accumulated_cost(self.__digged_tiles)

    def get_heuristic(self) -> float:
        return self.__rules.get_heuristic(self.__current_position)

    def get_movements(self) -> Iterator[Tuple[Direction, TreasureHuntMovement, CostType]]:
        return self.__rules.get_movements(
            self.__current_position,
            self.__digged_tiles)

    def _finished(self) -> bool:
        return self.__finished

    def _generate_new_position(
            self,
            new_coordinate: Coordinate,
            final_tile: Coordinate) -> "TreasureHuntPosition":
        new_digged_tiles = deepcopy(self.__digged_tiles)
        if new_coordinate not in new_digged_tiles:
            new_digged_tiles.add(new_coordinate)
        return TreasureHuntPosition(
            self.__rules,
            new_coordinate,
            new_digged_tiles,
            final_tile in new_digged_tiles
        )


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
            heuristic_mode: Optional[List[List[float]]] = None
            ):
        self.__map = deepcopy(map)
        self.__target = deepcopy(target)
        self.__start = deepcopy(start)

        self.__omnipresent_mode = omnipresent_mode

        if heuristic_mode is not None:
            self.__heuristic_activated = True
            self.__heuristic_map = SquareMap(heuristic_mode)
        else:
            self.__heuristic_activated = False

        # Check map
        self.__map.check(allow_zero=False)


    @override
    def n_players(self) -> int:
        return 1

    @override
    def first_position(self) -> TreasureHuntPosition:
        return TreasureHuntPosition(self, self.__start, [self.__start])

    @override
    def next_position(
            self,
            movement: TreasureHuntMovement,
            position: TreasureHuntPosition) -> TreasureHuntPosition:
        return position._generate_new_position(
            movement.coordinate,
            self.__target)


    @override
    def possible_movements(
            self,
            position: TreasureHuntPosition) -> Iterator[TreasureHuntMovement]:
        moves = position.get_movements()
        for _, move, _ in moves:
            yield move


    @override
    def finished(
            self,
            position: TreasureHuntPosition) -> bool:
        return position._finished()


    @override
    def score(
            self,
            position: TreasureHuntPosition) -> ScoreBoard:
        sb = ScoreBoard()
        sb.define_score(PlayerIndex.FirstPlayer, -position.accumulated_cost())
        return sb


    def accumulated_cost(
            self,
            digged_tiles: List[Coordinate]) -> CostType:
        total_cost = 0.0
        for coord in digged_tiles:
            total_cost += self.__map[coord.x, coord.y]
        return total_cost


    def get_heuristic(
            self,
            coordinate: Coordinate) -> CostType:
        if not self.__heuristic_activated:
            return 0.0
        return self.__heuristic_map[coordinate.x, coordinate.y]


    def get_movements(
            self,
            coordinate: Coordinate,
            digged_tiles: Set[Coordinate]
    ) -> Iterator[Tuple[Direction, TreasureHuntMovement, CostType]]:
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
