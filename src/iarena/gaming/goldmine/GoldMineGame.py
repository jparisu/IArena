"""GoldMine game registry entry."""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any, ClassVar

from iarena.gaming.Game import Game
from iarena.utilizing.structuring.GenericSingleton import GenericSingleton

if TYPE_CHECKING:
    from iarena.gaming.Configuration import Configuration
    from iarena.gaming.Oracle import Oracle
    from iarena.gaming.Rules import Rules
    from iarena.playing.Player import Player
    from iarena.visualizing.View import View

from iarena.gaming.goldmine.GoldMineConfiguration import GoldMineConfiguration
from iarena.gaming.goldmine.GoldMineOracle import GoldMineOracle
from iarena.gaming.goldmine.GoldMinePerfectPlayer import GoldMinePerfectPlayer
from iarena.gaming.goldmine.GoldMineRules import GoldMineRules
from iarena.gaming.goldmine.GoldMineStreamlitView import GoldMineStreamlitView
from iarena.gaming.goldmine.GoldMineTerminalView import GoldMineTerminalView
from iarena.playing.PolyvalentRandomPlayer import PolyvalentRandomPlayer
from iarena.playing.PolyvalentStreamlitPlayer import PolyvalentStreamlitPlayer
from iarena.playing.PolyvalentTerminalPlayer import PolyvalentTerminalPlayer


class GoldMineGame(Game):
    """Concrete `Game` implementation for GoldMine."""

    _singleton: ClassVar[GenericSingleton[GoldMineGame] | None] = None

    @classmethod
    def instance(cls) -> GoldMineGame:
        """Return the singleton GoldMine game instance."""
        if cls._singleton is None:
            cls._singleton = GenericSingleton(cls)
        return cls._singleton()

    def default_configuration(self) -> GoldMineConfiguration:
        """Return the default GoldMine configuration.

        Returns:
            GoldMineConfiguration: Default playable setup.
        """
        return GoldMineConfiguration(n_rows=6, n_cols=6, map_generator="uniform", seed=0)

    def _prompt_positive_int(
        self,
        input_fnc: Callable[[str], str],
        output_fnc: Callable[[str], None],
        prompt: str,
        default: int,
        field_name: str,
    ) -> int:
        """Prompt for one positive integer value.

        Args:
            input_fnc: Input function.
            output_fnc: Output function.
            prompt: Prompt text.
            default: Default value used on empty input.
            field_name: Field label used in validation messages.

        Returns:
            int: Validated positive integer value.
        """
        while True:
            raw_value = input_fnc(f"{prompt} [{default}]: ").strip()
            if raw_value == "":
                return default
            try:
                value = int(raw_value)
            except ValueError:
                output_fnc(f"Invalid value. {field_name} must be an integer.")
                continue
            if value < 1:
                output_fnc(f"{field_name} must be at least 1.")
                continue
            return value

    def terminal_prompt_configuration(
        self,
        input_fnc: Callable[[str], str],
        output_fnc: Callable[[str], None],
    ) -> GoldMineConfiguration:
        """Interactively build one GoldMine configuration in terminal mode.

        Args:
            input_fnc: Input callable used to capture user text.
            output_fnc: Output callable used to display prompts.

        Returns:
            GoldMineConfiguration: Configuration built from terminal answers.
        """
        output_fnc("Guided GoldMine configuration.")
        n_rows = self._prompt_positive_int(input_fnc, output_fnc, "Map rows", 6, "Map rows")
        n_cols = self._prompt_positive_int(input_fnc, output_fnc, "Map cols", 6, "Map cols")
        return GoldMineConfiguration(n_rows=n_rows, n_cols=n_cols, map_generator="uniform", seed=0)

    def streamlit_prompt_configuration(
        self,
        n_rows: int = 6,
        n_cols: int = 6,
        map_generator: str = "uniform",
        seed: int = 0,
        compass_activated: bool = False,
        proximity_activated: bool = False,
        density_activated: bool = False,
    ) -> GoldMineConfiguration:
        """Build a GoldMine configuration from streamlit-oriented control values.

        Args:
            n_rows: Number of map rows.
            n_cols: Number of map columns.
            map_generator: Map generation strategy name.
            seed: Random seed used when map data is generated.
            compass_activated: Whether compass hint should be enabled.
            proximity_activated: Whether proximity hint should be enabled.
            density_activated: Whether density hint should be enabled.

        Returns:
            GoldMineConfiguration: Configuration built from validated streamlit controls.
        """
        if n_rows < 1:
            raise ValueError("n_rows must be at least 1.")
        if n_cols < 1:
            raise ValueError("n_cols must be at least 1.")
        return GoldMineConfiguration(
            n_rows=n_rows,
            n_cols=n_cols,
            map_generator=map_generator,
            seed=seed,
            compass_activated=compass_activated,
            proximity_activated=proximity_activated,
            density_activated=density_activated,
        )

    def name(self) -> str:
        """Return the canonical game name."""
        return "goldmine"

    def _filter_candidates(
        self,
        requirements: Callable[[Any], bool],
        *candidates: type[Any],
    ) -> set[type[Any]]:
        """Return candidate classes accepted by `requirements`."""
        return {candidate for candidate in candidates if requirements(candidate)}

    def get_configurations(self, requirements: Callable[[Any], bool]) -> set[type[Configuration]]:
        """Return compatible configuration classes."""
        return self._filter_candidates(requirements, GoldMineConfiguration)

    def get_rules(self, requirements: Callable[[Any], bool]) -> set[type[Rules]]:
        """Return compatible rules classes."""
        return self._filter_candidates(requirements, GoldMineRules)

    def get_oracles(self, requirements: Callable[[Any], bool]) -> set[type[Oracle]]:
        """Return compatible oracle classes."""
        return self._filter_candidates(requirements, GoldMineOracle)

    def get_players(self, requirements: Callable[[Any], bool]) -> set[type[Player]]:
        """Return compatible player classes."""
        return self._filter_candidates(
            requirements,
            GoldMinePerfectPlayer,
            PolyvalentRandomPlayer,
            PolyvalentStreamlitPlayer,
            PolyvalentTerminalPlayer,
        )

    def get_renderers(self, requirements: Callable[[Any], bool]) -> set[type[View]]:
        """Return compatible renderer classes."""
        return self._filter_candidates(requirements, GoldMineTerminalView, GoldMineStreamlitView)

    def generate_rules(self, conf: Configuration) -> Rules:
        """Generate rules from one GoldMine configuration.

        Args:
            conf: Configuration object.

        Returns:
            Rules: Generated GoldMine rules.
        """
        if not isinstance(conf, GoldMineConfiguration):
            raise TypeError("conf must be an instance of GoldMineConfiguration.")
        return GoldMineRules(conf)
