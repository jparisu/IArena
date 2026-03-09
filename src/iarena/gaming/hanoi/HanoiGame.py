"""Declares the concrete game registry entry for Hanoi."""
# pylint: disable=too-many-lines  # TODO: review

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

from iarena.gaming.hanoi.HanoiConfiguration import HanoiConfiguration
from iarena.gaming.hanoi.HanoiOracle import HanoiOracle
from iarena.gaming.hanoi.HanoiRules import HanoiRules
from iarena.gaming.hanoi.HanoiStreamlitView import HanoiStreamlitView
from iarena.gaming.hanoi.HanoiTerminalView import HanoiTerminalView
from iarena.gaming.hanoi.PerfectHanoiPlayer import PerfectHanoiPlayer
from iarena.playing.PolyvalentRandomPlayer import PolyvalentRandomPlayer
from iarena.playing.PolyvalentStreamlitPlayer import PolyvalentStreamlitPlayer
from iarena.playing.PolyvalentTerminalPlayer import PolyvalentTerminalPlayer


class HanoiGame(Game):
    """Concrete game registry implementation for Hanoi.

    Purpose:
        Exposes Hanoi-specific components through the generic `Game` discovery API.
    How it works:
        Filters and returns compatible Hanoi configuration, rules, players, or views.
    Used for:
        Runtime game lookup, UI setup, and arena bootstrapping.
    Public Attributes:
        None declared at class level in this base definition.
    """

    _singleton: ClassVar[GenericSingleton[HanoiGame] | None] = None

    @classmethod
    def instance(cls) -> HanoiGame:
        """Return the singleton Hanoi game instance.

        Returns:
            HanoiGame: Shared singleton instance of `HanoiGame`.
        """
        if cls._singleton is None:
            cls._singleton = GenericSingleton(cls)
        return cls._singleton()

    def default_configuration(self) -> HanoiConfiguration:
        """Return the default Hanoi configuration for terminal quick-start flows.

        Returns:
            HanoiConfiguration: Default playable Hanoi setup.
        """
        return HanoiConfiguration(n_pegs=3, disks=[0, 0, 0])

    def terminal_prompt_configuration(  # pylint: disable=too-complex  # TODO: review
        self,
        input_fnc: Callable[[str], str],
        output_fnc: Callable[[str], None],
    ) -> HanoiConfiguration:
        """Interactively request Hanoi configuration values in terminal mode.

        Args:
            input_fnc: Input callable used to capture user text.
            output_fnc: Output callable used to display instructions and prompts.

        Returns:
            HanoiConfiguration: Configuration built from user-provided values.
        """
        output_fnc("Guided Hanoi configuration.")

        while True:
            raw_pegs = input_fnc("Number of pegs [3]: ").strip()
            if raw_pegs == "":
                n_pegs = 3
            else:
                try:
                    n_pegs = int(raw_pegs)
                except ValueError:
                    output_fnc("Invalid value. Number of pegs must be an integer.")
                    continue

            if n_pegs < 2:
                output_fnc("Number of pegs must be at least 2.")
                continue
            break

        while True:
            raw_disks = input_fnc("Number of disks [3]: ").strip()
            if raw_disks == "":
                n_disks = 3
            else:
                try:
                    n_disks = int(raw_disks)
                except ValueError:
                    output_fnc("Invalid value. Number of disks must be an integer.")
                    continue

            if n_disks < 0:
                output_fnc("Number of disks must be non-negative.")
                continue
            break

        return HanoiConfiguration(n_pegs=n_pegs, disks=[0] * n_disks)

    def streamlit_prompt_configuration(self, n_pegs: int = 3, n_disks: int = 3) -> HanoiConfiguration:
        """Build a Hanoi configuration from streamlit-oriented control values.

        Args:
            n_pegs: Number of puzzle pegs requested by the user.
            n_disks: Number of puzzle disks requested by the user.

        Returns:
            HanoiConfiguration: Configuration built from validated streamlit controls.
        """
        if n_pegs < 2:
            raise ValueError("Number of pegs must be at least 2.")
        if n_disks < 0:
            raise ValueError("Number of disks must be non-negative.")
        return HanoiConfiguration(n_pegs=n_pegs, disks=[0] * n_disks)

    def name(self) -> str:
        """Return the canonical game name used in registries and UI selectors.

        Returns:
            str: Stable human-readable identifier for this game.
        """
        return "hanoi"

    def _filter_candidates(
        self,
        requirements: Callable[[Any], bool],
        *candidates: type[Any],
    ) -> set[type[Any]]:
        """Return candidate classes accepted by the provided predicate.

        Args:
            requirements: Predicate used to keep or discard class candidates.
            *candidates: Candidate classes to evaluate.

        Returns:
            Set of accepted class objects.
        """
        return {candidate for candidate in candidates if requirements(candidate)}

    def get_configurations(self, requirements: Callable[[Any], bool]) -> set[type[Configuration]]:
        """Return supported Hanoi configuration classes satisfying requirements.

        Args:
            requirements: Predicate used to filter candidate component classes.

        Returns:
            set[type[Configuration]]: Set of compatible configuration classes.
        """
        return self._filter_candidates(requirements, HanoiConfiguration)

    def get_rules(self, requirements: Callable[[Any], bool]) -> set[type[Rules]]:
        """Return supported Hanoi rules classes satisfying requirements.

        Args:
            requirements: Predicate used to filter candidate component classes.

        Returns:
            set[type[Rules]]: Set of compatible rules classes.
        """
        return self._filter_candidates(requirements, HanoiRules)

    def get_oracles(self, requirements: Callable[[Any], bool]) -> set[type[Oracle]]:
        """Return supported Hanoi oracle classes satisfying requirements.

        Args:
            requirements: Predicate used to filter candidate component classes.

        Returns:
            set[type[Oracle]]: Set of compatible oracle classes.
        """
        return self._filter_candidates(requirements, HanoiOracle)

    def get_players(self, requirements: Callable[[Any], bool]) -> set[type[Player]]:
        """Return supported Hanoi player classes satisfying requirements.

        Args:
            requirements: Predicate used to filter candidate component classes.

        Returns:
            set[type[Player]]: Set of compatible player classes.
        """
        return self._filter_candidates(
            requirements,
            PerfectHanoiPlayer,
            PolyvalentStreamlitPlayer,
            PolyvalentTerminalPlayer,
            PolyvalentRandomPlayer,
        )

    def get_renderers(self, requirements: Callable[[Any], bool]) -> set[type[View]]:
        """Return supported Hanoi renderer classes satisfying requirements.

        Args:
            requirements: Predicate used to filter candidate component classes.

        Returns:
            set[type[View]]: Set of compatible renderer classes.
        """
        return self._filter_candidates(requirements, HanoiTerminalView, HanoiStreamlitView)

    def generate_rules(self, conf: Configuration) -> Rules:
        """Generate one Hanoi rules instance from a concrete configuration.

        Args:
            conf: Configuration object describing the puzzle setup.

        Returns:
            Rules: Rules engine initialized from the provided configuration.
        """
        if not isinstance(conf, HanoiConfiguration):
            raise TypeError("conf must be an instance of HanoiConfiguration.")
        return HanoiRules(conf)
