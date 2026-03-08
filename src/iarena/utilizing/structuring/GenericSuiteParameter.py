"""Declares a suite wrapper for parameter combination expansion."""

from __future__ import annotations

from collections.abc import Iterator, Mapping, Sequence
from itertools import product
from typing import Any, Generic, TypeVar

from .GenericParameter import GenericParameter

ParameterType = TypeVar("ParameterType", bound=GenericParameter)


class GenericSuiteParameter(Generic[ParameterType]):  # noqa: UP046
    """Suite wrapper that expands fixed and list-based inputs into concrete parameter instances.

    Purpose:
        Provides the `GenericSuiteParameter` type within the IArena architecture.
    How it works:
        Encapsulates behavior through its public API and type contracts defined in this class body.
    Used for:
        Building game, mapping, utility, or protocol components that can be composed by other modules.
    Public Attributes:
        parameter_cls (type[ParameterType]): Public attribute exposed by this class.
        fixed_values (dict[str, Any]): Public attribute exposed by this class.
        suite_values (dict[str, List[Any]]): Public attribute exposed by this class.
    """

    parameter_cls: type[ParameterType]
    fixed_values: dict[str, Any]
    suite_values: dict[str, list[Any]]

    def __init__(
        self,
        parameter_cls: type[ParameterType],
        fixed_values: Mapping[str, Any],
        suite_values: Mapping[str, Sequence[Any]],
    ) -> None:
        """Store the target parameter class and the parsed fixed/suite values.

        What it does:
            Implements `__init__` as part of the public behavior of its declaring class.
        How it works:
            Executes the operation according to the class contract and delegates detailed logic to the implementation.
        Args:
            parameter_cls (type[ParameterType]): Input consumed by this operation.
            fixed_values (Mapping[str, Any]): Input consumed by this operation.
            suite_values (Mapping[str, Sequence[Any]]): Input consumed by this operation.
        Returns:
            None: Performs side effects or state changes without returning a value.
        """
        self.parameter_cls = parameter_cls
        self.fixed_values = dict(fixed_values)
        self.suite_values = {key: list(values) for key, values in suite_values.items()}

    @classmethod
    def from_dict(
        cls,
        parameter_cls: type[ParameterType],
        src: Mapping[str, Any],
        *,
        suite_prefix: str = "suite:",
        treat_plain_lists_as_suite: bool = True,
    ) -> GenericSuiteParameter[ParameterType] | ParameterType:
        """Parse a source map into either one parameter instance or a suite wrapper.

        What it does:
            Implements `from_dict` as part of the public behavior of its declaring class.
        How it works:
            Executes the operation according to the class contract and delegates detailed logic to the implementation.
        Args:
            parameter_cls (type[ParameterType]): Input consumed by this operation.
            src (Mapping[str, Any]): Input consumed by this operation.
            suite_prefix (str, optional): Input consumed by this operation.
            treat_plain_lists_as_suite (bool, optional): Input consumed by this operation.
        Returns:
            GenericSuiteParameter[ParameterType] | ParameterType: Result produced after executing the method contract.
        """
        fixed_values: dict[str, Any] = {}
        suite_values: dict[str, list[Any]] = {}

        for raw_key, raw_value in src.items():
            if raw_key.startswith(suite_prefix):
                key = raw_key[len(suite_prefix) :]
                suite_values[key] = cls._as_suite_values(raw_value)
                continue

            if treat_plain_lists_as_suite and isinstance(raw_value, list):
                suite_values[raw_key] = list(raw_value)
                continue

            fixed_values[raw_key] = raw_value

        if not suite_values:
            return parameter_cls.from_dict(dict(fixed_values))

        return cls(parameter_cls=parameter_cls, fixed_values=fixed_values, suite_values=suite_values)

    def to_dict(self, target_format: str | None = None) -> dict[str, Any]:
        """Serialize current parameter values to a dictionary.

        What it does:
            Implements `to_dict` as part of the public behavior of its declaring class.
        How it works:
            Executes the operation according to the class contract and delegates detailed logic to the implementation.
        Args:
            target_format (str | None, optional): Input consumed by this operation.
        Returns:
            dict[str, Any]: Result produced after executing the method contract.
        """
        _ = target_format
        serialized = dict(self.fixed_values)
        for key, values in self.suite_values.items():
            serialized[f"suite:{key}"] = list(values)
        return serialized

    def length(self) -> int:
        """Return the number of concrete parameter combinations in the suite.

        What it does:
            Implements `length` as part of the public behavior of its declaring class.
        How it works:
            Executes the operation according to the class contract and delegates detailed logic to the implementation.
        Args:
            None.
        Returns:
            int: Result produced after executing the method contract.
        """
        total = 1
        for values in self.suite_values.values():
            total *= len(values)
        return total

    def individual_parameters(self) -> Iterator[ParameterType]:
        """Yield one concrete parameter instance per suite combination.

        What it does:
            Implements `individual_parameters` as part of the public behavior of its declaring class.
        How it works:
            Executes the operation according to the class contract and delegates detailed logic to the implementation.
        Args:
            None.
        Returns:
            Iterator[ParameterType]: Result produced after executing the method contract.
        """
        if not self.suite_values:
            yield self.parameter_cls.from_dict(dict(self.fixed_values))
            return

        suite_keys = list(self.suite_values.keys())
        suite_domains = [self.suite_values[key] for key in suite_keys]
        for suite_choice in product(*suite_domains):
            params_data = dict(self.fixed_values)
            for key, value in zip(suite_keys, suite_choice, strict=False):
                params_data[key] = value
            yield self.parameter_cls.from_dict(params_data)

    def individual_parameter(self) -> Iterator[ParameterType]:
        """Backward-compatible alias for `individual_parameters`.

        What it does:
            Implements `individual_parameter` as part of the public behavior of its declaring class.
        How it works:
            Executes the operation according to the class contract and delegates detailed logic to the implementation.
        Args:
            None.
        Returns:
            Iterator[ParameterType]: Result produced after executing the method contract.
        """
        return self.individual_parameters()

    @staticmethod
    def _as_suite_values(value: Any) -> list[Any]:
        """Normalize one input value into a list of suite values.

        Args:
            value (Any): Input raw value from source mapping.
        Returns:
            List[Any]: Normalized list of candidate values.
        """
        if isinstance(value, list):
            return list(value)
        if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
            return list(value)
        return [value]
