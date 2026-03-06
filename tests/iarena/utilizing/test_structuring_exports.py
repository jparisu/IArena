from dataclasses import dataclass

from iarena.utilizing import (
    Color,
    Factory,
    GenericEnumRegistry,
    GenericFactory,
    GenericParameter,
    GenericRegistry,
    GenericSingleton,
)


def test_structuring_symbols_exported_from_utilizing() -> None:
    assert Factory is not None
    assert issubclass(GenericEnumRegistry, object)
    assert issubclass(GenericFactory, GenericRegistry)
    assert issubclass(GenericParameter, object)
    assert issubclass(GenericSingleton, object)


@dataclass
class _Params(GenericParameter):
    color: Color | None = None


def test_color_is_converted_via_generic_parameter() -> None:
    params = _Params.from_dict({"color": (255, 0, 128)})
    assert params.color == "#ff0080"
    assert isinstance(params.color, Color)
