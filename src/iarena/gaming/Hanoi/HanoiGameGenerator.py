"""Dictionary-driven rules generator for Hanoi."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from iarena.desining.gaming.GameConfiguration import GameConfiguration
from iarena.desining.gaming.GameGenerator import GameGenerator
from iarena.desining.gaming.GameRules import GameRules
from iarena.gaming.Hanoi.HanoiGameConfiguration import HanoiGameConfiguration
from iarena.gaming.Hanoi.HanoiGameRules import HanoiGameRules


class HanoiGameGenerator(GameGenerator):
    """Build Hanoi rules from a plain dictionary configuration."""

    def _as_hanoi_configuration(
        self,
        configuration: GameConfiguration | HanoiGameConfiguration | Mapping[str, Any],
    ) -> HanoiGameConfiguration:
        """Normalize supported configuration values into Hanoi configuration.

        Args:
            configuration: Generic or game-specific configuration value.

        Returns:
            Parsed Hanoi configuration instance.
        """
        if isinstance(configuration, HanoiGameConfiguration):
            return configuration
        if isinstance(configuration, GameConfiguration):
            return HanoiGameConfiguration.from_game_configuration(configuration)
        return HanoiGameConfiguration.from_dict(configuration)

    def build_game(
        self,
        configuration: GameConfiguration | HanoiGameConfiguration | Mapping[str, Any],
    ) -> GameRules:
        """Build a ``HanoiGameRules`` object from a configuration payload.

        Args:
            configuration: Generic or game-specific configuration payload.

        Returns:
            Configured Hanoi rules object.
        """
        parsed_configuration = self._as_hanoi_configuration(configuration)
        return HanoiGameRules(
            n_disks=parsed_configuration.n_disks,
            start_peg=parsed_configuration.start_peg,
            target_peg=parsed_configuration.target_peg,
            n_pegs=parsed_configuration.n_pegs,
        )
