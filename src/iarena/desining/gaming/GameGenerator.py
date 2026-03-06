"""Protocol for factories that build game rules from configurations."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

from iarena.desining.gaming.GameConfiguration import GameConfiguration

if TYPE_CHECKING:
    from iarena.desining.gaming.GameRules import GameRules


@runtime_checkable
class GameGenerator(Protocol):
    """Opt-in capability to create game rules from typed configurations."""

    def build_game(self, configuration: GameConfiguration) -> GameRules:
        """Create and return rules configured by ``configuration``.

        Args:
            configuration: Structured configuration payload.

        Returns:
            Rules instance configured from ``configuration``.
        """
        raise NotImplementedError
