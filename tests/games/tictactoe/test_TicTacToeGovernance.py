"""Tests for TicTacToeGovernance."""

import pytest

from iarena.game.GameConfig import GameConfig
from iarena.game.GameGovernance import GameGovernance
from iarena.game.GameRules import GameRules
from iarena.games.tictactoe.TicTacToeConfig import TicTacToeConfig
from iarena.games.tictactoe.TicTacToeGovernance import TicTacToeGovernance
from iarena.games.tictactoe.TicTacToeRules import TicTacToeRules


@pytest.fixture()
def governance() -> TicTacToeGovernance:
    return TicTacToeGovernance()


class TestTicTacToeGovernance:
    # --- Happy path ---

    def test_is_game_governance_subclass(self) -> None:
        assert issubclass(TicTacToeGovernance, GameGovernance)

    def test_supported_configs_contains_tictactoe_config(
        self, governance: TicTacToeGovernance
    ) -> None:
        assert TicTacToeConfig in governance.supported_configs()

    def test_supported_configs_returns_list(self, governance: TicTacToeGovernance) -> None:
        result = governance.supported_configs()
        assert isinstance(result, list)
        assert all(issubclass(c, GameConfig) for c in result)

    def test_create_rules_returns_tictactoe_rules(self, governance: TicTacToeGovernance) -> None:
        rules = governance.create_rules(TicTacToeConfig())
        assert isinstance(rules, TicTacToeRules)

    def test_create_rules_returns_game_rules(self, governance: TicTacToeGovernance) -> None:
        rules = governance.create_rules(TicTacToeConfig())
        assert isinstance(rules, GameRules)

    # --- Failure cases ---

    def test_create_rules_wrong_config_type_raises(
        self, governance: TicTacToeGovernance
    ) -> None:
        class _OtherConfig(GameConfig):
            pass

        with pytest.raises(TypeError):
            governance.create_rules(_OtherConfig())
