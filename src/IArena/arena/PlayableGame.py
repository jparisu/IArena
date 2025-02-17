from typing import List

from IArena.interfaces.IGameRules import IGameRules
from IArena.interfaces.PlayerIndex import PlayerIndex
from IArena.interfaces.Score import ScoreBoard
from IArena.arena.GenericGame import GenericGame
from IArena.players.players import PlayablePlayer

class PlayableGame(GenericGame):

    def __init__(
            self,
            rules: IGameRules):
        super().__init__(
            rules=rules,
            players=[
                PlayablePlayer() for i in range(rules.n_players())])

    def play(self) -> ScoreBoard:
        score = super().play()
        print(f'SCORE: {score}')
        print(f'WINNER: Player <{score.winner()}>')
        return score
