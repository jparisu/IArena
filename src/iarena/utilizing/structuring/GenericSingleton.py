"""Declares a generic singleton wrapper type."""

from __future__ import annotations

from typing import Generic, TypeVar

T = TypeVar("T")


class GenericSingleton(Generic[T]):  # noqa: UP046
    """Generic singleton wrapper that lazily creates one instance per class.

    Purpose:
        Provides the `GenericSingleton` type within the IArena architecture.
    How it works:
        Encapsulates behavior through its public API and type contracts defined in this class body.
    Used for:
        Building game, mapping, utility, or protocol components that can be composed by other modules.
    Public Attributes:
        None declared at class level in this base definition.
    """

    def __init__(self, cls: type[T]) -> None:
        """Initialize singleton wrapper for the provided class.

        What it does:
            Implements `__init__` as part of the public behavior of its declaring class.
        How it works:
            Executes the operation according to the class contract and delegates detailed logic to the implementation.
        Args:
            None.
        Returns:
            None: Performs side effects or state changes without returning a value.
        """
        self._cls = cls
        self._instance: T | None = None

    def __call__(self, *args: object, **kwargs: object) -> T:
        """Return the singleton instance, creating it on first invocation.

        What it does:
            Implements `__call__` as part of the public behavior of its declaring class.
        How it works:
            Executes the operation according to the class contract and delegates detailed logic to the implementation.
        Args:
            *args (object): Input consumed by this operation.
            **kwargs (object): Input consumed by this operation.
        Returns:
            T: Result produced after executing the method contract.
        """
        if self._instance is None:
            self._instance = self._cls(*args, **kwargs)
        return self._instance

    def get_instance(self) -> T:
        """Return the singleton instance via explicit getter.

        What it does:
            Implements `get_instance` as part of the public behavior of its declaring class.
        How it works:
            Executes the operation according to the class contract and delegates detailed logic to the implementation.
        Args:
            None.
        Returns:
            T: Result produced after executing the method contract.
        """
        if self._instance is None:
            raise RuntimeError("Singleton instance has not been created yet.")
        return self._instance
