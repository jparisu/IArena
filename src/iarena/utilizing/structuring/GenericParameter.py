"""Declares a generic parameter abstraction with serialization intent."""
# pylint: disable=too-many-lines  # TODO: review

from __future__ import annotations

import copy
from collections.abc import Mapping
from dataclasses import asdict, is_dataclass
from types import NoneType, UnionType
from typing import Any, TypeVar, Union, get_args, get_origin, get_type_hints

T = TypeVar("T")


class GenericParameter:
    """Dataclass-oriented parameter base with typed update and serialization helpers.

    Purpose:
        Provides the `GenericParameter` type within the IArena architecture.
    How it works:
        Encapsulates behavior through its public API and type contracts defined in this class body.
    Used for:
        Building game, mapping, utility, or protocol components that can be composed by other modules.
    Public Attributes:
        None declared at class level in this base definition.
    """

    @classmethod
    def from_dict(cls: type[T], data: dict[str, Any]) -> T:
        """Build a parameter instance from a dictionary.

        What it does:
            Implements `from_dict` as part of the public behavior of its declaring class.
        How it works:
            Executes the operation according to the class contract and delegates detailed logic to the implementation.
        Args:
            data (dict[str, Any]): Input consumed by this operation.
        Returns:
            T: Result produced after executing the method contract.
        """
        instance = cls()  # type: ignore[call-arg]
        return instance.update_from_dict(data)

    def update_from_dict(self: T, data: Mapping[str, Any]) -> T:
        """Update current parameter fields from a mapping.

        What it does:
            Implements `update_from_dict` as part of the public behavior of its declaring class.
        How it works:
            Executes the operation according to the class contract and delegates detailed logic to the implementation.
        Args:
            data (Mapping[str, Any]): Input consumed by this operation.
        Returns:
            T: Result produced after executing the method contract.
        """
        aliases = self.aliases()
        type_hints = get_type_hints(type(self))

        for provided_name, value in data.items():
            field_name = aliases.get(provided_name, provided_name)
            if not hasattr(self, field_name):
                continue

            target_type = type_hints.get(field_name, Any)
            converted_value = self._convert_value(target_type=target_type, value=value)
            setattr(self, field_name, converted_value)

        return self

    def _convert_value(self, target_type: Any, value: Any) -> Any:  # pylint: disable=too-complex  # TODO: review
        """Convert one value to its target type with helper hooks.

        What it does:
            Implements `_convert_value` as part of the public behavior of its declaring class.
        How it works:
            Executes the operation according to the class contract and delegates detailed logic to the implementation.
        Args:
            target_type (Any): Input consumed by this operation.
            value (Any): Input consumed by this operation.
        Returns:
            Any: Result produced after executing the method contract.
        """
        if value is None:
            return None

        if target_type in (Any, object):
            return value

        origin = get_origin(target_type)
        args = get_args(target_type)

        if origin is None:
            return self._convert_atomic_value(target_type=target_type, value=value)

        if origin in (Union, UnionType):
            non_none_types = [arg for arg in args if arg is not NoneType]
            if value is None and len(non_none_types) < len(args):
                return None
            for candidate_type in non_none_types:
                try:
                    return self._convert_value(target_type=candidate_type, value=value)
                except (TypeError, ValueError):
                    continue
            return value

        if origin is list and args:
            if not isinstance(value, list):
                return value
            return [self._convert_value(target_type=args[0], value=item) for item in value]

        if origin is tuple and args:
            if not isinstance(value, (tuple, list)):
                return value
            if len(args) == 2 and args[1] is Ellipsis:
                return tuple(self._convert_value(target_type=args[0], value=item) for item in value)
            return tuple(
                self._convert_value(target_type=arg_type, value=item)
                for arg_type, item in zip(args, value, strict=False)
            )

        if origin is dict and len(args) == 2:
            if not isinstance(value, dict):
                return value
            return {
                self._convert_value(target_type=args[0], value=key): self._convert_value(
                    target_type=args[1], value=item_value
                )
                for key, item_value in value.items()
            }

        return value

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
        if is_dataclass(self):
            return asdict(self)
        return {key: value for key, value in vars(self).items() if not key.startswith("_")}

    def set_default_value(self, field_name: str, default_value: Any) -> None:
        """Set a field default only when the field currently holds None.

        What it does:
            Implements `set_default_value` as part of the public behavior of its declaring class.
        How it works:
            Executes the operation according to the class contract and delegates detailed logic to the implementation.
        Args:
            field_name (str): Input consumed by this operation.
            default_value (Any): Input consumed by this operation.
        Returns:
            None: Performs side effects or state changes without returning a value.
        """
        if not hasattr(self, field_name):
            raise AttributeError(f"Unknown field '{field_name}'.")
        if getattr(self, field_name) is None:
            setattr(self, field_name, default_value)

    @classmethod
    def aliases(cls) -> dict[str, str]:
        """Return alias mapping from external keys to field names.

        What it does:
            Implements `aliases` as part of the public behavior of its declaring class.
        How it works:
            Executes the operation according to the class contract and delegates detailed logic to the implementation.
        Args:
            None.
        Returns:
            dict[str, str]: Result produced after executing the method contract.
        """
        return {}

    def copy(self: T) -> T:
        """Return a copied parameter instance.

        What it does:
            Implements `copy` as part of the public behavior of its declaring class.
        How it works:
            Executes the operation according to the class contract and delegates detailed logic to the implementation.
        Args:
            None.
        Returns:
            T: Result produced after executing the method contract.
        """
        return copy.deepcopy(self)

    def _convert_atomic_value(self, target_type: Any, value: Any) -> Any:
        """Convert one scalar-like value to a direct target type.

        Args:
            target_type (Any): Destination type for conversion.
            value (Any): Input value to convert.
        Returns:
            Any: Converted value when possible, otherwise original value.
        """
        if target_type in (Any, object):
            return value

        if isinstance(target_type, type):
            if isinstance(value, target_type):
                return value

            if target_type is bool and isinstance(value, str):
                lowered = value.strip().lower()
                if lowered in {"true", "1", "yes", "on"}:
                    return True
                if lowered in {"false", "0", "no", "off"}:
                    return False
                raise ValueError(f"Cannot convert '{value}' to bool.")

            if issubclass(target_type, GenericParameter) and isinstance(value, dict):
                return target_type.from_dict(value)

            return target_type(value)

        return value
