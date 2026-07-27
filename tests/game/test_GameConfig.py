"""Tests for iarena.game.GameConfig."""

import abc

import pytest

from iarena.game.GameConfig import GameConfig


class _ConcreteGameConfig(GameConfig):
    """Minimal concrete subclass for testing."""


class TestGameConfig:
    """Tests for the GameConfig abstract base class."""

    def test_cannot_instantiate_abstract_class(self) -> None:
        """GameConfig must not be directly instantiable."""
        with pytest.raises(TypeError):
            GameConfig()  # type: ignore[abstract]

    def test_concrete_subclass_is_instantiable(self) -> None:
        """A concrete subclass with no abstract methods must be instantiable."""
        config = _ConcreteGameConfig()
        assert isinstance(config, GameConfig)

    def test_is_subclass_of_abc(self) -> None:
        """GameConfig must be a proper abstract base class."""
        assert issubclass(GameConfig, abc.ABC)
