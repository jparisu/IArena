"""Declares the concrete Hanoi movement model."""

from iarena.gaming.Movement import Movement


class HanoiMovement(Movement):
    """Concrete Hanoi movement defining source and destination pegs.

    Purpose:
        Represents one legal or candidate movement in a Tower of Hanoi puzzle.
    How it works:
        Stores origin and destination peg indices consumed by rules and renderers.
    Used for:
        Driving state transitions from one `HanoiPosition` to the next.
    Public Attributes:
        from_peg (int): Peg index where the moved disk currently lies.
        to_peg (int): Peg index where the moved disk should be placed.
    """

    from_peg: int
    to_peg: int

    def __init__(self, from_peg: int, to_peg: int) -> None:
        """Create one Hanoi movement from an origin peg to a destination peg.

        Args:
            from_peg: Origin peg index of the moved disk.
            to_peg: Destination peg index of the moved disk.

        Returns:
            None.
        """
        if from_peg < 0:
            raise ValueError("from_peg must be non-negative.")
        if to_peg < 0:
            raise ValueError("to_peg must be non-negative.")
        if from_peg == to_peg:
            raise ValueError("from_peg and to_peg must be different.")
        self.from_peg = from_peg
        self.to_peg = to_peg

    def __str__(self) -> str:
        """Return a user-friendly terminal representation of the movement.

        Returns:
            str: Human-readable peg transition text.
        """
        return f"{self.from_peg} -> {self.to_peg}"

    def __repr__(self) -> str:
        """Return a debug-oriented representation of the movement.

        Returns:
            str: Constructor-like textual representation.
        """
        return f"HanoiMovement(from_peg={self.from_peg}, to_peg={self.to_peg})"
