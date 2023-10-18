
from IArena.interfaces.PlayerIndex import PlayerIndex

Score = float

class ScoreBoard:

    def __init__(self):
        self.score = {}

    def define_score(self, player: PlayerIndex, score: Score):
        """Define the score of a player."""
        self.score[player] = score

    def get_score(self, player: PlayerIndex) -> Score:
        """Get the score of a player."""
        return self.score[player]

    def __str__(self) -> str:
        st = ""
        for player in sorted(self.score, key=self.score.get, reverse=True):
            st += "Player: <" + str(player) + "> : <" + str(self.score[player]) + ">\n"
        return st

    def add_score(self, player: PlayerIndex, score: Score):
        """Add score to a player."""
        if player in self.score:
            self.score[player] += score
        else:
            self.score[player] = score

    def winner(self) -> Score:
        """Get the winner of the game."""
        # Sort the players by score and return the higher
        return sorted(self.score, key=self.score.get)[0]

    def join(self, score_board: 'ScoreBoard'):
        """Join two score boards."""
        for player in score_board.score:
            if player in self.score:
                self.score[player] += score_board.score[player]
            else:
                self.score[player] = score_board.score[player]
