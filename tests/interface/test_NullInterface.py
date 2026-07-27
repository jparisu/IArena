"""Tests for iarena.interface.NullInterface."""

import pytest

from iarena.interface.Interface import Interface
from iarena.interface.NullInterface import NullInterface


class TestNullInterface:
    def test_is_subclass_of_interface(self) -> None:
        assert issubclass(NullInterface, Interface)

    def test_can_be_instantiated_without_view(self) -> None:
        NullInterface()  # must not raise

    def test_render_does_not_raise(self) -> None:
        NullInterface().render("anything")

    def test_ask_raises_not_implemented(self) -> None:
        with pytest.raises(NotImplementedError):
            NullInterface().ask("prompt")
