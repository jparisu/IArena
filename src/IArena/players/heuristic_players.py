
import random
import math
from typing import Tuple

from IArena.interfaces.IPosition import IPosition
from IArena.utils.decorators import override
from IArena.players.minimax_players import MinimaxScoreType, MinimaxRandomConsistentPlayer
from IArena.interfaces.PlayerIndex import PlayerIndex
from IArena.games.Connect4 import Connect4Matrix

class Connect4HeuristicPlayer(MinimaxRandomConsistentPlayer):

    def __init__(
            self,
            player: PlayerIndex = None,
            depth: int = -1,
            alpha: MinimaxScoreType = -1,
            beta: MinimaxScoreType = 1,
            seed: int = 0,
            name: str = None,
            possible_rows: int = 16,
            possible_3_rows: int = 24,
            centralize_pieces: int = 1):
        super().__init__(player=player, depth=depth, alpha=alpha, beta=beta, seed=seed, name=name)
        self.h_possible_rows = possible_rows
        self.h_possible_3_rows = possible_3_rows
        self.h_centralize_pieces = centralize_pieces


    @override
    def heuristic(self, position: IPosition) -> MinimaxScoreType:

        value = 0
        if self.h_possible_rows:
            value += self._count_possible_rows(position) * self.h_possible_rows
        if self.h_possible_3_rows:
            value += self._count_possible_3_rows(position) * self.h_possible_3_rows
        if self.h_centralize_pieces:
            value += self._centralize_pieces(position) * self.h_centralize_pieces

        # We reduce the range of the value as winning and losing is still 1 and -1
        return value / 10e6


    def _centralize_pieces(self, position: IPosition) -> int:
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

        return counter_cols[self.player] - counter_cols[not self.player]

    def _count_possible_rows(self, position: IPosition) -> int:

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

        return counter_rows[self.player] - counter_rows[not self.player]


    def _count_possible_3_rows(self, position: IPosition) -> int:

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

        return counter_rows[self.player] - counter_rows[not self.player]

    # NOT IN USE
    def _central_column(self, position: IPosition) -> int:
        # Give positive points if has a piece in the central column
        matrix = position.get_matrix()
        n_rows = position.n_rows()
        n_cols = position.n_columns()
        central_column = n_cols // 2
        return sum(matrix[r][central_column] == self.player for r in range(n_rows))

    # NOT IN USE
    def _count_3_rows(self, position: IPosition) -> int:

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

        return counter_rows[self.player] - counter_rows[not self.player]
