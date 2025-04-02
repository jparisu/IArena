
from typing import Iterator, List
from enum import Enum
from copy import deepcopy

from IArena.interfaces.IPosition import IPosition
from IArena.interfaces.IMovement import IMovement
from IArena.interfaces.IGameRules import IGameRules
from IArena.interfaces.PlayerIndex import PlayerIndex, two_player_game_change_player
from IArena.utils.decorators import override
from IArena.interfaces.ScoreBoard import ScoreBoard

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
        Empty = -1
        FirstPlayer = 0
        SecondPlayer = 1

    def __init__(
            self,
            rules: "TicTacToeRules",
            board: List[List[PlayerIndex]] = None,
            next_player: PlayerIndex = None):
        super().__init__(rules)

        # Set the board
        if board is None:
            board = TicTacToePosition.empty_board()
        self.board_ = board

        # If next player not given, calculate it
        # If odd pieces in the board, then it is the second player's turn
        if next_player is None:
            n_pieces = sum([sum([1 for x in row if x != TicTacToePosition.TicTacToePiece.Empty]) for row in self.board_])
            next_player = PlayerIndex.FirstPlayer if n_pieces % 2 == 0 else PlayerIndex.SecondPlayer

        self.next_player_ = next_player


    @override
    def next_player(
            self) -> PlayerIndex:
        return self.next_player_

    def board(self) -> List[List[PlayerIndex]]:
        return deepcopy(self.board_)

    def short_str(self) -> str:
        l = f"{self.next_player_}"
        for row in self.board_:
            l += "|"
            for column in row:
                l += str(column.value)
        return l


    def __eq__(
            self,
            other: "TicTacToePosition") -> bool:
        return self.board_ == other.board_ and self.next_player_ == other.next_player_

    def __str__(self) -> str:
        line = "+---+---+---+\n"
        st = line
        for row in self.board_:
            st += "|"
            for column in row:
                if column == TicTacToePosition.TicTacToePiece.Empty:
                    st += "   "
                elif column == TicTacToePosition.TicTacToePiece.FirstPlayer:
                    st += " X "
                elif column == TicTacToePosition.TicTacToePiece.SecondPlayer:
                    st += " O "
                st += "|"
            st += "\n"
            st += line
        return st

    def __getitem__(self, item: int) -> int:
        return self.board[item]

    def __hash__(self) -> int:
        return hash(self.short_str())

    def empty_board() -> List[List[PlayerIndex]]:
        return [
            [TicTacToePosition.TicTacToePiece.Empty for _ in range(3)] for _ in range(3)
        ]


class TicTacToeRules(IGameRules):

    def __init__(
            self,
            initial_position: TicTacToePosition = None):
        """
        Args:
            initial_position: The number of TicTacToe at the beginning of the game.
        """
        if initial_position is None:
            initial_position = TicTacToePosition(rules=self)
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
        board = position.board()

        # Check the movement is possible
        if board[movement.row][movement.column] != TicTacToePosition.TicTacToePiece.Empty:
            raise Exception(f"Invalid movement: {movement}, the position is already taken")

        if position.next_player() == PlayerIndex.FirstPlayer:
            board[movement.row][movement.column] = TicTacToePosition.TicTacToePiece.FirstPlayer
        else:
            board[movement.row][movement.column] = TicTacToePosition.TicTacToePiece.SecondPlayer

        return TicTacToePosition(rules=self, board=board)

    @override
    def possible_movements(
            self,
            position: TicTacToePosition) -> Iterator[TicTacToeMovement]:
        movements = []
        for row in range(3):
            for column in range(3):
                if position.board_[row][column] == TicTacToePosition.TicTacToePiece.Empty:
                    movements.append(TicTacToeMovement(row, column))
        return movements


    @override
    def finished(
            self,
            position: TicTacToePosition) -> bool:
        return self.__look_for_3_connected__(position) != None


    @override
    def score(
            self,
            position: TicTacToePosition) -> ScoreBoard:
        s = ScoreBoard()
        winner = self.__look_for_3_connected__(position)

        if winner is None:
            raise Exception("The game is not finished")

        elif winner == TicTacToePosition.TicTacToePiece.Empty:
            s.add_score(PlayerIndex.FirstPlayer, 0.0)
            s.add_score(PlayerIndex.SecondPlayer, 0.0)

        elif winner == TicTacToePosition.TicTacToePiece.FirstPlayer:
            s.add_score(PlayerIndex.FirstPlayer, 1.0)
            s.add_score(PlayerIndex.SecondPlayer, -1.0)

        else:
            s.add_score(PlayerIndex.FirstPlayer, -1.0)
            s.add_score(PlayerIndex.SecondPlayer, 1.0)

        return s


    def __look_for_3_connected__(self, position: TicTacToePosition) -> TicTacToePosition.TicTacToePiece:
        # Check if there is a winner in the rows
        for row in range(3):
            if (position.board_[row][0] != TicTacToePosition.TicTacToePiece.Empty
                    and position.board_[row][0] == position.board_[row][1]
                    and position.board_[row][1] == position.board_[row][2]):
                return position.board_[row][0]

        # Check if there is a winner in the columns
        for column in range(3):
            if (position.board_[0][column] != TicTacToePosition.TicTacToePiece.Empty
                    and position.board_[0][column] == position.board_[1][column]
                    and position.board_[1][column] == position.board_[2][column]):
                return position.board_[0][column]

        # Check if there is a winner in the diagonals
        if (position.board_[0][0] != TicTacToePosition.TicTacToePiece.Empty
                and position.board_[0][0] == position.board_[1][1]
                and position.board_[1][1] == position.board_[2][2]):
            return position.board_[0][0]

        if (position.board_[0][2] != TicTacToePosition.TicTacToePiece.Empty
                and position.board_[0][2] == position.board_[1][1]
                and position.board_[1][1] == position.board_[2][0]):
            return position.board_[0][2]

        # It have finished if there is a winner or the board_ is full
        if all([all([x != TicTacToePosition.TicTacToePiece.Empty for x in row]) for row in position.board_]):
            return TicTacToePosition.TicTacToePiece.Empty

        return None
