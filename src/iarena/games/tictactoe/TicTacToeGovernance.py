"""TicTacToe governance: factory and registry."""

from iarena.game.GameConfig import GameConfig
from iarena.game.GameGovernance import GameGovernance
from iarena.game.GameRules import GameRules
from iarena.games.tictactoe.TicTacToeConfig import TicTacToeConfig
from iarena.games.tictactoe.TicTacToeRules import TicTacToeRules


class TicTacToeGovernance(GameGovernance):
    """Registry and factory for TicTacToe rule variants.

    Accepts only TicTacToeConfig and produces TicTacToeRules instances.
    """

    def create_rules(self, config: GameConfig) -> GameRules:
        """Construct and return TicTacToeRules from config.

        Parameters
        ----------
        config:
            Must be a TicTacToeConfig instance.

        Returns
        -------
        TicTacToeRules
            Rules initialised from config.

        Raises
        ------
        TypeError
            If config is not a TicTacToeConfig.
        """
        if not isinstance(config, TicTacToeConfig):
            raise TypeError(f"Expected TicTacToeConfig, got {type(config).__name__}.")
        return TicTacToeRules(config)

    def supported_configs(self) -> list[type[GameConfig]]:
        """Return the list of supported config types (TicTacToeConfig only).

        Returns
        -------
        list[type[GameConfig]]
            ``[TicTacToeConfig]``.
        """
        return [TicTacToeConfig]
