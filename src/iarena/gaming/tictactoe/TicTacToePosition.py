"""Declares the concrete TicTacToe position model."""

from __future__ import annotations

from typing import TYPE_CHECKING

from iarena.gaming.Position import Position
from iarena.playing.PlayerIndex import PlayerIndex

if TYPE_CHECKING:
    from iarena.gaming.Rules import Rules
    from iarena.gaming.tictactoe.TicTacToeRules import TicTacToeRules


class TicTacToePosition(Position):
    """Concrete TicTacToe position containing board cells and current player.

    Purpose:
        Models one TicTacToe board state including played cells and turn ownership.
    How it works:
        Carries immutable-like game-state fields and exposes the `Position` API.
    Used for:
        Rules evaluation, player decision making, and renderer output in TicTacToe matches.
    Public Attributes:
        board_size (int): Side size of the square board.
        win_length (int): Number of aligned symbols required to win.
        cells (list[int | None]): Flat board values (`0`, `1`, or `None`) in row-major order.
        turn (int): Number of executed movements from the initial position.
        current_player (PlayerIndex): Player expected to act next.
    """

    board_size: int
    win_length: int
    cells: list[int | None]
    turn: int
    current_player: PlayerIndex

    def __init__(
        self,
        board_size: int,
        win_length: int,
        cells: list[int | None] | None = None,
        turn: int = 0,
        current_player: PlayerIndex | None = None,
    ) -> None:
        """Create one TicTacToe position with explicit board data.

        Args:
            board_size: Side size of the square board.
            win_length: Number of aligned symbols required to win.
            cells: Optional flat cell list in row-major order.
            turn: Number of movements already executed.
            current_player: Player expected to act next.

        Returns:
            None.
        """
        if board_size < 1:
            raise ValueError("board_size must be at least 1.")
        if win_length < 1:
            raise ValueError("win_length must be at least 1.")
        if win_length > board_size:
            raise ValueError("win_length must be less than or equal to board_size.")
        if turn < 0:
            raise ValueError("turn must be non-negative.")
        if current_player is None:
            current_player = PlayerIndex(0)
        if current_player not in (PlayerIndex(0), PlayerIndex(1)):
            raise ValueError("current_player must be either PlayerIndex(0) or PlayerIndex(1).")

        if cells is None:
            normalized_cells: list[int | None] = [None] * (board_size * board_size)
        else:
            if len(cells) != board_size * board_size:
                raise ValueError("cells length must be board_size * board_size.")
            if any(cell not in (None, 0, 1) for cell in cells):
                raise ValueError("cells may only contain None, 0, or 1.")
            normalized_cells = list(cells)

        self.board_size = board_size
        self.win_length = win_length
        self.cells = normalized_cells
        self.turn = turn
        self.current_player = PlayerIndex(int(current_player))
        self._rules: TicTacToeRules | None = None

    def hash(self) -> int:
        """Return a stable hash representation for this position.

        Returns:
            int: Deterministic integer hash for the current board state.
        """
        return hash(
            (
                self.board_size,
                self.win_length,
                tuple(self.cells),
                self.turn,
                int(self.current_player),
            ),
        )

    def __str__(self) -> str:
        """Return a compact textual representation of this TicTacToe position.

        Returns:
            str: Human-readable state summary.
        """
        return (
            "TicTacToePosition("
            f"size={self.board_size}, "
            f"win_length={self.win_length}, "
            f"turn={self.turn}, "
            f"current_player={int(self.current_player)}, "
            f"cells={self.cells}"
            ")"
        )

    def next_player(self) -> PlayerIndex:
        """Return the next player that must act from this position.

        Returns:
            PlayerIndex: Identifier of the player expected to play next.
        """
        return self.current_player

    def get_rules(self) -> Rules:
        """Return the rules object associated with this position.

        Returns:
            Rules: Rules instance that can validate and evolve this position.
        """
        if self._rules is None:
            from iarena.gaming.tictactoe.TicTacToeConfiguration import TicTacToeConfiguration
            from iarena.gaming.tictactoe.TicTacToeRules import TicTacToeRules

            self._rules = TicTacToeRules(
                TicTacToeConfiguration(
                    board_size=self.board_size,
                    win_length=self.win_length,
                ),
            )
        return self._rules
