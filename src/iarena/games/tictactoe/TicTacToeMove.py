"""TicTacToe move: a cell selection on the 3x3 board."""

from iarena.game.GameMove import ParseableStringifiableGameMove


class TicTacToeMove(ParseableStringifiableGameMove):
    """A move in TicTacToe: placing a mark on a specific cell.

    Cells are identified by (row, col) with both indices in [0, 2].
    The string representation is ``"row,col"`` (e.g. ``"1,2"``).

    Parameters
    ----------
    row:
        Row index in [0, 2].
    col:
        Column index in [0, 2].

    Raises
    ------
    ValueError
        If row or col is outside [0, 2].
    """

    def __init__(self, row: int, col: int) -> None:
        if not (0 <= row <= 2):
            raise ValueError(f"Row must be in [0, 2], got {row}.")
        if not (0 <= col <= 2):
            raise ValueError(f"Col must be in [0, 2], got {col}.")
        self._row = row
        self._col = col

    @property
    def row(self) -> int:
        """Row index of the selected cell."""
        return self._row

    @property
    def col(self) -> int:
        """Column index of the selected cell."""
        return self._col

    @classmethod
    def is_valid_string(cls, s: str) -> bool:
        """Return True if s is a valid ``"row,col"`` string for TicTacToe.

        Parameters
        ----------
        s:
            Candidate string.

        Returns
        -------
        bool
            True when s can be parsed as a valid cell address.
        """
        parts = s.split(",")
        if len(parts) != 2:
            return False
        try:
            row = int(parts[0])
            col = int(parts[1])
        except ValueError:
            return False
        return 0 <= row <= 2 and 0 <= col <= 2

    @classmethod
    def from_string(cls, s: str) -> "TicTacToeMove":
        """Construct a TicTacToeMove from a ``"row,col"`` string.

        Parameters
        ----------
        s:
            A string satisfying is_valid_string.

        Returns
        -------
        TicTacToeMove
            The corresponding move.

        Raises
        ------
        ValueError
            If s is not a valid move string.
        """
        if not cls.is_valid_string(s):
            raise ValueError(f"Invalid TicTacToeMove string: '{s}'.")
        parts = s.split(",")
        return cls(int(parts[0]), int(parts[1]))

    def to_string(self) -> str:
        """Return the ``"row,col"`` string representation.

        Returns
        -------
        str
            Serialised move.
        """
        return f"{self._row},{self._col}"

    def __eq__(self, other: object) -> bool:
        """Return True if other is a TicTacToeMove with the same cell."""
        if not isinstance(other, TicTacToeMove):
            return NotImplemented
        return self._row == other._row and self._col == other._col

    def __hash__(self) -> int:
        """Return a hash consistent with __eq__."""
        return hash((self._row, self._col))
