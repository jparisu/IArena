"""Rule engine for the Hanoi game."""

from __future__ import annotations

from collections.abc import Iterator

from iarena.desining.gaming.GameRules import GameRules
from iarena.desining.gaming.Movement import Movement
from iarena.desining.gaming.Position import Position
from iarena.desining.gaming.ScoreBoard import ScoreBoard
from iarena.gaming.Hanoi.Hanoi import HanoiPegIndex, HanoiPegsState
from iarena.gaming.Hanoi.HanoiMovement import HanoiMovement
from iarena.gaming.Hanoi.HanoiPosition import HanoiPosition
from iarena.utilizing.protocoling import ITextRenderable


class HanoiGameRules(GameRules, ITextRenderable):
    """Implement state transitions and scoring for Towers of Hanoi.

    This implementation models the canonical three-step constraints:

    1. Only the top disc of any peg can be moved.
    2. A larger disc cannot be placed over a smaller disc.
    3. The game is solved when all discs reach the target peg in descending
       order from bottom to top.
    """

    def __init__(
        self,
        n_disks: int,
        start_peg: HanoiPegIndex = 0,
        target_peg: HanoiPegIndex = 2,
        n_pegs: int = 3,
    ) -> None:
        """Initialize and validate Hanoi configuration.

        Args:
            n_disks: Number of discs in the puzzle.
            start_peg: Peg index where all discs start.
            target_peg: Peg index that must receive all discs.
            n_pegs: Number of available pegs.

        Returns:
            None.
        """
        if n_disks <= 0:
            raise ValueError("n_disks must be > 0")
        if n_pegs < 3:
            raise ValueError("n_pegs must be >= 3")

        self._n_disks = int(n_disks)
        self._n_pegs = int(n_pegs)
        self._start_peg = int(start_peg)
        self._target_peg = int(target_peg)

        self.require_valid_peg_index(self._start_peg)
        self.require_valid_peg_index(self._target_peg)
        if self._start_peg == self._target_peg:
            raise ValueError("start_peg and target_peg must be different")

        initial_pegs: list[tuple[int, ...]] = [tuple() for _ in range(self._n_pegs)]
        initial_pegs[self._start_peg] = tuple(range(self._n_disks, 0, -1))
        self._initial_pegs = tuple(initial_pegs)

    def _as_position(self, position: Position) -> HanoiPosition:
        """Validate and cast a generic position.

        Args:
            position: Position to validate.

        Returns:
            Same position typed as ``HanoiPosition``.
        """
        if not isinstance(position, HanoiPosition):
            raise TypeError(f"position must be HanoiPosition, got {type(position).__name__}")
        return position

    def require_valid_peg_index(self, peg_index: HanoiPegIndex) -> None:
        """Validate one peg index against this rule configuration.

        Args:
            peg_index: Peg index to validate.

        Returns:
            None.
        """
        if peg_index < 0 or peg_index >= self._n_pegs:
            raise IndexError(f"peg index {peg_index} out of range [0, {self._n_pegs - 1}]")

    def n_players(self) -> int:
        """Return number of players.

        Args:
            None.

        Returns:
            Always ``1``.
        """
        return 1

    def n_disks(self) -> int:
        """Return number of configured discs.

        Args:
            None.

        Returns:
            Number of puzzle discs.
        """
        return self._n_disks

    def n_pegs(self) -> int:
        """Return number of configured pegs.

        Args:
            None.

        Returns:
            Number of puzzle pegs.
        """
        return self._n_pegs

    def start_peg(self) -> HanoiPegIndex:
        """Return configured start peg index.

        Args:
            None.

        Returns:
            Start peg index.
        """
        return self._start_peg

    def target_peg(self) -> HanoiPegIndex:
        """Return configured target peg index.

        Args:
            None.

        Returns:
            Target peg index.
        """
        return self._target_peg

    def initial_pegs(self) -> HanoiPegsState:
        """Return a copy of the initial peg state.

        Args:
            None.

        Returns:
            Immutable tuple with initial peg content.
        """
        return tuple(tuple(peg) for peg in self._initial_pegs)

    def solved_stack(self) -> tuple[int, ...]:
        """Return the canonical solved stack ordering.

        Args:
            None.

        Returns:
            Tuple ``(n, ..., 2, 1)``.
        """
        return tuple(range(self._n_disks, 0, -1))

    def min_required_moves(self) -> int:
        """Return the optimal move count for this puzzle size.

        Args:
            None.

        Returns:
            Theoretical minimum number of moves ``2**n_disks - 1``.
        """
        return (2**self._n_disks) - 1

    def first_position(self) -> HanoiPosition:
        """Create the initial position.

        Args:
            None.

        Returns:
            Initial Hanoi position.
        """
        return HanoiPosition(rules=self, pegs=self.initial_pegs(), move_count=0)

    def movement_is_legal(self, movement: HanoiMovement, position: Position) -> bool:
        """Return whether one movement is legal from the given position.

        Args:
            movement: Movement to validate.
            position: Position to validate against.

        Returns:
            ``True`` when movement is legal.
        """
        state = self._as_position(position)
        return state.can_move(movement.from_peg, movement.to_peg)

    def next_position(self, movement: Movement, position: Position) -> HanoiPosition:
        """Apply one movement and return the successor position.

        Args:
            movement: Player-selected movement.
            position: Current game position.

        Returns:
            Successor position.
        """
        if not isinstance(movement, HanoiMovement):
            raise TypeError(f"movement must be HanoiMovement, got {type(movement).__name__}")

        state = self._as_position(position)
        if not self.movement_is_legal(movement, state):
            raise ValueError(f"illegal movement {movement}")

        pegs = [list(peg) for peg in state.pegs]
        moving_disc = pegs[movement.from_peg].pop()
        pegs[movement.to_peg].append(moving_disc)
        immutable_pegs: HanoiPegsState = tuple(tuple(peg) for peg in pegs)

        return HanoiPosition(rules=self, pegs=immutable_pegs, move_count=state.move_count + 1)

    def possible_movements(self, position: Position) -> Iterator[HanoiMovement]:
        """Yield legal movements for a position.

        Args:
            position: Current game position.

        Returns:
            Iterator with legal movements.
        """
        state = self._as_position(position)
        for from_peg in range(self._n_pegs):
            for to_peg in range(self._n_pegs):
                candidate = HanoiMovement(from_peg=from_peg, to_peg=to_peg)
                if self.movement_is_legal(candidate, state):
                    yield candidate

    def finished(self, position: Position) -> bool:
        """Return whether the puzzle is solved.

        Args:
            position: Position to evaluate.

        Returns:
            ``True`` when all discs are in the target peg.
        """
        state = self._as_position(position)
        return state.pegs[self._target_peg] == self.solved_stack()

    def score(self, position: Position) -> ScoreBoard:
        """Compute score board for a position.

        Args:
            position: Position to score.

        Returns:
            Scoreboard with negative move count.
        """
        state = self._as_position(position)
        board = ScoreBoard(self.n_players())
        board.define_score(0, -float(state.move_count))
        return board

    def to_text(self) -> str:
        """Render game-rules metadata as terminal-friendly text.

        Args:
            None.

        Returns:
            Human-readable static configuration summary.
        """
        return (
            "HanoiGameRules("
            f"n_disks={self._n_disks}, "
            f"n_pegs={self._n_pegs}, "
            f"start_peg={self._start_peg}, "
            f"target_peg={self._target_peg}, "
            f"min_required_moves={self.min_required_moves()}"
            ")"
        )

    def __str__(self) -> str:
        """Render this rules object using the text-rendering protocol.

        Args:
            None.

        Returns:
            Same value as :meth:`to_text`.
        """
        return self.to_text()
