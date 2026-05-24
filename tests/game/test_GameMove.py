"""Tests for iarena.game.GameMove and its specialisations."""

import pytest

from iarena.game.GameMove import (
    GameMove,
    ParseableGameMove,
    ParseableStringifiableGameMove,
    StringifiableGameMove,
)


class _ConcreteGameMove(GameMove):
    pass


class _ConcreteParseableGameMove(ParseableGameMove):
    @classmethod
    def is_valid_string(cls, s: str) -> bool:
        return bool(s)

    @classmethod
    def from_string(cls, s: str) -> "_ConcreteParseableGameMove":
        return cls()


class _ConcreteStringifiableGameMove(StringifiableGameMove):
    def to_string(self) -> str:
        return "move"


class _ConcretePSGameMove(ParseableStringifiableGameMove):
    @classmethod
    def is_valid_string(cls, s: str) -> bool:
        return bool(s)

    @classmethod
    def from_string(cls, s: str) -> "_ConcretePSGameMove":
        return cls()

    def to_string(self) -> str:
        return "ps_move"


class TestGameMove:
    def test_cannot_instantiate_abstract_class(self) -> None:
        with pytest.raises(TypeError):
            GameMove()  # type: ignore[abstract]

    def test_concrete_subclass_is_instantiable(self) -> None:
        move = _ConcreteGameMove()
        assert isinstance(move, GameMove)


class TestParseableGameMove:
    def test_cannot_instantiate_abstract_class(self) -> None:
        with pytest.raises(TypeError):
            ParseableGameMove()  # type: ignore[abstract]

    def test_is_valid_string_returns_bool(self) -> None:
        assert _ConcreteParseableGameMove.is_valid_string("hello") is True
        assert _ConcreteParseableGameMove.is_valid_string("") is False

    def test_from_string_returns_instance(self) -> None:
        move = _ConcreteParseableGameMove.from_string("hello")
        assert isinstance(move, ParseableGameMove)


class TestStringifiableGameMove:
    def test_cannot_instantiate_abstract_class(self) -> None:
        with pytest.raises(TypeError):
            StringifiableGameMove()  # type: ignore[abstract]

    def test_to_string_returns_str(self) -> None:
        move = _ConcreteStringifiableGameMove()
        assert isinstance(move.to_string(), str)

    def test_str_delegates_to_to_string(self) -> None:
        move = _ConcreteStringifiableGameMove()
        assert str(move) == move.to_string()


class TestParseableStringifiableGameMove:
    def test_cannot_instantiate_abstract_class(self) -> None:
        with pytest.raises(TypeError):
            ParseableStringifiableGameMove()  # type: ignore[abstract]

    def test_is_subclass_of_both_parents(self) -> None:
        assert issubclass(ParseableStringifiableGameMove, ParseableGameMove)
        assert issubclass(ParseableStringifiableGameMove, StringifiableGameMove)

    def test_round_trip(self) -> None:
        move = _ConcretePSGameMove()
        s = move.to_string()
        assert _ConcretePSGameMove.is_valid_string(s)
        restored = _ConcretePSGameMove.from_string(s)
        assert isinstance(restored, ParseableStringifiableGameMove)
