"""Tests for TicTacToeConfig."""

import pytest

from iarena.game.GameConfig import GameConfig
from iarena.games.tictactoe.TicTacToeConfig import TicTacToeConfig


class TestTicTacToeConfig:
    # --- Happy path ---

    def test_instantiation(self) -> None:
        config = TicTacToeConfig()
        assert isinstance(config, TicTacToeConfig)

    def test_is_game_config_subclass(self) -> None:
        assert issubclass(TicTacToeConfig, GameConfig)

    # --- Corner cases ---

    def test_base_game_config_still_abstract(self) -> None:
        with pytest.raises(TypeError):
            GameConfig()  # type: ignore[abstract]
