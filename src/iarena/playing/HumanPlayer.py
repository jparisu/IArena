"""Declares the abstract human-player type that interacts through a view."""

from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING

from .Player import Player

if TYPE_CHECKING:
    from iarena.visualizing.View import View


class HumanPlayer(Player, ABC):
    """Abstract human player that delegates interaction to a view.

    Purpose:
        Provides the `HumanPlayer` type within the IArena architecture.
    How it works:
        Encapsulates behavior through its public API and type contracts defined in this class body.
    Used for:
        Building game, mapping, utility, or protocol components that can be composed by other modules.
    Public Attributes:
        render (View): Public attribute exposed by this class.
    """

    render: View
