"""Declares the concrete game registry entry for TicTacToe."""
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

from iarena.gaming.tictactoe.TicTacToeConfiguration import TicTacToeConfiguration
from iarena.gaming.tictactoe.TicTacToeRules import TicTacToeRules
from iarena.gaming.tictactoe.TicTacToeStreamlitView import TicTacToeStreamlitView
from iarena.gaming.tictactoe.TicTacToeTerminalView import TicTacToeTerminalView
from iarena.playing.PolyvalentRandomPlayer import PolyvalentRandomPlayer
from iarena.playing.PolyvalentStreamlitPlayer import PolyvalentStreamlitPlayer
from iarena.playing.PolyvalentTerminalPlayer import PolyvalentTerminalPlayer


class TicTacToeGame(Game):
    """Concrete game registry implementation for TicTacToe.

    Purpose:
        Exposes TicTacToe-specific components through the generic `Game` discovery API.
    How it works:
        Filters and returns compatible TicTacToe configuration, rules, players, or views.
    Used for:
        Runtime game lookup, UI setup, and arena bootstrapping.
    Public Attributes:
        None declared at class level in this base definition.
    """

    _singleton: ClassVar[GenericSingleton[TicTacToeGame] | None] = None

    @classmethod
    def instance(cls) -> TicTacToeGame:
        """Return the singleton TicTacToe game instance.

        Returns:
            TicTacToeGame: Shared singleton instance of `TicTacToeGame`.
        """
        if cls._singleton is None:
            cls._singleton = GenericSingleton(cls)
        return cls._singleton()

    def default_configuration(self) -> TicTacToeConfiguration:
        """Return the default TicTacToe configuration for terminal quick-start flows.

        Returns:
            TicTacToeConfiguration: Default playable TicTacToe setup.
        """
        return TicTacToeConfiguration(board_size=3, win_length=3)

    def terminal_prompt_configuration(  # pylint: disable=too-complex  # TODO: review
        self,
        input_fnc: Callable[[str], str],
        output_fnc: Callable[[str], None],
    ) -> TicTacToeConfiguration:
        """Interactively request TicTacToe configuration values in terminal mode.

        Args:
            input_fnc: Input callable used to capture user text.
            output_fnc: Output callable used to display instructions and prompts.

        Returns:
            TicTacToeConfiguration: Configuration built from user-provided values.
        """
        output_fnc("Guided TicTacToe configuration.")

        while True:
            raw_size = input_fnc("Board size [3]: ").strip()
            if raw_size == "":
                board_size = 3
            else:
                try:
                    board_size = int(raw_size)
                except ValueError:
                    output_fnc("Invalid value. Board size must be an integer.")
                    continue

            if board_size < 1:
                output_fnc("Board size must be at least 1.")
                continue
            break

        while True:
            raw_win_length = input_fnc(f"Win length [{board_size}]: ").strip()
            if raw_win_length == "":
                win_length = board_size
            else:
                try:
                    win_length = int(raw_win_length)
                except ValueError:
                    output_fnc("Invalid value. Win length must be an integer.")
                    continue

            if win_length < 1:
                output_fnc("Win length must be at least 1.")
                continue
            if win_length > board_size:
                output_fnc("Win length must be less than or equal to board size.")
                continue
            break

        return TicTacToeConfiguration(board_size=board_size, win_length=win_length)

    def streamlit_prompt_configuration(self, board_size: int = 3, win_length: int = 3) -> TicTacToeConfiguration:
        """Build a TicTacToe configuration from streamlit-oriented control values.

        Args:
            board_size: Side size of the square board.
            win_length: Number of aligned symbols required to win.

        Returns:
            TicTacToeConfiguration: Configuration built from validated streamlit controls.
        """
        if board_size < 1:
            raise ValueError("board_size must be at least 1.")
        if win_length < 1:
            raise ValueError("win_length must be at least 1.")
        if win_length > board_size:
            raise ValueError("win_length must be less than or equal to board_size.")
        return TicTacToeConfiguration(board_size=board_size, win_length=win_length)

    def name(self) -> str:
        """Return the canonical game name used in registries and UI selectors.

        Returns:
            str: Stable human-readable identifier for this game.
        """
        return "tictactoe"

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
        """Return supported TicTacToe configuration classes satisfying requirements.

        Args:
            requirements: Predicate used to filter candidate component classes.

        Returns:
            set[type[Configuration]]: Set of compatible configuration classes.
        """
        return self._filter_candidates(requirements, TicTacToeConfiguration)

    def get_rules(self, requirements: Callable[[Any], bool]) -> set[type[Rules]]:
        """Return supported TicTacToe rules classes satisfying requirements.

        Args:
            requirements: Predicate used to filter candidate component classes.

        Returns:
            set[type[Rules]]: Set of compatible rules classes.
        """
        return self._filter_candidates(requirements, TicTacToeRules)

    def get_oracles(self, requirements: Callable[[Any], bool]) -> set[type[Oracle]]:
        """Return supported TicTacToe oracle classes satisfying requirements.

        Args:
            requirements: Predicate used to filter candidate component classes.

        Returns:
            set[type[Oracle]]: Set of compatible oracle classes.
        """
        _ = requirements
        return set()

    def get_players(self, requirements: Callable[[Any], bool]) -> set[type[Player]]:
        """Return supported TicTacToe player classes satisfying requirements.

        Args:
            requirements: Predicate used to filter candidate component classes.

        Returns:
            set[type[Player]]: Set of compatible player classes.
        """
        return self._filter_candidates(
            requirements,
            PolyvalentTerminalPlayer,
            PolyvalentStreamlitPlayer,
            PolyvalentRandomPlayer,
        )

    def get_renderers(self, requirements: Callable[[Any], bool]) -> set[type[View]]:
        """Return supported TicTacToe renderer classes satisfying requirements.

        Args:
            requirements: Predicate used to filter candidate component classes.

        Returns:
            set[type[View]]: Set of compatible renderer classes.
        """
        return self._filter_candidates(requirements, TicTacToeTerminalView, TicTacToeStreamlitView)

    def generate_rules(self, conf: Configuration) -> Rules:
        """Generate one TicTacToe rules instance from a concrete configuration.

        Args:
            conf: Configuration object describing the board setup.

        Returns:
            Rules: Rules engine initialized from the provided configuration.
        """
        if not isinstance(conf, TicTacToeConfiguration):
            raise TypeError("conf must be an instance of TicTacToeConfiguration.")
        return TicTacToeRules(conf)
