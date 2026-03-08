"""Declares the concrete rules contract for the TicTacToe game."""
# pylint: disable=too-many-lines  # TODO: review

from __future__ import annotations

from collections.abc import Iterator
from typing import TYPE_CHECKING

from iarena.gaming.Rules import Rules
from iarena.playing.PlayerIndex import PlayerIndex
from iarena.scoring.Score import Score
from iarena.scoring.ScoreBoard import ScoreBoard

if TYPE_CHECKING:
    from iarena.gaming.Movement import Movement
    from iarena.gaming.Position import Position
    from iarena.gaming.tictactoe.TicTacToeConfiguration import TicTacToeConfiguration

from iarena.gaming.tictactoe.TicTacToeMovement import TicTacToeMovement
from iarena.gaming.tictactoe.TicTacToePosition import TicTacToePosition


class TicTacToeRules(Rules):
    """Concrete rules implementation for the TicTacToe game.

    Purpose:
        Defines legal moves, turn progression, terminal conditions, and scoring for TicTacToe.
    How it works:
        Applies board-coordinate rules to evolve one position into the next.
    Used for:
        Match execution, move validation, and score computation.
    Public Attributes:
        configuration (TicTacToeConfiguration): Configuration instance used to initialize the ruleset.
    """

    configuration: TicTacToeConfiguration

    def __init__(self, configuration: TicTacToeConfiguration) -> None:
        """Create one TicTacToe rules engine bound to a concrete configuration.

        Args:
            configuration: Static setup used to derive initial and terminal states.

        Returns:
            None.
        """
        self.configuration = configuration

    def _require_position(self, pos: Position) -> TicTacToePosition:
        """Return the validated TicTacToe position used by rule operations.

        Args:
            pos: Candidate position object received by the public rules API.

        Returns:
            Validated `TicTacToePosition` instance.

        Raises:
            TypeError: If `pos` is not a `TicTacToePosition`.
            ValueError: If dimensions differ from the rule configuration.
        """
        if not isinstance(pos, TicTacToePosition):
            raise TypeError("pos must be an instance of TicTacToePosition.")
        if pos.board_size != self.configuration.board_size:
            raise ValueError("Position board_size must match rule configuration.")
        if pos.win_length != self.configuration.win_length:
            raise ValueError("Position win_length must match rule configuration.")
        return pos

    def _require_movement(self, mov: Movement) -> TicTacToeMovement:
        """Return the validated TicTacToe movement used by rule transitions.

        Args:
            mov: Candidate movement object received by the public rules API.

        Returns:
            Validated `TicTacToeMovement` instance.

        Raises:
            TypeError: If `mov` is not a `TicTacToeMovement`.
        """
        if not isinstance(mov, TicTacToeMovement):
            raise TypeError("mov must be an instance of TicTacToeMovement.")
        return mov

    def _index(self, row: int, col: int) -> int:
        """Return the flat list index associated with one board coordinate.

        Args:
            row: Zero-based row index.
            col: Zero-based column index.

        Returns:
            int: Row-major flat index.
        """
        return (row * self.configuration.board_size) + col

    def _winner(self, position: TicTacToePosition) -> PlayerIndex | None:
        """Return the winner of the provided position when available.

        Args:
            position: Position to analyze for aligned winning lines.

        Returns:
            PlayerIndex | None: Winning player index or `None` if there is no winner.
        """
        size = position.board_size
        target = position.win_length
        cells = position.cells

        directions = ((1, 0), (0, 1), (1, 1), (1, -1))
        for row in range(size):
            for col in range(size):
                current = cells[self._index(row, col)]
                if current is None:
                    continue

                for delta_row, delta_col in directions:
                    end_row = row + ((target - 1) * delta_row)
                    end_col = col + ((target - 1) * delta_col)
                    if end_row < 0 or end_row >= size or end_col < 0 or end_col >= size:
                        continue

                    if all(
                        cells[self._index(row + (step * delta_row), col + (step * delta_col))] == current
                        for step in range(target)
                    ):
                        return PlayerIndex(current)
        return None

    def n_players(self) -> int:
        """Return the number of players supported by this ruleset.

        Args:
            None.

        Returns:
            int: Number of participating players.
        """
        return 2

    def first_position(self) -> Position:
        """Return the initial position for a newly started TicTacToe match.

        Args:
            None.

        Returns:
            Position: Initial state derived from the configured dimensions.
        """
        position = TicTacToePosition(
            board_size=self.configuration.board_size,
            win_length=self.configuration.win_length,
            cells=None,
            turn=0,
            current_player=PlayerIndex(0),
        )
        position._rules = self
        return position

    def next_position(self, pos: Position, mov: Movement) -> Position:
        """Return the position produced after applying one movement.

        Args:
            pos: Source position where the movement is applied.
            mov: Candidate movement to evaluate and execute.

        Returns:
            Position: Position generated after the movement is applied.
        """
        tic_pos = self._require_position(pos)
        tic_mov = self._require_movement(mov)

        if self.is_finished(tic_pos):
            raise ValueError("Cannot play movement on a finished game.")

        size = tic_pos.board_size
        if tic_mov.row >= size or tic_mov.col >= size:
            raise ValueError("Movement coordinates must be within board bounds.")

        index = self._index(tic_mov.row, tic_mov.col)
        if tic_pos.cells[index] is not None:
            raise ValueError("Cannot play on an occupied cell.")

        next_cells = list(tic_pos.cells)
        next_cells[index] = int(tic_pos.current_player)
        next_player = PlayerIndex(1 - int(tic_pos.current_player))

        next_position = TicTacToePosition(
            board_size=tic_pos.board_size,
            win_length=tic_pos.win_length,
            cells=next_cells,
            turn=tic_pos.turn + 1,
            current_player=next_player,
        )
        next_position._rules = self
        return next_position

    def possible_movements(self, pos: Position) -> Iterator[Movement]:
        """Yield all legal movements available from the provided position.

        Args:
            pos: Position whose legal outgoing moves must be enumerated.

        Returns:
            Iterator[Movement]: Lazy iterator over legal movements.
        """
        tic_pos = self._require_position(pos)
        if self.is_finished(tic_pos):
            return

        size = tic_pos.board_size
        for row in range(size):
            for col in range(size):
                if tic_pos.cells[self._index(row, col)] is None:
                    yield TicTacToeMovement(row=row, col=col)

    def is_finished(self, pos: Position) -> bool:
        """Return whether the provided position is terminal.

        Args:
            pos: Position to evaluate against TicTacToe completion conditions.

        Returns:
            bool: `True` when the game has ended, else `False`.
        """
        tic_pos = self._require_position(pos)
        return self._winner(tic_pos) is not None or all(cell is not None for cell in tic_pos.cells)

    def get_score(self, pos: Position) -> ScoreBoard:
        """Return the scoreboard representation associated with a position.

        Args:
            pos: Position whose score must be derived.

        Returns:
            ScoreBoard: Scoreboard object representing the current match result.
        """
        tic_pos = self._require_position(pos)
        winner = self._winner(tic_pos)

        board = ScoreBoard()
        if winner == PlayerIndex(0):
            board._scores = {PlayerIndex(0): Score(1.0), PlayerIndex(1): Score(-1.0)}
        elif winner == PlayerIndex(1):
            board._scores = {PlayerIndex(0): Score(-1.0), PlayerIndex(1): Score(1.0)}
        else:
            board._scores = {PlayerIndex(0): Score(0.0), PlayerIndex(1): Score(0.0)}
        return board
