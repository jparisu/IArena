
from typing import Dict, Iterator, List
from enum import Enum
import random
import math

from IArena.interfaces.IPosition import IPosition
from IArena.interfaces.IMovement import IMovement
from IArena.interfaces.IGameRules import IGameRules
from IArena.interfaces.PlayerIndex import PlayerIndex
from IArena.utils.decorators import override

"""
This game represents a grid search where each square has a different weight.
There is a grid of NxN and the player must reach the position [N-1,N-1] from [0,0].
The player can move in 4 directions: up, down, left and right.
Each movement has a cost equal to the weight of the square.
The player must reach the end with the minimum cost.
The grid is not known a priori, and must be discovered by the player step by step.
"""

class BlindWalkMovement(IMovement):
    """
    Represents the movement of the player in the grid.

    Values:
        Up: 0 - Move up.
        Down: 1 - Move down.
        Left: 2 - Move left.
        Right: 3 - Move right.
    """

    class Direction(Enum):
        Up = 0
        Down = 1
        Left = 2
        Right = 3

    def __init__(
            self,
            direction: Direction):
        self.direction = direction

    def __eq__(
            self,
            other: "FieldWalkMovement"):
        return self.direction == other.direction

    def __str__(self):
        return f'{self.direction.name}'

    def up() -> "FieldWalkMovement":
        return FieldWalkMovement(FieldWalkMovement.Direction.Up)

    def down() -> "FieldWalkMovement":
        return FieldWalkMovement(FieldWalkMovement.Direction.Down)

    def left() -> "FieldWalkMovement":
        return FieldWalkMovement(FieldWalkMovement.Direction.Left)

    def right() -> "FieldWalkMovement":
        return FieldWalkMovement(FieldWalkMovement.Direction.Right)




class BlindWalkPosition(IPosition):
    """
    Represents the position of the player in the grid.

    Attributes:
        x: The row of the position (goal N-1)
        y: The column of the position (goal N-1)
        cost: The cost of the path to reach this position.
    """

    def __init__(
            self,
            x: int,
            y: int,
            cost: int,
            neighbors: Dict[BlindWalkMovement, int]):
        self.x = x
        self.y = y
        self.cost = cost
        self.neighbors = neighbors

    @override
    def next_player(
            self) -> PlayerIndex:
        return PlayerIndex.FirstPlayer

    def __eq__(
            self,
            other: "BlindWalkPosition"):
        return self.x == other.x and self.y == other.y and self.cost == other.cost and self.neighbors == other.neighbors

    def __str__(self):
        return f'{{[x: {self.x}, y: {self.y}]  accumulated cost: {self.cost}  neighbors: {self.neighbors}}}'


class BlindWalkMap:

    def __init__(
            self,
            squares: List[List[int]]):
        self.squares__ = squares

    def __str__(self):
        return '\n'.join([' '.join(["%0:4d".format(square) for square in row]) for row in self.squares])

    def __len__(self):
        return len(self.squares)

    def __getitem__(self, i, j):
        return self.squares[i][j]

    def goal(self):
        return (len(self)-1, len(self)-1)

    def is_goal(self, position: BlindWalkPosition):
        return position.x == len(self.squares) - 1 and position.y == len(self.squares[0]) - 1

    def get_matrix(self) -> List[List[int]]:
        return self.squares

    @staticmethod
    def generate_random_map(rows: int, cols: int, seed: int = 0):
        random.seed(seed)
        lambda_parameter = 0.5  # You can adjust this to your preference

        def exponential_random_number():
            return max(1, int(-1/lambda_parameter * math.log(1 - random.random())))

        return BlindWalkMap(
            [[exponential_random_number() for j in range(cols)] for i in range(rows)])

    def get_possible_movements(self, position: BlindWalkPosition) -> List[BlindWalkMovement]:
        result = []
        if position.x > 0:
            result[BlindWalkMovement.Up] = self.squares[position.x - 1][position.y]
        if position.x < len(self.squares) - 1:
            result[BlindWalkMovement.Down] = self.squares[position.x + 1][position.y]
        if position.y > 0:
            result[BlindWalkMovement.Left] = self.squares[position.x][position.y - 1]
        if position.y < len(self.squares[position.x]) - 1:
            result[BlindWalkMovement.Right] = self.squares[position.x][position.y + 1]
        return result

    def get_next_position(self, position: BlindWalkPosition, movement: BlindWalkMovement) -> BlindWalkPosition:
        if movement == BlindWalkMovement.Up:
            return BlindWalkPosition(position.x - 1, position.y, position.cost + self.squares[position.x - 1][position.y])
        if movement == BlindWalkMovement.Down:
            return BlindWalkPosition(position.x + 1, position.y, position.cost + self.squares[position.x + 1][position.y])
        if movement == BlindWalkMovement.Left:
            return BlindWalkPosition(position.x, position.y - 1, position.cost + self.squares[position.x][position.y - 1])
        if movement == BlindWalkMovement.Right:
            return BlindWalkPosition(position.x, position.y + 1, position.cost + self.squares[position.x][position.y + 1])


class BlindWalkRules(IGameRules):

    def __init__(
            self,
            initial_map: BlindWalkMap = None,
            rows: int = 10,
            cols: int = 10,
            seed: int = 0):
        """
        Args:
            initial_map: The map of the game. If none, it is generated randomly.
            rows: The number of rows of the map. Only has effect if initial_map is None.
            cols: The number of columns of the map. Only has effect if initial_map is None.
            seed: The seed for the random generator of the map. Only has effect if initial_map is None.
        """
        if initial_map:
            self.__map = initial_map
        else:
            self.__map = BlindWalkMap.generate_random_map(rows, cols, seed)

    @override
    def n_players(self) -> int:
        return 1

    @override
    def first_position(self) -> BlindWalkPosition:
        return BlindWalkPosition(
            x=0,
            y=0,
            cost=0)

    @override
    def next_position(
            self,
            movement: BlindWalkMovement,
            position: BlindWalkPosition) -> BlindWalkPosition:
        return self.__map.get_next_position(position, movement)

    @override
    def possible_movements(
            self,
            position: BlindWalkPosition) -> Iterator[BlindWalkMovement]:
        return self.__map.get_possible_movements(position)

    @override
    def finished(
            self,
            position: BlindWalkPosition) -> bool:
        return position.map.is_goal(position)

    @override
    def score(
            self,
            position: BlindWalkPosition) -> dict[PlayerIndex, float]:
        return {PlayerIndex.FirstPlayer : position.cost}
