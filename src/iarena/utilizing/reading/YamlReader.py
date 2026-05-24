"""Defines YAML reading helpers for raw mappings and typed parameter objects."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any, TypeVar

import yaml

from iarena.utilizing.structuring.GenericParameter import GenericParameter
from iarena.utilizing.structuring.GenericSuiteParameter import GenericSuiteParameter

ParameterType = TypeVar("ParameterType", bound=GenericParameter)


class YamlReader:
    """YAML reading utility for plain data and typed parameter models.

    Purpose:
        Centralize YAML file parsing and conversion into IArena parameter
        abstractions.
    How it works:
        Uses `yaml.safe_load` and delegates typed object creation to
        `GenericParameter`/`GenericSuiteParameter` constructors.
    Used for:
        CLI/app configuration loading and file-driven setup workflows.
    Public Attributes:
        None declared at class level in this base definition.
    """

    @classmethod
    def read(cls, path: str | Path) -> Any:
        """Read and parse one YAML file.

        Args:
            path: Path to the source YAML file.

        Returns:
            Any: Parsed YAML payload. Empty files return an empty dictionary.

        Raises:
            ValueError: If the file cannot be parsed as valid YAML.
        """
        _ = cls
        normalized_path = Path(path)
        content = normalized_path.read_text(encoding="utf-8")
        if not content.strip():
            return {}

        try:
            parsed = yaml.safe_load(content)
        except yaml.YAMLError as exc:
            raise ValueError(f"Invalid YAML content in '{normalized_path}'.") from exc

        return {} if parsed is None else parsed

    @classmethod
    def read_mapping(cls, path: str | Path) -> Mapping[str, Any]:
        """Read a YAML file and ensure it is a mapping payload.

        Args:
            path: Path to the source YAML file.

        Returns:
            Mapping[str, Any]: Parsed mapping data.

        Raises:
            TypeError: If parsed YAML is not a mapping.
        """
        payload = cls.read(path)
        if not isinstance(payload, Mapping):
            raise TypeError("YAML root content must be a mapping/object.")
        return payload

    @classmethod
    def read_parameter(cls, path: str | Path, parameter_cls: type[ParameterType]) -> ParameterType:
        """Read one YAML file and build a concrete parameter instance.

        Args:
            path: Path to the source YAML file.
            parameter_cls: Parameter class used to build the result.

        Returns:
            ParameterType: Parameter object created from YAML mapping data.
        """
        payload = cls.read_mapping(path)
        return parameter_cls.from_dict(dict(payload))

    @classmethod
    def read_parameter_or_suite(
        cls,
        path: str | Path,
        parameter_cls: type[ParameterType],
        *,
        suite_prefix: str = "suite:",
        treat_plain_lists_as_suite: bool = True,
    ) -> GenericSuiteParameter[ParameterType] | ParameterType:
        """Read one YAML file as a parameter or parameter-suite definition.

        Args:
            path: Path to the source YAML file.
            parameter_cls: Parameter class used for conversion.
            suite_prefix: Prefix used to identify suite fields.
            treat_plain_lists_as_suite: Whether plain list fields are treated as
                suite dimensions.

        Returns:
            GenericSuiteParameter[ParameterType] | ParameterType:
                Parsed concrete parameter or suite wrapper.
        """
        payload = cls.read_mapping(path)
        return GenericSuiteParameter.from_dict(
            parameter_cls=parameter_cls,
            src=payload,
            suite_prefix=suite_prefix,
            treat_plain_lists_as_suite=treat_plain_lists_as_suite,
        )
