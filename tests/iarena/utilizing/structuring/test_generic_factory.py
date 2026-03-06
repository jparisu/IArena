import pytest

from iarena.utilizing.structuring.GenericFactory import GenericFactory


class _Factory(GenericFactory[dict]):
    pass


def test_register_and_construct() -> None:
    factory = _Factory()
    factory.register_constructor(dict, name="dict")

    result = factory.construct("dict", a=1)
    assert result == {"a": 1}


def test_construct_unknown_raises_key_error() -> None:
    factory = _Factory()
    with pytest.raises(KeyError):
        factory.construct("missing")


def test_construct_non_callable_raises_type_error() -> None:
    factory = _Factory()
    factory.register({"x": 1}, name="bad")

    with pytest.raises(TypeError):
        factory.construct("bad")
