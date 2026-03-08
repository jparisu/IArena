from __future__ import annotations

from dataclasses import dataclass

from iarena.utilizing.structuring.GenericParameter import GenericParameter
from iarena.utilizing.structuring.GenericSuiteParameter import GenericSuiteParameter


@dataclass
class _Params(GenericParameter):
    a: int = 0
    b: str = ""


class _Suite(GenericSuiteParameter[_Params]):
    pass


def test_init_stores_parameter_class_and_values() -> None:
    suite = _Suite(parameter_cls=_Params, fixed_values={"a": 1}, suite_values={"b": ["x", "y"]})
    assert suite.parameter_cls is _Params
    assert suite.fixed_values == {"a": 1}
    assert suite.suite_values == {"b": ["x", "y"]}


def test_from_dict_returns_suite_when_suite_values_are_present() -> None:
    result = _Suite.from_dict(_Params, {"a": 1, "suite:b": ["x", "y"]})
    assert isinstance(result, _Suite)


def test_from_dict_returns_single_parameter_when_no_suite_values() -> None:
    result = _Suite.from_dict(_Params, {"a": 3, "b": "z"})
    assert isinstance(result, _Params)


def test_to_dict_serializes_fixed_and_suite_values() -> None:
    suite = _Suite(parameter_cls=_Params, fixed_values={"a": 1}, suite_values={"b": ["x", "y"]})
    assert suite.to_dict() == {"a": 1, "suite:b": ["x", "y"]}


def test_length_returns_number_of_combinations() -> None:
    suite = _Suite(parameter_cls=_Params, fixed_values={"a": 1}, suite_values={"b": ["x", "y", "z"]})
    assert suite.length() == 3


def test_individual_parameters_yields_each_parameter_combination() -> None:
    suite = _Suite(parameter_cls=_Params, fixed_values={"a": 1}, suite_values={"b": ["x", "y"]})
    params = list(suite.individual_parameters())
    assert len(params) == 2
    assert {p.b for p in params} == {"x", "y"}
    assert all(p.a == 1 for p in params)


def test_individual_parameter_is_backward_compatible_alias() -> None:
    suite = _Suite(parameter_cls=_Params, fixed_values={"a": 2}, suite_values={"b": ["left", "right"]})
    assert list(suite.individual_parameter()) == list(suite.individual_parameters())
