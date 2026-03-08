"""Declares the abstract representation of a playable game position."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from iarena.utilizing.protocoling.Hashable import Hashable

if TYPE_CHECKING:
    from iarena.gaming.Rules import Rules
    from iarena.playing.PlayerIndex import PlayerIndex


class Position(Hashable, ABC):
    """Abstract representation of a game state position.

    Purpose:
        Provides the `Position` type within the IArena architecture.
    How it works:
        Encapsulates behavior through its public API and type contracts defined in this class body.
    Used for:
        Building game, mapping, utility, or protocol components that can be composed by other modules.
    Public Attributes:
        None declared at class level in this base definition.
    """

    @abstractmethod
    def next_player(self) -> PlayerIndex:
        """Return the player index that should act from this position.

        What it does:
            Implements `next_player` as part of the public behavior of its declaring class.
        How it works:
            Executes the operation according to the class contract and delegates detailed logic to the implementation.
        Args:
            None.
        Returns:
            'PlayerIndex': Result produced after executing the method contract.
        """
        # TODO
        ...

    @abstractmethod
    def get_rules(self) -> Rules:
        """Return the rules instance associated with this position.

        What it does:
            Implements `get_rules` as part of the public behavior of its declaring class.
        How it works:
            Executes the operation according to the class contract and delegates detailed logic to the implementation.
        Args:
            None.
        Returns:
            'Rules': Result produced after executing the method contract.
        """
        # TODO
        ...
