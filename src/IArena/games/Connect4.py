
from typing import Iterator, List
import copy

from IArena.interfaces.IPosition import IPosition
from IArena.interfaces.IMovement import IMovement
from IArena.interfaces.IGameRules import IGameRules
from IArena.interfaces.IPlayer import IPlayer
from IArena.interfaces.PlayerIndex import PlayerIndex, two_player_game_change_player
from IArena.utils.decorators import override
from IArena.interfaces.Score import ScoreBoard

"""
This game represents the wide known connect 4 game.
"""

class Connect4Position(IPosition):
    """
    Represents the position of the game by a binary matrix of nxm, and the player to play

    Attributes:
        n: The number of rows of the board [default=6].
        m: The number of columns of the board [default=7].
    """

    EMPTY_CELL = -1

    def __init__(
            self,
            rules: "Connect4Rules",
            matrix: List[List[int]],
            next_player: PlayerIndex):
        super().__init__(rules)
        self.matrix = matrix
        self.next_player_ = next_player

    @override
    def next_player(
            self) -> PlayerIndex:
        return self.next_player_

    def n_rows(self) -> int:
        return len(self.matrix)

    def n_columns(self) -> int:
        return len(self.matrix[0])

    def read_file(file):
        """
        Reads a file and returns a Connect4Position object.
        The file must contains a square matrix with 0s, 1s and '.'.
        """
        with open(file, 'r') as f:

            lines = f.readlines()
            matrix = []
            for line in lines:
                # Convert '.' to -1
                matrix.append([int(x) if x != '.' else Connect4Position.EMPTY_CELL for x in line.strip()])

            return matrix

    def __eq__(
            self,
            other: "Connect4Position"):
        # Compare matrix
        if self.matrix != other.matrix:
            return False
        # Compare next player
        if self.next_player_ != other.next_player_:
            return False
        return True

    def __str__(self):

        st = f"Player: {self.next_player_}\n"

        # PRINT MATRIX
        r = len(self.matrix)
        c = len(self.matrix[0])

        st += "  " + "   ".join(map(str, range(c))) + "  \n"
        h_line = "+" + "---+" * c + "\n"
        st += h_line

        for i in range(r):
            st += "|"
            for j in range(c):
                if self.matrix[i][j] == Connect4Position.EMPTY_CELL:
                    st += "   |"
                else:
                    st += f" {self.matrix[i][j]} |"
            st += "\n"
            st += h_line


        return st

    def short_str(self):
        st = str(self.next_player_) + "|"
        for c in range(self.n_columns()):
            for r in range(self.n_rows()-1, -1, -1):
                if self.matrix[r][c] == Connect4Position.EMPTY_CELL:
                    break
                st += str(self.matrix[r][c])
            st += "|"
        return st

    def __hash__(self):
        return hash(self.short_str())


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

    def __init__(
            self,
            initial_player: PlayerIndex = PlayerIndex.FirstPlayer,
            initial_matrix: List[List[int]] = None,
            initial_matrix_file: str = None):
        """
        Args:
            initial_matrix: The initial matrix of the game.
            initial_matrix_file: The file with the initial matrix.
        """
        if not initial_matrix and not initial_matrix_file:
            # Use default initial matrix
            self.initial_matrix = [
                [Connect4Position.EMPTY_CELL for _ in range(7)] for _ in range(6)]
        elif initial_matrix:
            self.initial_matrix = initial_matrix
        else:
            self.initial_matrix = Connect4Position.read_file(initial_matrix_file)

        self.initial_player = initial_player
        self.n_rows = len(self.initial_matrix)
        self.n_cols = len(self.initial_matrix[0])

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
        return Connect4Position(
            self,
            self.initial_matrix,
            PlayerIndex.FirstPlayer)

    @override
    def next_position(
            self,
            movement: Connect4Movement,
            position: Connect4Position) -> Connect4Position:

        # Check if the movement is valid
        if movement.n < 0 or movement.n >= self.n_cols:
            raise Exception(f"Invalid movement: invalid column: {movement.n}")
        # Check if the column is not full
        if position.matrix[0][movement.n] != Connect4Position.EMPTY_CELL:
            raise Exception(f"Invalid movement: full column: {movement.n}")

        # Copy matrix
        matrix = copy.deepcopy(position.matrix)

        # Find the first empty cell in the column
        i = self.n_rows - 1
        while i >= 0 and matrix[i][movement.n] != Connect4Position.EMPTY_CELL:
            i -= 1

        matrix[i][movement.n] = position.next_player()

        return Connect4Position(
            self,
            matrix,
            two_player_game_change_player(position.next_player()))


    @override
    def possible_movements(
            self,
            position: Connect4Position) -> Iterator[Connect4Movement]:
        # Check if the column is not full
        movements = []
        for i in range(self.n_cols):
            if position.matrix[0][i] == Connect4Position.EMPTY_CELL:
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
        for r in range(self.n_rows):
            for c in range(self.n_cols):
                if position.matrix[r][c] == Connect4Position.EMPTY_CELL:
                    continue
                player = position.matrix[r][c]
                # Check horizontal
                if c + 3 < self.n_cols and all(position.matrix[r][c + i] == player for i in range(4)):
                    return player
                # Check vertical
                if r + 3 < self.n_rows and all(position.matrix[r + i][c] == player for i in range(4)):
                    return player
                # Check diagonal (down-right)
                if r + 3 < self.n_rows and c + 3 < self.n_cols and all(position.matrix[r + i][c + i] == player for i in range(4)):
                    return player
                # Check diagonal (down-left)
                if r + 3 < self.n_rows and c - 3 >= 0 and all(position.matrix[r + i][c - i] == player for i in range(4)):
                    return player

        # If the board is full, return a draw
        if all(position.matrix[r][c] != Connect4Position.EMPTY_CELL for r in range(self.n_rows) for c in range(self.n_cols)):
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
