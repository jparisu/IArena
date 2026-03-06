"""Terminal-focused arena that renders rules, positions, and chosen movements."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import cast

from iarena.arening.ArenaBehaviors import ArenaContext, ArenaTurnRecord, IArenaObserver, IArenaStopCondition
from iarena.arening.GenericArena import GenericArena
from iarena.desining.gaming.GameRules import GameRules
from iarena.desining.gaming.Position import Position
from iarena.desining.gaming.ScoreBoard import ScoreBoard
from iarena.desining.playing.Player import Player
from iarena.desining.visualing.TerminalGame import TerminalGame

OutputFunction = Callable[[str], object]


class TerminalArena(GenericArena):
    """Arena implementation that prints game state for terminal play/debugging."""

    def __init__(
        self,
        rules: GameRules,
        players: Sequence[Player],
        position: Position | None = None,
        stop_conditions: Sequence[IArenaStopCondition] | None = None,
        observers: Sequence[IArenaObserver] | None = None,
        raise_on_stop: bool = True,
        output_function: OutputFunction = print,
    ) -> None:
        """Initialize terminal arena and validate terminal-interface requirements.

        Args:
            rules: Rules object that defines game mechanics.
            players: Ordered players participating in the game.
            position: Optional initial position override.
            stop_conditions: Optional stop conditions evaluated each turn.
            observers: Optional arena lifecycle observers.
            raise_on_stop: Whether stop conditions raise ``ArenaStoppedError``.
            output_function: Writer used to emit terminal messages.

        Returns:
            None.
        """
        super().__init__(
            rules=rules,
            players=players,
            position=position,
            stop_conditions=stop_conditions,
            observers=observers,
            raise_on_stop=raise_on_stop,
        )
        self._output_function = output_function
        self._require_terminal_interface(self.rules, value_name="rules")

    def _require_terminal_interface(self, value: object, value_name: str) -> None:
        """Validate that one value implements the terminal-game protocol.

        Args:
            value: Value to validate.
            value_name: Friendly label used in error messages.

        Returns:
            None.
        """
        if not isinstance(value, TerminalGame):
            raise TypeError(f"TerminalArena requires {value_name} to implement TerminalGame")

    def _as_terminal_game(self, rules: GameRules) -> TerminalGame:
        """Return rules typed as terminal interface after runtime validation.

        Args:
            rules: Rules instance to validate.

        Returns:
            Same rules instance typed as ``TerminalGame``.
        """
        self._require_terminal_interface(rules, value_name="rules")
        return cast(TerminalGame, rules)

    def _on_game_start(self, context: ArenaContext) -> None:
        """Print game rules when a terminal game starts.

        Args:
            context: Initial arena context.

        Returns:
            None.
        """
        terminal_rules = self._as_terminal_game(context.rules)
        instructions = terminal_rules.terminal_instructions()
        if instructions is not None:
            self._output_function("Rules:")
            self._output_function(instructions)

    def _on_turn_start(self, context: ArenaContext, player_index: int) -> None:
        """Print turn header and current position before requesting movement.

        Args:
            context: Current arena context.
            player_index: Index of player that must act now.

        Returns:
            None.
        """
        terminal_rules = self._as_terminal_game(context.rules)
        self._output_function(f"Turn {context.turn_count + 1}, player {player_index}")
        self._output_function(terminal_rules.position_to_terminal(context.position))

    def _on_turn_end(self, turn_record: ArenaTurnRecord, context: ArenaContext) -> None:
        """Print selected movement after a turn has been applied.

        Args:
            turn_record: Data from the completed turn.
            context: Arena state after the completed turn.

        Returns:
            None.
        """
        terminal_rules = self._as_terminal_game(context.rules)
        movement_text = terminal_rules.movement_to_terminal(turn_record.movement)
        self._output_function(f"Player {turn_record.player_index} selected movement: {movement_text}")

    def _on_game_end(self, final_position: Position, final_score: ScoreBoard, reason: str | None) -> None:
        """Print final game result and optional early-stop reason.

        Args:
            final_position: Final game position.
            final_score: Final scoreboard.
            reason: Optional custom reason for ending early.

        Returns:
            None.
        """
        del final_position
        self._output_function("Game finished.")
        self._output_function(f"Final score: {final_score}")
        if reason is not None:
            self._output_function(f"End reason: {reason}")
