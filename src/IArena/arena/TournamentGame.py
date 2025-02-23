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
                "won": sum([1 for s in self.players[player] if s > 0]),
                "tie": sum([1 for s in self.players[player] if s == 0]),
                "lost": sum([1 for s in self.players[player] if s < 0]),
            }
        return table

    def print_players_table(self) -> str:
        if not self.players:
            return "No data"

        table = self.get_players_table()

        players = list(sorted(table.keys()))
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

    def print_matches(self) -> str:
        if not self.matches:
            return "No data"

        rows = []
        for match, score in self.matches.items():
            rows.append(f"{match}: {str(score)}")

        return "\n".join(rows)

    def __str__(self) -> str:
        line = "-"*70 + "\n"
        st = ""
        st += line
        st += "Results:\n"
        st += self.print_players_table() + "\n"
        st += "\n"
        st += "Matches:\n"
        st += self.print_matches() + "\n"
        st += line
        return st


class RepeatedGame(GenericGame):

    def __init__(
            self,
            rules: IGameRules,
            players: List[IPlayer],
            repetition: int = 10):
        super().__init__(rules, players)
        self.repetition = repetition

    @override
    def play(self) -> TournamentScoreBoard:

        score_board = TournamentScoreBoard()
        players_names = [p.name() for p in self.players]

        for _ in range(self.repetition):
            score = super().play()
            score_board.add_match(score, players_names)

        return score_board


class TournamentGame():

    def __init__(
            self,
            rules: IGameRules,
            players: List[IPlayer],
            matches: int = 10,
            game_ctor = GenericGame):

        self.rules = rules
        self.players = players
        self.matches = matches
        self.game_ctor = game_ctor


    def play(self) -> TournamentScoreBoard:

        game_players = self.rules.n_players()

        score_board = TournamentScoreBoard()

        # Set all possible games
        for matching in itertools.permutations(range(len(self.players)), game_players):
            players = [self.players[p] for p in matching]
            players_names = [p.name() for p in players]
            for _ in range(self.matches):
                match_score = self._next_match(players)
                score_board.add_match(match_score, players_names)

        return score_board


    def _next_match(self, players: List[IPlayer]) -> ScoreBoard:

        game = self.game_ctor(self.rules, players)
        return game.play()
