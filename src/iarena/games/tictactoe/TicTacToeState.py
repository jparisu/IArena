"""TicTacToe game state."""

from iarena.game.GameState import GameState

# Cell value constants
EMPTY: int = 0
PLAYER_X: int = 1  # player index 0
PLAYER_O: int = 2  # player index 1


class TicTacToeState(GameState):
    """Immutable snapshot of a TicTacToe board.

    The board is represented as a 3x3 list of integers where:
    - 0 means empty
    - 1 means Player X (player index 0)
    - 2 means Player O (player index 1)

    Parameters
    ----------
    board:
        3x3 list of int. If None, an empty board is created.
    current_player:
        Index of the player whose turn it is (0 or 1).
    """

    def __init__(
        self,
        board: list[list[int]] | None = None,
        current_player: int = 0,
    ) -> None:
        if current_player not in (0, 1):
            raise ValueError(f"current_player must be 0 or 1, got {current_player}.")
        if board is None:
            self._board: list[list[int]] = [[EMPTY] * 3 for _ in range(3)]
        else:
            if len(board) != 3 or any(len(row) != 3 for row in board):
                raise ValueError("Board must be a 3x3 list.")
            valid_values = {EMPTY, PLAYER_X, PLAYER_O}
            for row in board:
                for cell in row:
                    if cell not in valid_values:
                        raise ValueError(f"Invalid cell value: {cell}. Must be 0, 1, or 2.")
            self._board = [list(row) for row in board]
        self._current_player = current_player

    @property
    def board(self) -> list[list[int]]:
        """Return a copy of the 3x3 board."""
        return [list(row) for row in self._board]

    def current_player_id(self) -> int:
        """Return the index of the active player (0 or 1).

        Returns
        -------
        int
            0 for Player X, 1 for Player O.
        """
        return self._current_player

    def get_cell(self, row: int, col: int) -> int:
        """Return the value of a specific cell.

        Parameters
        ----------
        row:
            Row index in [0, 2].
        col:
            Column index in [0, 2].

        Returns
        -------
        int
            0 (empty), 1 (Player X), or 2 (Player O).
        """
        return self._board[row][col]
