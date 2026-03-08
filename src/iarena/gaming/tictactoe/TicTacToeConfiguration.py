"""Declares the concrete TicTacToe configuration model."""

from __future__ import annotations

from typing import Any

from iarena.gaming.Configuration import Configuration


class TicTacToeConfiguration(Configuration):
    """Concrete TicTacToe configuration defining board and line dimensions.

    Purpose:
        Encapsulates static parameters required to build a playable TicTacToe ruleset.
    How it works:
        Stores board size and win-length constraints used by `TicTacToeGame.generate_rules`.
    Used for:
        Instantiating reproducible TicTacToe matches with explicit dimensions.
    Public Attributes:
        board_size (int): Side size of the square board.
        win_length (int): Number of aligned symbols required to win.
    """

    board_size: int
    win_length: int

    def __init__(self, board_size: int = 3, win_length: int = 3) -> None:
        """Create one TicTacToe configuration from board parameters.

        Args:
            board_size: Side size of the square board.
            win_length: Number of aligned symbols required to win.

        Returns:
            None.
        """
        if board_size < 1:
            raise ValueError("board_size must be at least 1.")
        if win_length < 1:
            raise ValueError("win_length must be at least 1.")
        if win_length > board_size:
            raise ValueError("win_length must be less than or equal to board_size.")

        self.board_size = board_size
        self.win_length = win_length

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TicTacToeConfiguration:
        """Build one TicTacToe configuration from a dictionary payload.

        Args:
            data: Mapping containing optional `board_size` and `win_length` keys.

        Returns:
            TicTacToeConfiguration: Parsed concrete configuration object.
        """
        board_size = int(data.get("board_size", 3))
        win_length = int(data.get("win_length", board_size))
        return cls(board_size=board_size, win_length=win_length)
