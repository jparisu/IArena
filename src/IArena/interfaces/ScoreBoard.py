from typing import List, Dict
import numpy as np

from IArena.interfaces.PlayerIndex import PlayerIndex

Score = float

class ScoreBoard:

    def __init__(self):
        self.score = []

    def define_score(self, player: PlayerIndex, score: Score):
        """Define the score of a player."""
        if len(self.score) <= player:
            self.score += [0] * (player - len(self.score) + 1)
        self.score[player] = score

    def get_score(self, player: PlayerIndex) -> Score:
        """Get the score of a player."""
        return self.score[player]

    def __str__(self) -> str:
        return str(self.score)

    def pretty_print(self) -> str:
        st = ""
        for player in range(len(self.score)):
            st += "Player: <" + str(player) + "> : <" + str(self.score[player]) + ">\n"
        return st

    def add_score(self, player: PlayerIndex, score: Score):
        """Add score to a player."""
        if len(self.score) <= player:
            self.score += [0] * (player - len(self.score) + 1)
        self.score[player] += score

    def winner(self) -> PlayerIndex:
        """Get the winner of the game."""
        winner_index = None
        winner_score = -float('inf')
        is_unique_winner = True

        for player, score in enumerate(self.score):
            if score > winner_score:
                winner_index = player
                winner_score = score
                is_unique_winner = True
            elif score == winner_score:
                is_unique_winner = False
        if is_unique_winner:
            return winner_index
        else:
            return None


    def join(self, score_board: 'ScoreBoard'):
        """Join two score boards."""
        for player, score in enumerate(score_board.score):
            self.add_score(player, score)

    def __getitem__(self, player: PlayerIndex) -> Score:
        return self.get_score(player)
