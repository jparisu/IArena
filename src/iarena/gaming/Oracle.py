"""Declares the base oracle contract for benchmark score estimation."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from iarena.gaming.Rules import Rules
    from iarena.scoring.ScoreBoard import ScoreBoard


class Oracle:
    """Resolver that computes min and max benchmark scores for a game.

    Purpose:
        Provides the `Oracle` type within the IArena architecture.
    How it works:
        Encapsulates behavior through its public API and type contracts defined in this class body.
    Used for:
        Building game, mapping, utility, or protocol components that can be composed by other modules.
    Public Attributes:
        None declared at class level in this base definition.
    """

    @classmethod
    def reckon_solution_score(cls, rules: Rules) -> tuple[ScoreBoard, ScoreBoard]:
        """Compute best and worst attainable scoreboards for given rules.

        What it does:
            Implements `reckon_solution_score` as part of the public behavior of its declaring class.
        How it works:
            Executes the operation according to the class contract and delegates detailed logic to the implementation.
        Args:
            rules ('Rules'): Input consumed by this operation.
        Returns:
            tuple['ScoreBoard', 'ScoreBoard']: Result produced after executing the method contract.
        """
        # TODO
        raise NotImplementedError("Oracle.reckon_solution_score is not implemented yet.")
