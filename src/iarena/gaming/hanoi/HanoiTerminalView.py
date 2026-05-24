"""Declares the terminal visualization contract for the Hanoi game."""

from __future__ import annotations

from typing import TYPE_CHECKING

from iarena.visualizing.terminal_frontend.TerminalView import TerminalView

if TYPE_CHECKING:
    from iarena.gaming.Movement import Movement
    from iarena.gaming.Position import Position
    from iarena.gaming.Rules import Rules

from iarena.gaming.hanoi.HanoiMovement import HanoiMovement
from iarena.gaming.hanoi.HanoiPosition import HanoiPosition
from iarena.gaming.hanoi.HanoiRules import HanoiRules


class HanoiTerminalView(TerminalView):
    """Concrete terminal view implementation for the Hanoi game.

    Purpose:
        Provides text-based rendering and input parsing for Hanoi in terminal executions.
    How it works:
        Converts Hanoi domain objects into formatted strings and user commands into movements.
    Used for:
        Command-line gameplay and debugging-oriented textual visualization.
    Public Attributes:
        Inherits terminal I/O callables from `TerminalView`.
    """

    def _disk_stacks(self, position: HanoiPosition) -> list[list[int]]:
        """Build a per-peg list representation of the current disk arrangement.

        Args:
            position: Position whose disk arrangement should be represented by peg stacks.

        Returns:
            List where each index stores the disk indices currently present on that peg.
        """
        pegs: list[list[int]] = [[] for _ in range(position.n_pegs)]
        for disk_index, peg in enumerate(position.disks):
            pegs[peg].append(disk_index)
        return pegs

    def _ascii_disk(self, size: int | None, max_size: int) -> str:
        """Return one ASCII token representing a disk or an empty rod slot.

        Args:
            size: Disk size to render, or `None` for an empty level.
            max_size: Maximum disk size in the current puzzle.

        Returns:
            str: Fixed-width ASCII token for one peg level.
        """
        total_width = (2 * max_size) + 1
        if size is None:
            return "|".center(total_width)

        disk_width = (2 * size) - 1
        label = str(size)
        if disk_width == 1:
            return label.center(total_width)

        usable_label = label[:disk_width]
        left_padding = (disk_width - len(usable_label)) // 2
        right_padding = disk_width - len(usable_label) - left_padding
        disk_text = ("=" * left_padding) + usable_label + ("=" * right_padding)
        return disk_text.center(total_width)

    def _ascii_tower_lines(self, position: HanoiPosition) -> list[str]:
        """Build multi-line ASCII representation of all Hanoi towers.

        Args:
            position: Position to render as tower columns.

        Returns:
            list[str]: ASCII lines representing towers from top to base.
        """
        peg_stacks = self._disk_stacks(position)
        n_disks = len(position.disks)
        max_size = max(1, n_disks)

        disk_sizes_per_peg: list[list[int]] = []
        for peg_stack in peg_stacks:
            disk_sizes_per_peg.append([n_disks - disk_index for disk_index in peg_stack])

        lines: list[str] = []
        for level in range(n_disks - 1, -1, -1):
            tokens: list[str] = []
            for disk_sizes in disk_sizes_per_peg:
                disk_size = disk_sizes[level] if level < len(disk_sizes) else None
                tokens.append(self._ascii_disk(disk_size, max_size))
            lines.append("   ".join(tokens))

        token_width = (2 * max_size) + 1
        full_width = (token_width * position.n_pegs) + (3 * (position.n_pegs - 1))
        lines.append("-" * full_width)
        labels = [f"{peg_index}".center(token_width) for peg_index in range(position.n_pegs)]
        lines.append("   ".join(labels))
        return lines

    def get_str_info(self, rules: Rules) -> str:
        """Return formatted static information for the current Hanoi match.

        Args:
            rules: Rules instance used to derive user-facing game metadata.

        Returns:
            str: Text block rendered in the terminal information area.
        """
        if not isinstance(rules, HanoiRules):
            raise TypeError("rules must be an instance of HanoiRules.")

        conf = rules.configuration
        return (
            "=== Tower of Hanoi ===\n"
            f"Pegs: {conf.n_pegs}\n"
            f"Disks: {len(conf.disks)}\n"
            f"Goal peg: {conf.n_pegs - 1}\n"
            "Instructions:\n"
            "  - Move one disk at a time.\n"
            "  - You cannot place a larger disk on top of a smaller one.\n"
            "  - Solve by moving all disks to the goal peg."
        )

    def get_str_state(self, position: Position) -> str:
        """Return formatted text representation of the current Hanoi position.

        Args:
            position: Position to transform into a terminal-friendly state string.

        Returns:
            str: Text block describing the board state.
        """
        if not isinstance(position, HanoiPosition):
            raise TypeError("position must be an instance of HanoiPosition.")

        possible_movements = list(position.get_rules().possible_movements(position))
        movement_lines = [f"  [{move_index}] {movement}" for move_index, movement in enumerate(possible_movements)]
        if not movement_lines:
            movement_lines = ["  No legal movements available."]

        goal_peg = position.n_pegs - 1
        disks_on_goal = sum(1 for peg in position.disks if peg == goal_peg)
        progress = f"{disks_on_goal}/{len(position.disks)}" if position.disks else "0/0"

        return "\n".join(
            [
                f"Steps: {position.steps}",
                f"Progress to goal peg {goal_peg}: {progress} disks",
                f"Next player: P{int(position.next_player())}",
                "Towers:",
                *self._ascii_tower_lines(position),
                "Possible movements:",
                *movement_lines,
            ],
        )

    def capture_input(self, input: str) -> Movement:
        """Convert a terminal input line into a Hanoi movement instance.

        Args:
            input: Raw text entered by the terminal user.

        Returns:
            Movement: Parsed movement represented by the input text.
        """
        parts = input.replace(",", " ").replace("->", " ").split()
        if len(parts) != 2:
            raise ValueError("Expected exactly two peg indices, e.g. '0 2'.")

        from_peg, to_peg = int(parts[0]), int(parts[1])
        return HanoiMovement(from_peg=from_peg, to_peg=to_peg)
