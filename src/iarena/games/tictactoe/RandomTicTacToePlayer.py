"""Random automatic player for TicTacToe."""

import random

from iarena.game.GameMove import GameMove
from iarena.game.GameState import GameState
from iarena.games.tictactoe.TicTacToeRules import TicTacToeRules
from iarena.player.AutomaticPlayer import AutomaticPlayer


class RandomTicTacToePlayer(AutomaticPlayer):
    """Picks a uniformly random legal move each turn.

    Parameters
    ----------
    rules:
        The TicTacToeRules instance used to enumerate legal moves.
    """

    def __init__(self, rules: TicTacToeRules) -> None:
        self._rules = rules

    def choose_move(self, state: GameState) -> GameMove:
        moves = list(self._rules.legal_moves(state))
        return random.choice(moves)
