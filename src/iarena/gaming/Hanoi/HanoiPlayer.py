"""Default baseline player for Hanoi."""

from __future__ import annotations

from iarena.desining.gaming.GameRules import GameRules
from iarena.desining.gaming.Movement import Movement
from iarena.desining.gaming.Position import Position
from iarena.desining.playing.Player import Player, PlayerIndex
from iarena.gaming.Hanoi.HanoiGameRules import HanoiGameRules
from iarena.gaming.Hanoi.HanoiMovement import HanoiMovement
from iarena.gaming.Hanoi.HanoiPosition import HanoiPosition


class HanoiPlayer(Player):
    """Deterministic baseline player using a recursive solution plan.

    The player pre-computes the canonical sequence of moves for a three-peg
    Hanoi puzzle at game start. If the current state diverges from that plan,
    it falls back to the first legal movement in deterministic order.
    """

    def __init__(self, name: str | None = None) -> None:
        """Initialize player state and optional name.

        Args:
            name: Optional display name.

        Returns:
            None.
        """
        super().__init__(name=name)
        self._planned_moves: tuple[HanoiMovement, ...] = tuple()
        self._next_move_index = 0

    def _build_recursive_plan(
        self,
        n_disks: int,
        source_peg: int,
        target_peg: int,
        auxiliary_peg: int,
    ) -> tuple[HanoiMovement, ...]:
        """Build canonical recursive movement sequence for three pegs.

        Args:
            n_disks: Number of discs to move.
            source_peg: Source peg index.
            target_peg: Target peg index.
            auxiliary_peg: Helper peg index.

        Returns:
            Tuple with ordered movements.
        """
        if n_disks <= 0:
            return tuple()

        before = self._build_recursive_plan(n_disks - 1, source_peg, auxiliary_peg, target_peg)
        middle = (HanoiMovement(from_peg=source_peg, to_peg=target_peg),)
        after = self._build_recursive_plan(n_disks - 1, auxiliary_peg, target_peg, source_peg)
        return before + middle + after

    def _first_auxiliary_peg(self, rules: HanoiGameRules) -> int:
        """Return one auxiliary peg distinct from start and target.

        Args:
            rules: Active Hanoi rule set.

        Returns:
            Auxiliary peg index.
        """
        for peg_index in range(rules.n_pegs()):
            if peg_index not in {rules.start_peg(), rules.target_peg()}:
                return peg_index
        raise RuntimeError("failed to determine auxiliary peg")

    def _fallback_movement(self, position: HanoiPosition) -> HanoiMovement:
        """Select deterministic fallback movement when plan cannot be followed.

        Args:
            position: Current game position.

        Returns:
            First legal movement sorted by source and destination peg.
        """
        legal_moves: list[HanoiMovement] = list(position.rules.possible_movements(position))
        if not legal_moves:
            raise RuntimeError("no legal movement available for HanoiPlayer")
        legal_moves.sort(key=lambda movement: (movement.from_peg, movement.to_peg))
        return legal_moves[0]

    def _consume_if_legal(self, candidate: HanoiMovement, position: HanoiPosition) -> bool:
        """Consume one candidate planned movement if it is legal.

        Args:
            candidate: Candidate planned movement.
            position: Current game position.

        Returns:
            ``True`` when the candidate was consumed.
        """
        if position.can_move(candidate.from_peg, candidate.to_peg):
            self._next_move_index += 1
            return True
        return False

    def starting_game(self, rules: GameRules, player_index: PlayerIndex) -> None:
        """Pre-compute recursive solution plan before the game starts.

        Args:
            rules: Rules object that governs the upcoming game.
            player_index: Index assigned to this player in the match.

        Returns:
            None.
        """
        del player_index
        self._next_move_index = 0
        self._planned_moves = tuple()

        if not isinstance(rules, HanoiGameRules):
            return None

        if rules.n_pegs() != 3:
            return None

        auxiliary_peg = self._first_auxiliary_peg(rules)
        self._planned_moves = self._build_recursive_plan(
            n_disks=rules.n_disks(),
            source_peg=rules.start_peg(),
            target_peg=rules.target_peg(),
            auxiliary_peg=auxiliary_peg,
        )
        return None

    def play(self, position: Position) -> Movement:
        """Choose one legal movement from the provided position.

        Args:
            position: Current game position.

        Returns:
            Selected Hanoi movement.
        """
        if not isinstance(position, HanoiPosition):
            raise TypeError(f"position must be HanoiPosition, got {type(position).__name__}")

        if self._next_move_index < len(self._planned_moves):
            candidate = self._planned_moves[self._next_move_index]
            if self._consume_if_legal(candidate, position):
                return candidate

        return self._fallback_movement(position)
