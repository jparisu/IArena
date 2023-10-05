
from typing import Dict, Iterator, List
from enum import Enum
import random
import math

from IArena.interfaces.IPosition import IPosition
from IArena.interfaces.IMovement import IMovement
from IArena.interfaces.IGameRules import IGameRules
from IArena.interfaces.PlayerIndex import PlayerIndex, two_player_game_change_player
from IArena.utils.decorators import override
import IArena.games.BlindWalk as BlindWalk

"""
This game represents a grid search where each square has a different weight.
There is a grid of NxN and the player must reach the position [N-1,N-1] from [0,0].
The player can move in 4 directions: up, down, left and right.
Each movement has a cost equal to the weight of the square.
The player must reach the end with the minimum cost.

Similar to BlindWalk but the player has access to the whole map from the beginning.
"""

FieldWalkSquare = BlindWalk.BlindWalkSquare
FieldWalkMovement = BlindWalk.BlindWalkMovement
MovementDirection = BlindWalk.MovementDirection
FieldWalkPosition = BlindWalk.BlindWalkPosition
FieldWalkMap = BlindWalk.BlindWalkMap
FieldWalkRules = BlindWalk.BlindWalkRules

class FieldWalkRules(BlindWalk.BlindWalkRules):

    def __init__(
            self,
            initial_map: BlindWalk.BlindWalkMap = None,
            rows: int = 10,
            cols: int = 10,
            seed: int = 0):
        super().__init__(initial_map, rows, cols, seed)

    def get_map(self):
        return self._BlindWalkRules__map
