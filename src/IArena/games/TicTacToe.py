
from typing import Iterator, List
from enum import Enum
from copy import deepcopy

from IArena.interfaces.IPosition import IPosition
from IArena.interfaces.IMovement import IMovement
from IArena.interfaces.IGameRules import IGameRules
from IArena.interfaces.PlayerIndex import PlayerIndex, two_player_game_change_player
from IArena.utils.decorators import override

"""
This game represents the Tic Tac Toe or 3 in a row game.
The game is played on a 3x3 board, where each player has a symbol (X/1 or O).
The players alternate turns, and the first player to get 3 of their symbols in a row (horizontally, vertically or diagonally) wins.
If the board is full and neither player has 3 in a row, the game is a draw.
"""


class TicTacToeMovement(IMovement):
    """
    Represents a new position of the piece in the board.

    Attributes:
        row: [0, 1, 2] The row where the piece is moved.
        column: [0, 1, 2] The column where the piece is moved.
    """

    def __init__(
            self,
            row: int,
            column: int):
        self.row = row
        self.column = column

    def __eq__(
            self,
            other: "TicTacToeMovement"):
        return self.row == other.row and self.column == other.column

    def __str__(self):
        return f'[{self.row}, {self.column}]'


class TicTacToePosition(IPosition):
    """
    Represents the position of the board game.

    Attributes:
        board: List[List[int]] The board of the game.
    """

    class TicTacToePiece(Enum):
        Empty = 0
        FirstPlayer = 1
        SecondPlayer = 2

    def __init__(
            self,
            board: List[List[PlayerIndex]]):
        self.board = board

    @override
    def next_player(
            self) -> PlayerIndex:
        # The movement is first player if the count in the board is even, otherwise is second player.
        return PlayerIndex.FirstPlayer if sum(
            [sum([1 for x in row if x != TicTacToePosition.TicTacToePiece.Empty]) for row in self.board]) % 2 == 0 else PlayerIndex.SecondPlayer

    def __eq__(
            self,
            other: "TicTacToePosition"):
        return self.board == other.board

    def __str__(self):
        st = "----------------\n"
        for row in self.board:
            st += "|"
            for column in row:
                if column == TicTacToePosition.TicTacToePiece.Empty:
                    st += " "
                elif column == TicTacToePosition.TicTacToePiece.FirstPlayer:
                    st += "X"
                elif column == TicTacToePosition.TicTacToePiece.SecondPlayer:
                    st += "O"
                st += "|"
            st += "\n"
        st += "----------------\n"
        return st


class TicTacToeRules(IGameRules):

    def __init__(
            self,
            initial_position: TicTacToePosition = None):
        """
        Args:
            initial_position: The number of TicTacToe at the beginning of the game.
            min_play: The minimum number of TicTacToe that can be removed.
            max_play: The maximum number of TicTacToe that can be removed.
        """
        if initial_position is None:
            initial_position = TicTacToePosition(
                [
                    [TicTacToePosition.TicTacToePiece.Empty for _ in range(3)] for _ in range(3)
                ]
            )
        self.initial_position = initial_position

    @override
    def n_players(self) -> int:
        return 2

    @override
    def first_position(self) -> TicTacToePosition:
        return self.initial_position

    @override
    def next_position(
            self,
            movement: TicTacToeMovement,
            position: TicTacToePosition) -> TicTacToePosition:
        board = deepcopy(position.board)

        if position.next_player() == PlayerIndex.FirstPlayer:
            board[movement.row][movement.column] = TicTacToePosition.TicTacToePiece.FirstPlayer
        else:
            board[movement.row][movement.column] = TicTacToePosition.TicTacToePiece.SecondPlayer

        return TicTacToePosition(board=board)

    @override
    def possible_movements(
            self,
            position: TicTacToePosition) -> Iterator[TicTacToeMovement]:
        movements = []
        for row in range(3):
            for column in range(3):
                if position.board[row][column] == TicTacToePosition.TicTacToePiece.Empty:
                    movements.append(TicTacToeMovement(row, column))
        return movements

    @staticmethod
    def check_winner(position: TicTacToePosition) -> TicTacToePosition.TicTacToePiece:
        # Check if there is a winner in the rows
        for row in range(3):
            if (position.board[row][0] != TicTacToePosition.TicTacToePiece.Empty
                    and position.board[row][0] == position.board[row][1]
                    and position.board[row][1] == position.board[row][2]):
                return position.board[row][0]

        # Check if there is a winner in the columns
        for column in range(3):
            if (position.board[0][column] != TicTacToePosition.TicTacToePiece.Empty
                    and position.board[0][column] == position.board[1][column]
                    and position.board[1][column] == position.board[2][column]):
                return position.board[0][column]

        # Check if there is a winner in the diagonals
        if (position.board[0][0] != TicTacToePosition.TicTacToePiece.Empty
                and position.board[0][0] == position.board[1][1]
                and position.board[1][1] == position.board[2][2]):
            return position.board[0][0]

        if (position.board[0][2] != TicTacToePosition.TicTacToePiece.Empty
                and position.board[0][2] == position.board[1][1]
                and position.board[1][1] == position.board[2][0]):
            return position.board[0][2]

        return TicTacToePosition.TicTacToePiece.Empty


    @override
    def finished(
            self,
            position: TicTacToePosition) -> bool:
        winner = TicTacToeRules.check_winner(position)

        # It have finished if there is a winner or the board is full
        return winner != TicTacToePosition.TicTacToePiece.Empty or all(
            [all([x != TicTacToePosition.TicTacToePiece.Empty for x in row]) for row in position.board])

    @override
    def score(
            self,
            position: TicTacToePosition) -> dict[PlayerIndex, float]:
        winner = TicTacToeRules.check_winner(position)

        if winner == TicTacToePosition.TicTacToePiece.FirstPlayer:
            return {
                PlayerIndex.FirstPlayer: 0.0,
                PlayerIndex.SecondPlayer: 3.0
            }

        if winner == TicTacToePosition.TicTacToePiece.SecondPlayer:
            return {
                PlayerIndex.FirstPlayer: 3.0,
                PlayerIndex.SecondPlayer: 0.0
            }

        # If there is no winner, it is a draw
        return {
            PlayerIndex.FirstPlayer: 1.0,
            PlayerIndex.SecondPlayer: 1.0
        }
