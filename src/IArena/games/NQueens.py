
from typing import Iterator, List

from IArena.interfaces.IPosition import IPosition
from IArena.interfaces.IMovement import IMovement
from IArena.interfaces.IGameRules import IGameRules
from IArena.interfaces.PlayerIndex import PlayerIndex
from IArena.utils.decorators import override

"""
This game represents the NQueens game.
In a chessboard of NxN, N queens must be placed in a way that no queen can attack another.
"""

class NQueensPosition(IPosition):
    """
    List of positions of the queens along the board.

    Attributes:
        n: Size of the board = nxn
        positions: List of (x,y) positions of the queens
    """
    def __init__(self, n, positions: List[tuple[int, int]] = []) -> None:
        self.n = n
        self.positions = positions

    @override
    def next_player(
            self) -> PlayerIndex:
        return PlayerIndex.FirstPlayer

    def __str__(self) -> str:
        # Print the board with the queens
        board = [["." for _ in range(self.n)] for _ in range(self.n)]
        for x, y in self.positions:
            board[x][y] = "Q"
        return "\n".join(["".join(row) for row in board])

    def __len__(self) -> int:
        return len(self.positions)


class NQueensMovement(IMovement):
    """
    A movement in this game is the position of the 1 queen in the board.

    Attributes:
        new_position: (x,y) position of the new queen
    """

    def __init__(
            self,
            new_position: tuple[int, int]):
        self.new_position = new_position

    def __eq__(
            self,
            other: "NQueensMovement"):
        return self.new_position == other.new_position

    def __str__(self):
        return f'[{self.new_position[0]},{self.new_position[1]}]'


class NQueensRules(IGameRules):
    """
    Rules of the NQueens game.

    Attributes:
        n: Size of the board = nxn

    The score of the game is calculated as the number of queens that are attacking other queens.
    0 score is the best score.
    """

    DefaultBoardSize = 8

    def __init__(
            self,
            n: int = DefaultBoardSize):
        """
        Args:
            n: Size of the board = nxn
        """
        self.n = n

    @override
    def n_players(self) -> int:
        return 1

    @override
    def first_position(self) -> NQueensPosition:
        return NQueensPosition(self.n)

    @override
    def next_position(
            self,
            movement: NQueensMovement,
            position: NQueensPosition) -> NQueensPosition:
        return NQueensPosition(self.n, position.positions + [movement.new_position])

    @override
    def possible_movements(
            self,
            position: NQueensPosition) -> Iterator[NQueensMovement]:
        return [NQueensMovement((x, y)) for x in range(self.n) for y in range(self.n)]

    @override
    def finished(
            self,
            position: NQueensPosition) -> bool:
        return len(position) == self.n


    @override
    def score(
            self,
            position: NQueensPosition) -> dict[PlayerIndex, float]:
        # Sum 1 for each queen that is attacking other
        attacks = 0

        # For each queen
        for x, y in position.positions:
            # For each other
            for x2, y2 in position.positions:
                if x != x2 and y != y2:

                    # Check if it not attacking other horizontally
                    if x == x2:
                        attacks += 1
                    # Check if it not attacking other vertically
                    if y == y2:
                        attacks += 1
                    # Check if it not attacking other diagonally
                    if abs(x - x2) == abs(y - y2):
                        attacks += 1

        return {PlayerIndex.FirstPlayer: attacks}
