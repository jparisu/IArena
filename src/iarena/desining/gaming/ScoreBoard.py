"""Score aggregation utilities for multi-player games."""

from __future__ import annotations

from iarena.desining.playing.Player import PlayerIndex

Score = float


class ScoreBoard:
    """Store per-player numeric scores and derive winner information."""

    def __init__(self, n_players: int) -> None:
        """Create a scoreboard with a fixed number of players.

        Args:
            n_players: Number of players tracked by this board.

        Returns:
            None.
        """
        if n_players < 0:
            raise ValueError("n_players must be >= 0")
        self.score: list[Score] = [0.0] * n_players

    def _check_player(self, player: PlayerIndex) -> None:
        """Validate that a player index is within scoreboard bounds.

        Args:
            player: Player index to validate.

        Returns:
            None.
        """
        if player < 0 or player >= len(self.score):
            raise IndexError(f"player index {player} out of range [0, {len(self.score) - 1}]")

    def define_score(self, player: PlayerIndex, score: Score) -> None:
        """Set the absolute score for one player.

        Args:
            player: Player index to update.
            score: New absolute score value.

        Returns:
            None.
        """
        self._check_player(player)
        self.score[player] = score

    def get_score(self, player: PlayerIndex) -> Score:
        """Return the current score of a specific player.

        Args:
            player: Player index to query.

        Returns:
            Current score for ``player``.
        """
        self._check_player(player)
        return self.score[player]

    def __str__(self) -> str:
        """Return compact string representation of all score values.

        Args:
            None.

        Returns:
            Compact score representation.
        """
        return str(self.score)

    def pretty_print(self) -> str:
        """Return a multi-line player-by-player score representation.

        Args:
            None.

        Returns:
            Multiline string with one line per player.
        """
        lines = [f"Player: <{player}> : {value}" for player, value in enumerate(self.score)]
        return "\n".join(lines) + ("\n" if lines else "")

    def add_score(self, player: PlayerIndex, score: Score) -> None:
        """Add a score delta to a player.

        Args:
            player: Player index to update.
            score: Increment (or decrement) to apply.

        Returns:
            None.
        """
        self._check_player(player)
        self.score[player] += score

    def winner(self) -> PlayerIndex | None:
        """Return winner index when there is a unique best score.

        Args:
            None.

        Returns:
            Winner player index, or ``None`` when tied.
        """
        winner_index: PlayerIndex | None = None
        winner_score = -float("inf")
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
        return None

    def join(self, score_board: ScoreBoard) -> None:
        """Merge another scoreboard into this one by summing scores.

        Args:
            score_board: Source scoreboard to accumulate.

        Returns:
            None.
        """
        if len(self.score) != len(score_board.score):
            raise ValueError("both scoreboards must have the same number of players")
        for player, score in enumerate(score_board.score):
            self.add_score(player, score)

    def n_players(self) -> int:
        """Return how many players are tracked by this scoreboard.

        Args:
            None.

        Returns:
            Number of tracked players.
        """
        return len(self.score)

    def __getitem__(self, player: PlayerIndex) -> Score:
        """Enable index-based access like ``board[player_index]``.

        Args:
            player: Player index to query.

        Returns:
            Current score for ``player``.
        """
        return self.get_score(player)
