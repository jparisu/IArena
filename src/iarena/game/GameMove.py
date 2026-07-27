"""Abstract base classes for game moves."""

from abc import ABC, abstractmethod


class GameMove(ABC):  # noqa: B024
    """Root abstract class representing an action a player can perform.

    A move must be independent of the interface through which it was
    selected. The same GameMove subclass should be usable whether
    the move came from a terminal, a web interface, or an algorithm.
    """

    def __new__(cls, *args: object, **kwargs: object) -> "GameMove":
        """Prevent direct instantiation of the abstract base class."""
        if cls is GameMove:
            raise TypeError("GameMove is an abstract class and cannot be instantiated directly.")
        return super().__new__(cls)


class ParseableGameMove(GameMove):
    """A GameMove that can be constructed from a plain string."""

    @classmethod
    @abstractmethod
    def is_valid_string(cls, s: str) -> bool:
        """Return True if s is a valid string representation of this move.

        Parameters
        ----------
        s:
            Candidate string to validate.
        """

    @classmethod
    @abstractmethod
    def from_string(cls, s: str) -> "ParseableGameMove":
        """Construct and return a move from its string representation.

        Parameters
        ----------
        s:
            A string that satisfies is_valid_string.

        Returns
        -------
        ParseableGameMove
            A new move instance decoded from s.

        Raises
        ------
        ValueError
            If s is not a valid string representation.
        """


class StringifiableGameMove(GameMove):
    """A GameMove that can be serialised to a plain string.

    Implements __str__ via to_string so that str(move) always
    delegates to the concrete serialisation method.
    """

    @abstractmethod
    def to_string(self) -> str:
        """Return the string representation of this move.

        Returns
        -------
        str
            A human-readable or machine-parseable encoding of the move.
        """

    def __str__(self) -> str:
        """Return self.to_string()."""
        return self.to_string()


class ParseableStringifiableGameMove(ParseableGameMove, StringifiableGameMove):
    """A GameMove that supports both parsing from and serialisation to a string.

    Combines ParseableGameMove and StringifiableGameMove for moves that
    must survive a round-trip through string representations.
    """
