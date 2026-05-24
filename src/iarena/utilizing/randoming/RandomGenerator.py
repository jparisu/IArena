"""Declares a reproducible random generator abstraction."""

from __future__ import annotations

import random
from collections.abc import MutableSequence, Sequence
from typing import TypeVar

T = TypeVar("T")


class RandomGenerator:
    """Random generator abstraction used to centralize reproducible randomness.

    Purpose:
        Provides the `RandomGenerator` type within the IArena architecture.
    How it works:
        Encapsulates behavior through its public API and type contracts defined in this class body.
    Used for:
        Building game, mapping, utility, or protocol components that can be composed by other modules.
    Public Attributes:
        None declared at class level in this base definition.
    """

    def __init__(self, seed: int | None = 0) -> None:
        """Initialize the random generator with an optional seed.

        What it does:
            Implements `__init__` as part of the public behavior of its declaring class.
        How it works:
            Executes the operation according to the class contract and delegates detailed logic to the implementation.
        Args:
            seed (int | None, optional): Input consumed by this operation.
        Returns:
            None: Performs side effects or state changes without returning a value.
        """
        self._initial_seed = seed
        self._seed = seed
        self._rng = random.Random(seed)

    def rand(self) -> float:
        """Return a pseudo-random floating-point number in [0, 1).

        What it does:
            Implements `rand` as part of the public behavior of its declaring class.
        How it works:
            Executes the operation according to the class contract and delegates detailed logic to the implementation.
        Args:
            None.
        Returns:
            float: Result produced after executing the method contract.
        """
        return self._rng.random()

    def random(self) -> float:
        """Return a pseudo-random floating-point number in [0, 1).

        What it does:
            Implements `random` as part of the public behavior of its declaring class.
        How it works:
            Executes the operation according to the class contract and delegates detailed logic to the implementation.
        Args:
            None.
        Returns:
            float: Result produced after executing the method contract.
        """
        return self.rand()

    def choice(self, seq: Sequence[T]) -> T:
        """Return one random element selected from a non-empty sequence.

        What it does:
            Implements `choice` as part of the public behavior of its declaring class.
        How it works:
            Executes the operation according to the class contract and delegates detailed logic to the implementation.
        Args:
            seq (Sequence[T]): Input consumed by this operation.
        Returns:
            T: Result produced after executing the method contract.
        """
        if not seq:
            raise ValueError("Sequence is empty.")
        return self._rng.choice(seq)

    def set_seed(self, seed: int, consistent: bool = False) -> None:
        """Set the generator seed and optionally update consistency tracking.

        What it does:
            Implements `set_seed` as part of the public behavior of its declaring class.
        How it works:
            Executes the operation according to the class contract and delegates detailed logic to the implementation.
        Args:
            seed (int): Input consumed by this operation.
            consistent (bool, optional): Input consumed by this operation.
        Returns:
            None: Performs side effects or state changes without returning a value.
        """
        self._seed = seed
        if consistent:
            self._initial_seed = seed
        self._rng.seed(seed)

    def reset_seed(self) -> None:
        """Reset the generator to its initial seed value.

        What it does:
            Implements `reset_seed` as part of the public behavior of its declaring class.
        How it works:
            Executes the operation according to the class contract and delegates detailed logic to the implementation.
        Args:
            None.
        Returns:
            None: Performs side effects or state changes without returning a value.
        """
        self._seed = self._initial_seed
        self._rng.seed(self._initial_seed)

    def shuffle(self, x: MutableSequence[T]) -> None:
        """Shuffle a mutable sequence in-place using this generator.

        What it does:
            Implements `shuffle` as part of the public behavior of its declaring class.
        How it works:
            Executes the operation according to the class contract and delegates detailed logic to the implementation.
        Args:
            x (MutableSequence[T]): Input consumed by this operation.
        Returns:
            None: Performs side effects or state changes without returning a value.
        """
        self._rng.shuffle(x)

    def randint(self, high: int, low: int = 0) -> int:
        """Return a pseudo-random integer sampled from [low, high).

        What it does:
            Implements `randint` as part of the public behavior of its declaring class.
        How it works:
            Executes the operation according to the class contract and delegates detailed logic to the implementation.
        Args:
            high (int): Input consumed by this operation.
            low (int, optional): Input consumed by this operation.
        Returns:
            int: Result produced after executing the method contract.
        """
        if high <= low:
            raise ValueError("`high` must be greater than `low`.")
        return self._rng.randrange(low, high)
