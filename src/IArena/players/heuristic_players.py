
import random
import math
from typing import Tuple

from IArena.interfaces.IPosition import IPosition
from IArena.interfaces.IMovement import IMovement
from IArena.interfaces.IPlayer import IPlayer
from IArena.interfaces.PlayerIndex import PlayerIndex
from IArena.utils.decorators import override
from IArena.utils.RandomGenerator import RandomGenerator
from IArena.players.minimax_players import MinimaxRandomConsistentPlayer, MinimaxScoreType


class Connect4HeuristicPlayer(IPlayer):

    @override
    def heuristic(self, position: IPosition) -> MinimaxScoreType:
        return 0
