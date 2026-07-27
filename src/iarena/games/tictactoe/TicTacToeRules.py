"""TicTacToe game rules."""

from collections.abc import Iterator

from iarena.game.GameMove import GameMove
from iarena.game.GameRules import FullGameRules
from iarena.game.GameState import GameState
from iarena.games.tictactoe.TicTacToeConfig import TicTacToeConfig
from iarena.games.tictactoe.TicTacToeMove import TicTacToeMove
from iarena.games.tictactoe.TicTacToeState import TicTacToeState


class TicTacToeRules(FullGameRules):
    """Rules for the standard 3x3 TicTacToe game.

    Two players alternate placing marks (X and O).  The first player
    to occupy three cells in a row, column, or diagonal wins.  If all
    nine cells are filled without a winner the game is a draw.

    Parameters
    ----------
    config:
        A TicTacToeConfig instance (currently has no fields, but is
        required for consistency with the framework).

    Raises
    ------
    TypeError
        If config is not a TicTacToeConfig.
    """

    # Lines that constitute a win: three rows, three cols, two diagonals.
    _WIN_LINES: list[list[tuple[int, int]]] = [
        # Rows
        [(0, 0), (0, 1), (0, 2)],
        [(1, 0), (1, 1), (1, 2)],
        [(2, 0), (2, 1), (2, 2)],
        # Columns
        [(0, 0), (1, 0), (2, 0)],
        [(0, 1), (1, 1), (2, 1)],
        [(0, 2), (1, 2), (2, 2)],
        # Diagonals
        [(0, 0), (1, 1), (2, 2)],
        [(0, 2), (1, 1), (2, 0)],
    ]

    def __init__(self, config: TicTacToeConfig) -> None:
        if not isinstance(config, TicTacToeConfig):
            raise TypeError(f"Expected TicTacToeConfig, got {type(config).__name__}.")
        self._config = config

    def number_of_players(self) -> int:
        """Return 2 (TicTacToe is always a two-player game).

        Returns
        -------
        int
            Always 2.
        """
        return 2

    def first_position(self) -> TicTacToeState:
        """Return the empty starting board with Player X to move.

        Returns
        -------
        TicTacToeState
            A fresh 3x3 board with current_player=0.
        """
        return TicTacToeState()

    def apply_move(self, state: GameState, move: GameMove) -> TicTacToeState:
        """Apply move to state and return the new state.

        Parameters
        ----------
        state:
            Current board position (must be TicTacToeState).
        move:
            The cell to claim (must be TicTacToeMove).

        Returns
        -------
        TicTacToeState
            New state after the move with the next player active.

        Raises
        ------
        TypeError
            If state or move is not the expected type.
        ValueError
            If the move is illegal.
        """
        if not isinstance(state, TicTacToeState):
            raise TypeError(f"Expected TicTacToeState, got {type(state).__name__}.")
        if not isinstance(move, TicTacToeMove):
            raise TypeError(f"Expected TicTacToeMove, got {type(move).__name__}.")
        if not self.is_legal(state, move):
            raise ValueError(f"Illegal move {move} in current state.")
        new_board = state.board
        player_value = state.current_player_id() + 1  # 0 -> PLAYER_X=1, 1 -> PLAYER_O=2
        new_board[move.row][move.col] = player_value
        next_player = 1 - state.current_player_id()
        return TicTacToeState(board=new_board, current_player=next_player)

    def _winner(self, state: TicTacToeState) -> int | None:
        """Return the cell value (1 or 2) of the winner, or None."""
        board = state.board
        for line in self._WIN_LINES:
            values = [board[r][c] for r, c in line]
            if values[0] != 0 and values[0] == values[1] == values[2]:
                return values[0]
        return None

    def is_terminal(self, state: GameState) -> bool:
        """Return True if the game has ended.

        A game ends when one player has three in a row/column/diagonal
        or when all nine cells are filled.

        Parameters
        ----------
        state:
            Board to evaluate.

        Returns
        -------
        bool
            True if the game is over.
        """
        assert isinstance(state, TicTacToeState)
        if self._winner(state) is not None:
            return True
        # Draw: all cells filled
        board = state.board
        return all(board[r][c] != 0 for r in range(3) for c in range(3))

    def result(self, state: GameState) -> int | None:
        """Return the winner player index, or None for a draw.

        Parameters
        ----------
        state:
            A terminal game state.

        Returns
        -------
        int | None
            0 if Player X won, 1 if Player O won, None for a draw.
        """
        assert isinstance(state, TicTacToeState)
        winner_value = self._winner(state)
        if winner_value is None:
            return None
        return winner_value - 1  # PLAYER_X=1 -> 0, PLAYER_O=2 -> 1

    def is_legal(self, state: GameState, move: GameMove) -> bool:
        """Return True if move is legal in state.

        A move is legal if it targets an empty cell and the game is
        not yet over.

        Parameters
        ----------
        state:
            Current board position.
        move:
            Candidate move.

        Returns
        -------
        bool
            True if the move is legal.
        """
        assert isinstance(state, TicTacToeState)
        assert isinstance(move, TicTacToeMove)
        if self.is_terminal(state):
            return False
        return state.get_cell(move.row, move.col) == 0

    def legal_moves(self, state: GameState) -> Iterator[TicTacToeMove]:
        """Yield all legal moves for the current position.

        Parameters
        ----------
        state:
            Current board position.

        Yields
        ------
        TicTacToeMove
            Each empty cell as a TicTacToeMove.
        """
        assert isinstance(state, TicTacToeState)
        if self.is_terminal(state):
            return
        for row in range(3):
            for col in range(3):
                if state.get_cell(row, col) == 0:
                    yield TicTacToeMove(row, col)
