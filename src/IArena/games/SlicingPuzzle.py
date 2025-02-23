
from typing import Iterator, List
from enum import Enum
import random

from IArena.interfaces.IPosition import CostPosition, CostType
from IArena.interfaces.IMovement import IMovement
from IArena.interfaces.IGameRules import IGameRules
from IArena.interfaces.PlayerIndex import PlayerIndex
from IArena.interfaces.ScoreBoard import ScoreBoard
from IArena.utils.decorators import override

"""
This game represents the SlicingPuzzle game.
This is a grid NxN with NxN-1 numerated squares.
One movement moves one of the squares next to the empty space to the empty space.
The goal is to order the squares from 1 to NxN-1.
"""

class SlicingPuzzlePosition(CostPosition):
    """
    This is the grid NxN with NxN-1 numerated squares.
    The empty space is the -1.
    The not empty numbers go from 1 to NxN-1.
    """
    def __init__(
            self,
            rules: "SlicingPuzzleRules",
            squares: List[List[int]],
            cost: CostType) -> None:
        super().__init__(rules, cost)
        self.squares = squares
        self.n = len(squares)

    @override
    def next_player(
            self) -> PlayerIndex:
        return PlayerIndex.FirstPlayer

    def __str__(self) -> str:
        # Print the board with the squares
        board = f"Cost: {self.cost()}\n"
        board += "+" + "----+" * self.n + "\n"
        for row in self.squares:
            for col in row:
                if col == -1:
                    board += "|    "
                else:
                    board += f"|{col:3d} "
            board += "|\n+" + "----+" * self.n + "\n"
        return board

    def empty_space(self):
        for i in range(self.n):
            for j in range(self.n):
                if self.squares[i][j] == -1:
                    return (i, j)


class SlicingPuzzleMovement(IMovement):
    """
    Represents the movement of one of the neighbors of the empty space to the empty space.

    Values:
        Up: 0 - Move up.
        Down: 1 - Move down.
        Left: 2 - Move left.
        Right: 3 - Move right.
    """

    class Values(Enum):
        Up = 0
        Down = 1
        Left = 2
        Right = 3


class SlicingPuzzleRules(IGameRules):
    """
    Rules for the SlicingPuzzle game.
    """

    DefaultSize = 3
    DefaultRandomShuffle = 1000


    def generate_correct_position(n: int) -> List[List[int]]:
        """
        Generate a correct position of the game.

        Args:
            n: Size of the board = nxn
        """
        squares = [[i + j * n + 1 for i in range(n)] for j in range(n)]
        squares[n - 1][n - 1] = -1
        return squares


    def generate_random_position(self, seed: int = None, random_moves: int = DefaultRandomShuffle) -> List[List[int]]:
        """
        Generate a random position of the game by moving random_moves times a correct one

        Args:
            seed: Seed for the random generator
            random_moves: Number of random movements
        """
        self.initial_position = SlicingPuzzlePosition(self, SlicingPuzzleRules.generate_correct_position(self.n), 0)

        # Move the squares randomly to generate a random position
        if seed is not None:
            random.seed(seed)

        for _ in range(random_moves):
            possible_movements = self.possible_movements(self.initial_position)
            movement = random.choice(list(possible_movements))
            self.initial_position = self.next_position(movement, self.initial_position)

        return self.initial_position.squares


    def __init__(
            self,
            initial_position: List[List[int]] = None,
            n: int = DefaultSize,
            seed: int = None):
        """
        Args:
            initial_position: Initial position of the game if given.
            n: Size of the board = nxn
        """
        if initial_position is None:
            self.n = n
            self.initial_position = self.generate_random_position(seed=seed)
        else:
            self.initial_position = initial_position
            self.n = len(initial_position)

    @override
    def n_players(self) -> int:
        return 1

    @override
    def first_position(self) -> SlicingPuzzlePosition:
        return SlicingPuzzlePosition(
            rules=self,
            squares=self.initial_position,
            cost=0)

    @override
    def next_position(
            self,
            movement: SlicingPuzzleMovement,
            position: SlicingPuzzlePosition) -> SlicingPuzzlePosition:
                # Find the empty space and move the square next to it to the empty space
        empty_space = position.empty_space()
        new_space = None

        if movement == SlicingPuzzleMovement.Values.Up:
            new_space = (empty_space[0] + 1, empty_space[1])

        elif movement == SlicingPuzzleMovement.Values.Down:
            new_space = (empty_space[0] - 1, empty_space[1])

        elif movement == SlicingPuzzleMovement.Values.Left:
            new_space = (empty_space[0], empty_space[1] + 1)

        elif movement == SlicingPuzzleMovement.Values.Right:
            new_space = (empty_space[0], empty_space[1] - 1)

        new_squares = [[position.squares[i][j] for j in range(self.n)] for i in range(self.n)]
        new_squares[empty_space[0]][empty_space[1]] = new_squares[new_space[0]][new_space[1]]
        new_squares[new_space[0]][new_space[1]] = -1

        return SlicingPuzzlePosition(
            rules=self,
            squares=new_squares,
            cost=position.cost() + 1)


    @override
    def possible_movements(
            self,
            position: SlicingPuzzlePosition) -> Iterator[SlicingPuzzleMovement]:
        # Find the empty space and return the possible movements depending on the borders of the game
        empty_space = position.empty_space()

        possible_movements = []
        if empty_space[0] > 0:
            possible_movements.append(SlicingPuzzleMovement.Values.Down)
        if empty_space[0] < self.n - 1:
            possible_movements.append(SlicingPuzzleMovement.Values.Up)
        if empty_space[1] > 0:
            possible_movements.append(SlicingPuzzleMovement.Values.Right)
        if empty_space[1] < self.n - 1:
            possible_movements.append(SlicingPuzzleMovement.Values.Left)

        return possible_movements


    @override
    def finished(
            self,
            position: SlicingPuzzlePosition) -> bool:
        # Check that every square is in the correct position
        correct_n = 1
        for i in range(self.n):
            for j in range(self.n):
                if position.squares[i][j] != correct_n:
                    if i == self.n - 1 and j == self.n - 1:
                        continue
                    else:
                        return False
                correct_n += 1
        return True


    @override
    def score(
            self,
            position: SlicingPuzzlePosition) -> ScoreBoard:
        s = ScoreBoard()
        s.add_score(PlayerIndex.FirstPlayer, position.cost())
        return s
