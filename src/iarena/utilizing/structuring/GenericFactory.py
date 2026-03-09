"""Declares a generic constructor factory registry."""

from __future__ import annotations

from abc import ABC
from collections.abc import Callable
from typing import Any, TypeVar

from iarena.utilizing.structuring.GenericRegistry import GenericRegistry

T = TypeVar("T")


class GenericFactory(GenericRegistry[Callable[..., T]], ABC):
    """Factory registry that stores constructors and creates instances by name.

    Purpose:
        Provides the `GenericFactory` type within the IArena architecture.
    How it works:
        Encapsulates behavior through its public API and type contracts defined in this class body.
    Used for:
        Building game, mapping, utility, or protocol components that can be composed by other modules.
    Public Attributes:
        None declared at class level in this base definition.
    """

    def register_constructor(
        self,
        constructor: Callable[..., T],
        name: str,
        aliases: list[str] | None = None,
        overwrite: bool = False,
    ) -> None:
        """Register a constructor under one name and optional aliases.

        What it does:
            Implements `register_constructor` as part of the public behavior of its declaring class.
        How it works:
            Executes the operation according to the class contract and delegates detailed logic to the implementation.
        Args:
            constructor (Callable[..., T]): Input consumed by this operation.
            name (str): Input consumed by this operation.
            aliases (List[str] | None, optional): Input consumed by this operation.
            overwrite (bool, optional): Input consumed by this operation.
        Returns:
            None: Performs side effects or state changes without returning a value.
        """
        self.register(obj=constructor, name=name, aliases=aliases, overwrite=overwrite)

    def construct(self, name: str, **kwargs: Any) -> T:
        """Construct and return an instance using the constructor bound to name.

        What it does:
            Implements `construct` as part of the public behavior of its declaring class.
        How it works:
            Executes the operation according to the class contract and delegates detailed logic to the implementation.
        Args:
            name (str): Input consumed by this operation.
            **kwargs (Any): Input consumed by this operation.
        Returns:
            T: Result produced after executing the method contract.
        """
        constructor = self.get(name)
        if constructor is None:
            raise KeyError(f"Unknown constructor '{name}'.")
        return constructor(**kwargs)
