"""Declares the concrete TicTacToe movement model."""

from iarena.gaming.Movement import Movement


class TicTacToeMovement(Movement):
    """Concrete TicTacToe movement defining a board cell selection.

    Purpose:
        Represents one move in TicTacToe as a `(row, col)` board coordinate.
    How it works:
        Stores validated zero-based coordinates consumed by rules and renderers.
    Used for:
        Driving state transitions from one `TicTacToePosition` to the next.
    Public Attributes:
        row (int): Row index of the selected board cell.
        col (int): Column index of the selected board cell.
    """

    row: int
    col: int

    def __init__(self, row: int, col: int) -> None:
        """Create one TicTacToe movement from row/column coordinates.

        Args:
            row: Zero-based row index of the selected cell.
            col: Zero-based column index of the selected cell.

        Returns:
            None.
        """
        if row < 0:
            raise ValueError("row must be non-negative.")
        if col < 0:
            raise ValueError("col must be non-negative.")
        self.row = row
        self.col = col

    def __str__(self) -> str:
        """Return a user-friendly terminal representation of the movement.

        Args:
            None.

        Returns:
            str: Human-readable row/column selection.
        """
        return f"({self.row}, {self.col})"

    def __repr__(self) -> str:
        """Return a debug-oriented representation of the movement.

        Args:
            None.

        Returns:
            str: Constructor-like textual representation.
        """
        return f"TicTacToeMovement(row={self.row}, col={self.col})"
