"""Factory built on top of :class:`GenericRegistry`."""

from abc import ABC
from typing import Any, Callable, TypeVar

from iarena.utilizing.structuring.GenericRegistry import GenericRegistry

T = TypeVar("T")


class GenericFactory(GenericRegistry[Callable[..., T]], ABC):
    """
    An abstract base class for creating objects.
    Stores constructors/callables and invokes them on demand.
    """

    def register_constructor(
        self, constructor: Callable[..., T], name: str, aliases: list[str] | None = None, overwrite: bool = False
    ) -> None:
        """
        Registers a constructor (class or function) under a primary name and aliases.
        """
        # We reuse the base register method which handles all the alias/overwrite logic
        self.register(obj=constructor, name=name, aliases=aliases, overwrite=overwrite)

    def construct(self, name: str, **kwargs: Any) -> T:
        """
        Retrieves the constructor associated with 'name' and returns a new instance.

        Args:
            name: The primary name or alias of the constructor.
            **kwargs: Arguments to pass to the constructor.

        Returns:
            An instance of type T.

        Raises:
            KeyError: If the name/alias is not registered.
            TypeError: If the registered object is not callable.
        """
        # Use strict=True to ensure we get a KeyError if missing
        constructor = self.get(name, strict=True)

        if not callable(constructor):
            raise TypeError(f"Registered entry '{name}' is not a callable constructor.")

        return constructor(**kwargs)


# Backward compatibility.
Factory = GenericFactory
