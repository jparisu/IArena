"""Seedable random-number utility with helpers for common operations."""

import random
from collections.abc import MutableSequence, Sequence
from typing import TypeVar

T = TypeVar("T")


class RandomGenerator:
    """Wrap Python's random generator with reproducibility helpers."""

    def __init__(self, seed: int | None = 0) -> None:
        """Initialize a random generator.

        Args:
            seed: Initial seed. If ``None``, a random seed is generated.
        """
        if seed is None:
            seed = random.randint(0, 2**32 - 1)
        self.initial_seed: int = seed
        self.seed: int = seed
        self.rng: random.Random = random.Random(seed)

    def rand(self) -> float:
        """Return a pseudo-random float in the interval ``[0.0, 1.0)``.

        Returns:
            Pseudo-random float in ``[0.0, 1.0)``.
        """
        return self.rng.random()

    def random(self) -> float:
        """Alias for :meth:`rand`.

        Returns:
            Pseudo-random float in ``[0.0, 1.0)``.
        """
        return self.rand()

    def choice(self, seq: Sequence[T]) -> T:
        """Return one random element from a non-empty sequence.

        Args:
            seq: Input sequence.

        Returns:
            Selected element.
        """
        return self.rng.choice(seq)

    def set_seed(self, seed: int, consistent: bool = False) -> None:
        """Set a new seed for the internal generator.

        Args:
            seed: New seed value.
            consistent: Whether to also update the stored seed used for
                consistency tracking.
        """
        if consistent:
            self.seed = seed
        self.rng = random.Random(seed)

    def reset_seed(self) -> None:
        """Reset the generator to the initial seed."""
        self.set_seed(self.initial_seed, consistent=False)

    def shuffle(self, x: MutableSequence[T]) -> None:
        """Shuffle a mutable sequence in place.

        Args:
            x: Sequence to shuffle.
        """
        self.rng.shuffle(x)

    def randint(self, high: int, low: int = 0) -> int:
        """Return a pseudo-random integer in the interval ``[low, high)``.

        Args:
            high: Exclusive upper bound.
            low: Inclusive lower bound.

        Returns:
            Pseudo-random integer in ``[low, high)``.
        """
        return self.rng.randint(low, high - 1)
