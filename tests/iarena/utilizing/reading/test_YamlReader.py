"""Tests for YAML reading helpers in the utilizing.reading package."""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from iarena.utilizing.reading.YamlReader import YamlReader
from iarena.utilizing.structuring.GenericParameter import GenericParameter
from iarena.utilizing.structuring.GenericSuiteParameter import GenericSuiteParameter


@dataclass
class _Params(GenericParameter):
    n_pegs: int = 3
    disks: list[int] | None = None


def test_read_returns_mapping_from_yaml_file(tmp_path) -> None:
    yaml_path = tmp_path / "conf.yaml"
    yaml_path.write_text("n_pegs: 4\ndisks: [0, 0, 0]\n", encoding="utf-8")

    payload = YamlReader.read(yaml_path)

    assert payload == {"n_pegs": 4, "disks": [0, 0, 0]}


def test_read_parameter_builds_generic_parameter_instance(tmp_path) -> None:
    yaml_path = tmp_path / "conf.yaml"
    yaml_path.write_text("n_pegs: '5'\ndisks: [0, 0]\n", encoding="utf-8")

    params = YamlReader.read_parameter(yaml_path, _Params)

    assert isinstance(params, _Params)
    assert params.n_pegs == 5
    assert params.disks == [0, 0]


def test_read_parameter_or_suite_builds_suite_when_suite_values_present(tmp_path) -> None:
    yaml_path = tmp_path / "suite.yaml"
    yaml_path.write_text("suite:n_pegs: [3, 4]\ndisks: [0, 0]\n", encoding="utf-8")

    params_or_suite = YamlReader.read_parameter_or_suite(
        yaml_path,
        _Params,
        treat_plain_lists_as_suite=False,
    )

    assert isinstance(params_or_suite, GenericSuiteParameter)
    assert params_or_suite.length() == 2


def test_read_mapping_rejects_non_mapping_yaml_root(tmp_path) -> None:
    yaml_path = tmp_path / "items.yaml"
    yaml_path.write_text("- a\n- b\n", encoding="utf-8")

    with pytest.raises(TypeError, match="must be a mapping"):
        YamlReader.read_mapping(yaml_path)


def test_read_raises_value_error_for_invalid_yaml(tmp_path) -> None:
    yaml_path = tmp_path / "broken.yaml"
    yaml_path.write_text("bad: [1, 2\n", encoding="utf-8")

    with pytest.raises(ValueError, match="Invalid YAML"):
        YamlReader.read(yaml_path)
