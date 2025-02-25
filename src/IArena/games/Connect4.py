
from typing import Iterator, List
import copy

from IArena.interfaces.IPosition import IPosition
from IArena.interfaces.IMovement import IMovement
from IArena.interfaces.IGameRules import IGameRules
from IArena.interfaces.IPlayer import IPlayer
from IArena.interfaces.PlayerIndex import PlayerIndex, two_player_game_change_player
from IArena.utils.decorators import override
from IArena.interfaces.ScoreBoard import ScoreBoard

"""
This game represents the wide known connect 4 game.
"""

class Connect4Matrix:

    EMPTY_CELL = -1

    def __init__(
            self,
            matrix: List[List[int]],
            next_player: PlayerIndex = PlayerIndex.FirstPlayer):
        self.matrix = matrix
        self.next_player = next_player

    def n_rows(self) -> int:
        return len(self.matrix)

    def n_columns(self) -> int:
        return len(self.matrix[0])

    def __hash__(self):
        return hash(str(self))

    def __str__(self) -> str:
        n_rows = len(self.matrix)
        n_cols = len(self.matrix[0])
        st = str(self.next_player) + "|" + str(n_rows) + "|"
        for c in range(n_cols):
            for r in range(n_rows-1, -1, -1):
                if self.matrix[r][c] == Connect4Matrix.EMPTY_CELL:
                    break
                st += str(self.matrix[r][c])
            st += "|"
        return st

    def from_str(st: str):
        """
        Creates a Connect4Matrix object from a string.
        """
        parts = st.split("|")
        next_player = int(parts[0])
        n_rows = int(parts[1])
        n_cols = len(parts) - 3
        matrix = [[Connect4Matrix.EMPTY_CELL for _ in range(n_cols)] for _ in range(n_rows)]
        for c, part in enumerate(parts[2:]):
            for r in range(len(part)):
                matrix[n_rows - 1 - r][c] = int(part[r])

        return Connect4Matrix(matrix, next_player)


class Connect4Position(IPosition):
    """
    Represents the position of the game by a binary matrix of nxm, and the player to play

    Attributes:
        n: The number of rows of the board [default=6].
        m: The number of columns of the board [default=7].
    """

    EMPTY_CELL = Connect4Matrix.EMPTY_CELL

    def __init__(
            self,
            rules: "Connect4Rules",
            position: Connect4Matrix = None,
            matrix: List[List[int]] = None,
            next_player: PlayerIndex = PlayerIndex.FirstPlayer):
        IPosition.__init__(self, rules)

        if position:
            self.position = position
        elif matrix:
            self.position = Connect4Matrix(matrix, next_player)
        else:
            raise Exception("Invalid parameters: position or matrix must be provided")

    @override
    def next_player(
            self) -> PlayerIndex:
        return self.position.next_player

    def get_matrix(self) -> List[List[int]]:
        return copy.deepcopy(self.position.matrix)

    def n_rows(self) -> int:
        return self.position.n_rows()

    def n_columns(self) -> int:
        return self.position.n_columns()

    def __eq__(
            self,
            other: "Connect4Position"):
        return str(self.position) == str(other.position)

    def __str__(self):

        st = f"Player: {self.next_player()}\n"

        # PRINT MATRIX
        matrix = self.position.matrix
        r = len(matrix)
        c = len(matrix[0])

        st += "  " + "   ".join(map(str, range(c))) + "  \n"
        h_line = "+" + "---+" * c + "\n"
        st += h_line

        for i in range(r):
            st += "|"
            for j in range(c):
                if matrix[i][j] == Connect4Matrix.EMPTY_CELL:
                    st += "   |"
                else:
                    st += f" {matrix[i][j]} |"
            st += "\n"
            st += h_line

        return st

    def __hash__(self):
        return hash(self.position)

    def to_short_str(self) -> str:
        return str(self.position)

    def from_str(rules: "Connect4Rules", short_str: str) -> "Connect4Position":
        return Connect4Position(rules, Connect4Matrix.from_str(short_str))

    def convert_short_str_to_matrix(short_str: str) -> List[List[int]]:
        return Connect4Matrix.from_str(short_str).matrix

    def convert_short_str_to_matrix_str(short_str: str) -> str:
        return str(Connect4Position(None, Connect4Matrix.from_str(short_str)))

    def convert_matrix_to_short_str(matrix: List[List[int]]) -> str:
        return str(Connect4Matrix(matrix=matrix))

class Connect4Movement(IMovement):
    """
    Represents a movement of the player in the game by the column number

    Attributes:
        n: The number of coins removed.
    """

    def __init__(
            self,
            n: int):
        self.n = n

    def __eq__(
            self,
            other: "Connect4Movement"):
        return self.n == other.n

    def __str__(self):
        return f'{{column: {self.n}}}'


class Connect4Rules(IGameRules):

    DEFAULT_MATRIX = [[Connect4Matrix.EMPTY_CELL for _ in range(7)] for _ in range(6)]

    def __init__(
            self,
            initial_player: PlayerIndex = PlayerIndex.FirstPlayer,
            initial_matrix: List[List[int]] = None,
            initial_matrix_str: str = None):
        """
        Args:
            initial_matrix: The initial matrix of the game.
            initial_matrix_file: The file with the initial matrix.
        """
        if initial_matrix:
            self.initial_position = Connect4Position(
                rules=self,
                position=Connect4Matrix(
                    matrix=initial_matrix,
                    next_player=initial_player))

        elif initial_matrix_str:
            self.initial_position = Connect4Position.from_str(
                rules=self,
                short_str=initial_matrix_str)
        else:
            self.initial_position = Connect4Position(
                rules=self,
                position=Connect4Matrix(
                    matrix=Connect4Rules.DEFAULT_MATRIX,
                    next_player=initial_player))

        self.n_rows = self.initial_position.n_rows()
        self.n_cols = self.initial_position.n_columns()

    def n_rows(self) -> int:
        """Number of rows of the board."""
        return self.n_rows

    def n_columns(self) -> int:
        """Number of columns of the board."""
        return self.n_cols

    @override
    def n_players(self) -> int:
        return 2

    @override
    def first_position(self) -> Connect4Position:
        return self.initial_position

    @override
    def next_position(
            self,
            movement: Connect4Movement,
            position: Connect4Position) -> Connect4Position:

        matrix = position.get_matrix()

        # Check if the movement is valid
        if movement.n < 0 or movement.n >= self.n_cols:
            raise Exception(f"Invalid movement: invalid column: {movement.n}")
        # Check if the column is not full
        if matrix[0][movement.n] != Connect4Matrix.EMPTY_CELL:
            raise Exception(f"Invalid movement: full column: {movement.n}")

        # Copy matrix
        matrix = copy.deepcopy(matrix)

        # Find the first empty cell in the column
        i = self.n_rows - 1
        while i >= 0 and matrix[i][movement.n] != Connect4Matrix.EMPTY_CELL:
            i -= 1

        matrix[i][movement.n] = position.next_player()

        return Connect4Position(
            self,
            Connect4Matrix(
                matrix=matrix,
                next_player=two_player_game_change_player(position.next_player())
            )
        )


    @override
    def possible_movements(
            self,
            position: Connect4Position) -> Iterator[Connect4Movement]:
        # Check if the column is not full
        movements = []
        for i in range(self.n_cols):
            if position.get_matrix()[0][i] == Connect4Matrix.EMPTY_CELL:
                movements.append(Connect4Movement(i))
        return movements


    @override
    def finished(
            self,
            position: Connect4Position) -> bool:
        return self.__look_for_4_connected__(position) is not None


    @override
    def score(
            self,
            position: Connect4Position) -> ScoreBoard:
        s = ScoreBoard()
        winner = self.__look_for_4_connected__(position)

        if winner is None:
            raise Exception("The game is not finished")

        elif winner == PlayerIndex.Draw:
            s.add_score(PlayerIndex.FirstPlayer, 0.0)
            s.add_score(PlayerIndex.SecondPlayer, 0.0)

        else:
            s.add_score(winner, 1.0)
            s.add_score(two_player_game_change_player(winner), -1.0)

        return s


    def __look_for_4_connected__ (
            self,
            position: Connect4Position) -> PlayerIndex:
        """
        Look for 4 connected coins in the board.
        """
        matrix = position.get_matrix()
        for r in range(self.n_rows):
            for c in range(self.n_cols):
                if matrix[r][c] == Connect4Matrix.EMPTY_CELL:
                    continue
                player = matrix[r][c]
                # Check horizontal
                if c + 3 < self.n_cols and all(matrix[r][c + i] == player for i in range(4)):
                    return player
                # Check vertical
                if r + 3 < self.n_rows and all(matrix[r + i][c] == player for i in range(4)):
                    return player
                # Check diagonal (down-right)
                if r + 3 < self.n_rows and c + 3 < self.n_cols and all(matrix[r + i][c + i] == player for i in range(4)):
                    return player
                # Check diagonal (down-left)
                if r + 3 < self.n_rows and c - 3 >= 0 and all(matrix[r + i][c - i] == player for i in range(4)):
                    return player

        # If the board is full, return a draw
        if all(matrix[r][c] != Connect4Matrix.EMPTY_CELL for r in range(self.n_rows) for c in range(self.n_cols)):
            return PlayerIndex.Draw

        return None  # No win found



class Connect4PlayablePlayer(IPlayer):

    SeparatorN = 40

    @override
    def play(
            self,
            position: IPosition) -> IMovement:

        possibilities = list(position.get_rules().possible_movements(position))

        print ("=" * Connect4PlayablePlayer.SeparatorN)
        print (f"Next player: {position.next_player()}")
        print ("-" * Connect4PlayablePlayer.SeparatorN)
        print (position)
        print ("-" * Connect4PlayablePlayer.SeparatorN)
        print ("Movements:")

        valid_columns = [m.n for m in possibilities]
        print(f"Columns: {' , '.join(map(str, valid_columns))}")

        print ("=" * Connect4PlayablePlayer.SeparatorN)

        print (": ", end="")
        move = int(input())

        while move not in valid_columns:
            print ("Invalid movement")
            print (": ", end="")
            move = int(input())

        return Connect4Movement(move)
