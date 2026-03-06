from __future__ import annotations

import logging
import types
from collections.abc import Mapping
from dataclasses import asdict, fields, is_dataclass
from typing import Any, TypeVar, Union, cast, get_args, get_origin, get_type_hints

from iarena.utilizing.structuring.GenericEnumRegistry import GenericEnumRegistry

logger = logging.getLogger(__name__)

T = TypeVar("T", bound="GenericParameter")


class GenericParameter:
    # Dev note: this class intentionally remains non-abstract because it
    # provides shared behavior but currently has no abstract members.
    @classmethod
    def from_dict(cls: type[T], data: dict[str, Any]) -> T:
        """Create an instance and update it from dictionary values."""
        # This assumes the class is a @dataclass
        instance = cls()
        return instance.update_from_dict(data)

    def update_from_dict(self: T, data: Mapping[str, Any]) -> T:
        """Update dataclass fields from key/value input, applying alias resolution."""
        if not is_dataclass(self):
            raise TypeError(f"{type(self).__name__} must be a dataclass to use GenericParameter.")
        try:
            type_hints = get_type_hints(type(self))
        except Exception:  # pragma: no cover - defensive fallback for unresolved annotations
            type_hints = {}

        field_map = {f.name: type_hints.get(f.name, f.type) for f in fields(cast(Any, self))}

        aliases = self.aliases()

        for key, value in data.items():
            # Resolve aliases
            target_key = aliases.get(key, key)

            if target_key in field_map:
                target_type = field_map[target_key]
                setattr(self, target_key, self._convert_value(target_type, value))
            else:
                logger.warning("Key '%s' not recognized in %s", key, type(self).__name__)
        return self

    def _convert_value(self, target_type: Any, value: Any) -> Any:
        if value is None:
            return None

        # Handle Optional/Union types
        origin = get_origin(target_type)
        if origin in (Union, types.UnionType):
            args = get_args(target_type)
            potential_types = [a for a in args if a is not type(None)]
            target_type = potential_types[0] if potential_types else target_type

        # Auto-convert Registry Enums
        if isinstance(target_type, type) and issubclass(target_type, GenericEnumRegistry):
            if isinstance(value, target_type):
                return value
            if isinstance(value, GenericEnumRegistry):
                value = value.value
            return target_type.find(value)

        # Support generic classes exposing ``from_value`` / ``from_string``.
        if isinstance(target_type, type):
            if isinstance(value, target_type):
                return value

            from_value = getattr(target_type, "from_value", None)
            if callable(from_value):
                return from_value(value)

            if isinstance(value, str):
                from_string = getattr(target_type, "from_string", None)
                if callable(from_string):
                    return from_string(value)

        return value

    def to_dict(self, target_format: str | None = None) -> dict[str, Any]:
        """
        Converts the dataclass to a dict.
        If target_format is 'plotly' or 'matplotlib', it resolves Enums automatically.
        """
        if not is_dataclass(self):
            raise TypeError(f"{type(self).__name__} must be a dataclass to use GenericParameter.")
        raw = asdict(cast(Any, self))
        if not target_format:
            return raw

        processed = {}
        for key, value in raw.items():
            # If the field exposes a target serializer, use it.
            actual_member = getattr(self, key)
            method_name = f"to_{target_format}"
            serializer = getattr(actual_member, method_name, None)
            if callable(serializer):
                processed[key] = serializer()
                continue
            processed[key] = value
        return processed

    def set_default_value(self, field_name: str, default_value: Any) -> None:
        """Set a value if the current field value is ``None``."""
        if getattr(self, field_name) is None:
            setattr(self, field_name, default_value)

    @classmethod
    def aliases(cls) -> dict[str, str]:
        """Return a map from input aliases to target field names."""
        return {}

    def copy(self: T) -> T:
        """Return a copy of this parameter instance."""
        return self.__class__.from_dict(self.to_dict())
