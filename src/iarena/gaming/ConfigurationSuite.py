"""Declares the abstract suite contract for generating game configurations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterator, Mapping
from typing import Any

from iarena.gaming.Configuration import Configuration
from iarena.utilizing.structuring.GenericSuiteParameter import GenericSuiteParameter


class ConfigurationSuite(GenericSuiteParameter[Configuration], ABC):
    """Abstract configuration suite that generates multiple game configurations.

    Purpose:
        Provides the `ConfigurationSuite` type within the IArena architecture.
    How it works:
        Encapsulates behavior through its public API and type contracts defined in this class body.
    Used for:
        Building game, mapping, utility, or protocol components that can be composed by other modules.
    Public Attributes:
        None declared at class level in this base definition.
    """

    @classmethod
    def from_dict(
        cls,
        parameter_cls: type[Configuration],
        src: Mapping[str, Any],
        *,
        suite_prefix: str = "suite:",
        treat_plain_lists_as_suite: bool = True,
    ) -> ConfigurationSuite | Configuration:
        """Parse a dictionary as either one configuration or a suite of configurations.

        What it does:
            Implements `from_dict` as part of the public behavior of its declaring class.
        How it works:
            Executes the operation according to the class contract and delegates detailed logic to the implementation.
        Args:
            parameter_cls (type[Configuration]): Input consumed by this operation.
            src (Mapping[str, Any]): Input consumed by this operation.
            suite_prefix (str, optional): Input consumed by this operation.
            treat_plain_lists_as_suite (bool, optional): Input consumed by this operation.
        Returns:
            'ConfigurationSuite | Configuration': Result produced after executing the method contract.
        """
        # TODO
        raise NotImplementedError("ConfigurationSuite.from_dict is not implemented yet.")

    @abstractmethod
    def generate_configurations(self) -> Iterator[Configuration]:
        """Yield each concrete configuration from the suite product.

        What it does:
            Implements `generate_configurations` as part of the public behavior of its declaring class.
        How it works:
            Executes the operation according to the class contract and delegates detailed logic to the implementation.
        Args:
            None.
        Returns:
            Iterator[Configuration]: Result produced after executing the method contract.
        """
        # TODO
        ...

    @abstractmethod
    def length(self) -> int:
        """Return the number of concrete configurations in the suite.

        What it does:
            Implements `length` as part of the public behavior of its declaring class.
        How it works:
            Executes the operation according to the class contract and delegates detailed logic to the implementation.
        Args:
            None.
        Returns:
            int: Result produced after executing the method contract.
        """
        # TODO
        ...
