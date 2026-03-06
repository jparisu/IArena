import pytest

from iarena.utilizing.structuring.GenericEnumRegistry import GenericEnumRegistry


# Minimal normalizer for predictable tests (matches the docstring intent:
# "lowercase, no punctuation"). This avoids depending on the real
# Naming_convention implementation details.
def _norm(s: str) -> str:
    s = str(s).lower()
    out = []
    for ch in s:
        if ch.isalnum():
            out.append(ch)
    return "".join(out)


# Ad-hoc enums declared at module scope to keep them importable/reusable across tests.
# (They could be declared inside tests too; keeping them here avoids repetition.)
class _StringEnum(GenericEnumRegistry):
    RED = "Red Apple"
    BLUE = "blue-berry"
    COUNT = 3  # non-string value

    @classmethod
    def aliases(cls) -> dict:
        return {"rouge": "RED", "azure": "BLUE"}


class _SeqEnum(GenericEnumRegistry):
    HELLO = ("hello", "hi")
    BYE = ["bye", "goodbye"]
    MIXED = ("one", 2, "three")  # includes non-string in sequence

    @classmethod
    def aliases(cls) -> dict:
        return {}


def test_get_all_values_string_enum():
    assert _StringEnum.get_all_values() == ["Red Apple", "blue-berry", 3]


def test_get_all_values_sequence_enum():
    assert _SeqEnum.get_all_values() == [
        ("hello", "hi"),
        ["bye", "goodbye"],
        ("one", 2, "three"),
    ]


def test_get_without_index_returns_value():
    assert _StringEnum.RED.get() == "Red Apple"
    assert _StringEnum.COUNT.get() == 3
    assert _SeqEnum.HELLO.get() == ("hello", "hi")


def test_get_with_index_returns_element_for_sequences():
    assert _SeqEnum.HELLO.get(0) == "hello"
    assert _SeqEnum.HELLO.get(1) == "hi"
    assert _SeqEnum.BYE.get(1) == "goodbye"
    assert _SeqEnum.MIXED.get(1) == 2


def test_get_with_index_raises_for_non_sequence():
    with pytest.raises(TypeError, match="value is not a Sequence"):
        _StringEnum.RED.get(0)

    with pytest.raises(TypeError, match="value is not a Sequence"):
        _StringEnum.COUNT.get(0)


def test_find_matches_by_member_name_case_insensitive():
    # Depends only on the intent that name_convention normalizes case/punctuation.
    # Using plain case change should pass for any reasonable Naming_convention.
    assert _StringEnum.find("red") is _StringEnum.RED
    assert _StringEnum.find("BLUE") is _StringEnum.BLUE


def test_find_matches_by_value_string():
    # Avoid punctuation assumptions; use normalization-equivalent queries.
    assert _StringEnum.find("Red Apple") is _StringEnum.RED
    assert _StringEnum.find("blue berry") is _StringEnum.BLUE  # likely normalized to match "blue-berry"


def test_find_matches_inside_sequence_values():
    assert _SeqEnum.find("hi") is _SeqEnum.HELLO
    assert _SeqEnum.find("goodbye") is _SeqEnum.BYE


def test_find_is_robust_for_non_string_values():
    # COUNT has int 3, MIXED contains int 2; find() stringifies values.
    assert _StringEnum.find("3") is _StringEnum.COUNT
    assert _SeqEnum.find("2") is _SeqEnum.MIXED


def test_find_only_keys_true_does_not_match_values():
    with pytest.raises(ValueError):
        _SeqEnum.find("goodbye", only_keys=True, throw=True)

    assert _SeqEnum.find("goodbye", only_keys=True, throw=False) is _SeqEnum.HELLO


def test_find_uses_aliases():
    assert _StringEnum.find("rouge") is _StringEnum.RED
    assert _StringEnum.find("azure") is _StringEnum.BLUE


def test_from_string_delegates_to_find():
    assert _StringEnum.from_string("rouge") is _StringEnum.RED
