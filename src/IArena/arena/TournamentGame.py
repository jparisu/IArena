import itertools
import numpy as np
from typing import List, Dict

from IArena.interfaces.IPlayer import IPlayer
from IArena.interfaces.IPosition import IPosition
from IArena.interfaces.IGameRules import IGameRules
from IArena.interfaces.PlayerIndex import PlayerIndex
from IArena.interfaces.ScoreBoard import ScoreBoard
from IArena.arena.GenericGame import GenericGame
from IArena.utils.decorators import override
from IArena.utils.Timer import Timer

class TournamentGame():

    def __init__(
            self,
            rules: IGameRules,
            players: Dict[str, IPlayer],
            matches: int = 10):

        self.rules = rules
        self.players = players
        self.matches = matches


    def play(self) -> PlayerIndex:

        players_names = list(self.players.keys())
        game_players = self.rules.n_players()

        board = TournamentScoreBoard()

        # Set all possible games
        for matching in itertools.permutations(players_names, game_players):
            for _ in range(self.matches):
                match_score = self._next_match(matching)
                board.add_match(match_score, matching)

        return board


    def _next_match(self, players: List[PlayerIndex]) -> ScoreBoard:

        to_play = [self.players[p] for p in players]
        game = GenericGame(self.rules, to_play)
        return game.play()


class TournamentScoreBoard:

    def __init__(self):
        self.players = {}
        self.matches = {}

    def add_match(self, score: ScoreBoard, player_names: List[str]):
        """Add score to a player."""

        # Adapt scores to player_names

        for i, s in enumerate(score.score):
            player_name = player_names[i]
            if player_name in self.players:
                self.players[player_name].append(s)
            else:
                self.players[player_name] = [s]

        matching = ' VS '.join(player_names)
        if matching in self.matches:
            self.matches[matching].join(score)
        else:
            self.matches[matching] = score


    def get_player_scores(self, player: str) -> ScoreBoard:
        """Get the score of a player."""
        return self.players[player]

    def get_players_table(self) -> Dict[str, Dict[str, float]]:
        """Create a table with each column each player and each row:
            - number of matches
            - total score
            - average score
            - max score
            - min score
            - std score
        """
        table = {}
        for player in self.players:
            table[player] = {
                "matches": len(self.players[player]),
                "total": sum(self.players[player]),
                "max": max(self.players[player]),
                "min": min(self.players[player]),
                "average": np.mean(self.players[player]),
                "std": np.std(self.players[player]),
                "won": sum([1 for s in self.players[player] if s > 0])
            }
        return table


    def __str__(self) -> str:
        """Print the table."""

        if not self.players:
            return "No data"

        table = self.get_players_table()

        players = list(table.keys())
        columns = table[players[0]].keys()

        # Format each value: use 2 decimals for floats, simple string conversion for ints.
        formatted = {}
        for player in players:
            formatted[player] = {}
            for col in columns:
                val = table[player][col]
                if isinstance(val, float):
                    formatted[player][col] = f"{val:.2f}"
                else:
                    formatted[player][col] = str(val)

        # Determine width for each statistic column
        col_widths = {}
        for col in columns:
            max_width = len(col)
            for player in players:
                max_width = max(max_width, len(formatted[player][col]))
            col_widths[col] = max_width

        # Determine width for the player column
        player_col_width = max(len(str(player)) for player in players)

        # Build header row
        header = f"{'Player'.ljust(player_col_width)} | " + " | ".join(col.rjust(col_widths[col]) for col in columns)
        separator = "-" * len(header)

        # Build each player row
        rows = [header, separator]
        for player in players:
            row = str(player).ljust(player_col_width) + " | " + " | ".join(formatted[player][col].rjust(col_widths[col]) for col in columns)
            rows.append(row)

        return "\n".join(rows)
