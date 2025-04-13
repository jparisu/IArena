
import random
import math
from typing import Tuple

from IArena.interfaces.IPosition import IPosition
from IArena.utils.decorators import override
from IArena.players.minimax_players import MinimaxScoreType, MinimaxRandomConsistentPlayer
from IArena.interfaces.PlayerIndex import PlayerIndex
from IArena.games.Connect4 import Connect4Matrix, Connect4Position
from IArena.games.Nim import NimPosition
from IArena.games.Coins import CoinsPosition


class Connect4HeuristicPlayer(MinimaxRandomConsistentPlayer):

    def __init__(
            self,
            depth: int = -1,
            alpha: MinimaxScoreType = -1,
            beta: MinimaxScoreType = 1,
            seed: int = 0,
            name: str = None,
            possible_rows: int = 16,
            possible_3_rows: int = 24,
            centralize_pieces: int = 1):
        super().__init__(depth=depth, alpha=alpha, beta=beta, seed=seed, name=name)
        self.h_possible_rows = possible_rows
        self.h_possible_3_rows = possible_3_rows
        self.h_centralize_pieces = centralize_pieces


    @override
    def heuristic(self, position: Connect4Position) -> MinimaxScoreType:

        value = 0
        if self.h_possible_rows:
            value += self._count_possible_rows(position) * self.h_possible_rows
        if self.h_possible_3_rows:
            value += self._count_possible_3_rows(position) * self.h_possible_3_rows
        if self.h_centralize_pieces:
            value += self._centralize_pieces(position) * self.h_centralize_pieces

        # We reduce the range of the value as winning and losing is still 1 and -1
        return value / 10e6


    def _centralize_pieces(self, position: Connect4Position) -> int:
        # Initialize variables
        matrix = position.get_matrix()
        n_rows = position.n_rows()
        n_cols = position.n_columns()
        # Initialize counters
        counter_cols = [0,0]
        # Count 1 for each piece, and double for each piece in a more centric column
        for c in range((1+n_cols)//2):
            counter_cols[0] += (c+1)*sum(matrix[r][c] == PlayerIndex.FirstPlayer for r in range(n_rows))
            counter_cols[0] += (c+1)*sum(matrix[r][-1-c] == PlayerIndex.FirstPlayer for r in range(n_rows))
            counter_cols[1] += (c+1)*sum(matrix[r][c] == PlayerIndex.SecondPlayer for r in range(n_rows))
            counter_cols[1] += (c+1)*sum(matrix[r][-1-c] == PlayerIndex.SecondPlayer for r in range(n_rows))

        return counter_cols[0] - counter_cols[1]

    def _count_possible_rows(self, position: Connect4Position) -> int:

        # Initialize variables
        matrix = position.get_matrix()
        n_rows = position.n_rows()
        n_cols = position.n_columns()
        # Initialize counters
        counter_rows = [0,0]

        for r in range(n_rows):
            for c in range(n_cols):
                if matrix[r][c] == Connect4Matrix.EMPTY_CELL:
                    continue
                player = matrix[r][c]
                # Check horizontal
                if c + 3 < n_cols and all(matrix[r][c + i] == player or matrix[r][c + i] == Connect4Matrix.EMPTY_CELL for i in range(4)):
                    counter_rows[player] += 1
                # Check vertical
                if r + 3 < n_rows and all(matrix[r + i][c] == player or matrix[r + i][c] == Connect4Matrix.EMPTY_CELL for i in range(4)):
                    counter_rows[player] += 1
                # Check diagonal (down-right)
                if r + 3 < n_rows and c + 3 < n_cols and all(matrix[r + i][c + i] == player or matrix[r + i][c + i] == Connect4Matrix.EMPTY_CELL for i in range(4)):
                    counter_rows[player] += 1
                # Check diagonal (down-left)
                if r + 3 < n_rows and c - 3 >= 0 and all(matrix[r + i][c - i] == player or matrix[r + i][c - i] == Connect4Matrix.EMPTY_CELL for i in range(4)):
                    counter_rows[player] += 1

        return counter_rows[0] - counter_rows[1]


    def _count_possible_3_rows(self, position: Connect4Position) -> int:

        # Initialize variables
        matrix = position.get_matrix()
        n_rows = position.n_rows()
        n_cols = position.n_columns()
        # Initialize counters
        counter_rows = [0,0]

        for r in range(n_rows):
            for c in range(n_cols):
                if matrix[r][c] == Connect4Matrix.EMPTY_CELL:
                    continue
                player = matrix[r][c]

                # Check horizontal
                if c + 2 < n_cols and all(matrix[r][c + i] == player for i in range(3)):
                    if c - 1 >= 0 and matrix[r][c - 1] == Connect4Matrix.EMPTY_CELL:
                        counter_rows[player] += 1
                    if c + 3 < n_cols and matrix[r][c + 3] == Connect4Matrix.EMPTY_CELL:
                        counter_rows[player] += 1

                # Check vertical
                if r + 2 < n_rows and all(matrix[r + i][c] == player for i in range(3)):
                    if r + 3 < n_rows and matrix[r + 3][c] == Connect4Matrix.EMPTY_CELL:
                        counter_rows[player] += 1

                # Check diagonal (down-right)
                if r + 2 < n_rows and c + 2 < n_cols and all(matrix[r + i][c + i] == player for i in range(3)):
                    if r - 1 >= 0 and c - 1 >= 0 and matrix[r - 1][c - 1] == Connect4Matrix.EMPTY_CELL:
                        counter_rows[player] += 1
                    if r + 3 < n_rows and c + 3 < n_cols and matrix[r + 3][c + 3] == Connect4Matrix.EMPTY_CELL:
                        counter_rows[player] += 1

                # Check diagonal (down-left)
                if r + 2 < n_rows and c - 2 >= 0 and all(matrix[r + i][c - i] == player for i in range(3)):
                    if r - 1 >= 0 and c + 1 < n_cols and matrix[r - 1][c + 1] == Connect4Matrix.EMPTY_CELL:
                        counter_rows[player] += 1
                    if r + 3 < n_rows and c - 3 >= 0 and matrix[r + 3][c - 3] == Connect4Matrix.EMPTY_CELL:
                        counter_rows[player] += 1

        return counter_rows[0] - counter_rows[1]

    # NOTE: NOT IN USE
    # NOTE: TODO fix
    def _central_column(self, position: Connect4Position) -> int:
        # Give positive points if has a piece in the central column
        matrix = position.get_matrix()
        n_rows = position.n_rows()
        n_cols = position.n_columns()
        central_column = n_cols // 2
        return sum(matrix[r][central_column] == 0 for r in range(n_rows))

    # NOTE: NOT IN USE
    def _count_3_rows(self, position: Connect4Position) -> int:

        # Initialize variables
        matrix = position.get_matrix()
        n_rows = position.n_rows()
        n_cols = position.n_columns()
        # Initialize counters
        counter_rows = [0,0]

        for r in range(n_rows):
            for c in range(n_cols):
                if matrix[r][c] == Connect4Matrix.EMPTY_CELL:
                    continue
                player = matrix[r][c]
                # Check horizontal
                if c + 2 < n_cols and all(matrix[r][c + i] == player for i in range(3)):
                    counter_rows[player] += 1
                # Check vertical
                if r + 2 < n_rows and all(matrix[r + i][c] == player for i in range(3)):
                    counter_rows[player] += 1
                # Check diagonal (down-right)
                if r + 2 < n_rows and c + 2 < n_cols and all(matrix[r + i][c + i] == player for i in range(3)):
                    counter_rows[player] += 1
                # Check diagonal (down-left)
                if r + 2 < n_rows and c - 2 >= 0 and all(matrix[r + i][c - i] == player for i in range(3)):
                    counter_rows[player] += 1

        return counter_rows[0] - counter_rows[1]



class NimHeuristicPlayer(MinimaxRandomConsistentPlayer):
    """
    Player 0 is MAX ; Player 1 is MIN
    """

    def __init__(
            self,
            seed: int = 0,
            name: str = None):
        super().__init__(depth=1, alpha=-1, beta=1, seed=seed, name=name)


    @override
    def heuristic(self, position: NimPosition) -> MinimaxScoreType:
        x = self.xor_(position)
        if position.next_player() == PlayerIndex.FirstPlayer:
            if x == 0:
                return -1
            else:
                return 1
        else:
            if x == 0:
                return 1
            else:
                return -1


    def xor_(self, position: NimPosition) -> int:
        xor = 0
        for line in position.lines:
            xor ^= line
        return xor


class CoinsHeuristicPlayer(MinimaxRandomConsistentPlayer):
    """
    This player only works with coin plays where only the last coin has value
    Player 0 is MAX ; Player 1 is MIN
    """

    def __init__(
            self,
            seed: int = 0,
            name: str = None):
        super().__init__(depth=1, seed=seed, name=name)

    @override
    def heuristic(self, position: CoinsPosition) -> MinimaxScoreType:
        rules = position.get_rules()
        c = len(position)
        min_play = rules.min_play()
        max_play = rules.max_play()

        # Check if wins current player or opposite
        c = c % (min_play + max_play)
        wins_next = True
        if c < min_play:
            wins_next = False

        if position.next_player() == PlayerIndex.FirstPlayer:
            if wins_next:
                return 1
            else:
                return -1
        else:
            if wins_next:
                return -1
            else:
                return 1
