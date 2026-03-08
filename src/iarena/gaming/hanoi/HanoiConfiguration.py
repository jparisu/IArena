"""Declares the concrete Hanoi configuration model."""

from __future__ import annotations

from typing import Any

from iarena.gaming.Configuration import Configuration


class HanoiConfiguration(Configuration):
    """Concrete Hanoi configuration defining initial disk-to-peg layout.

    Purpose:
        Encapsulates puzzle parameters required to build a playable Hanoi ruleset.
    How it works:
        Stores static setup values used by `HanoiGame.generate_rules`.
    Used for:
        Instantiating reproducible Hanoi matches with explicit board dimensions.
    Public Attributes:
        n_pegs (int): Number of pegs available in the puzzle.
        disks (list[int]): Initial per-disk peg assignment.
    """

    n_pegs: int
    disks: list[int]

    def __init__(self, n_pegs: int, disks: list[int]) -> None:
        """Create one Hanoi configuration from basic puzzle parameters.

        Args:
            n_pegs: Number of pegs available in the puzzle.
            disks: Initial per-disk peg assignment at game start.

        Returns:
            None.
        """
        if n_pegs < 2:
            raise ValueError("n_pegs must be at least 2.")
        if any(peg < 0 or peg >= n_pegs for peg in disks):
            raise ValueError("All disk peg indices must be within [0, n_pegs).")

        self.n_pegs = n_pegs
        self.disks = list(disks)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> HanoiConfiguration:
        """Build one Hanoi configuration from a dictionary payload.

        Args:
            data: Mapping containing `n_pegs` and either `disks` or `n_disks`.

        Returns:
            HanoiConfiguration: Parsed concrete configuration object.
        """
        n_pegs = int(data.get("n_pegs", 3))

        raw_disks = data.get("disks")
        if raw_disks is None:
            n_disks = int(data.get("n_disks", 3))
            raw_disks = [0] * n_disks

        if not isinstance(raw_disks, list):
            raise TypeError("`disks` must be a list of peg indices.")

        disks = [int(peg_index) for peg_index in raw_disks]
        return cls(n_pegs=n_pegs, disks=disks)
