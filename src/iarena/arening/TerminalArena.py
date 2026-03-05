"""Terminal-focused arena that renders rules, positions, and chosen movements."""

from __future__ import annotations

from collections.abc import Callable, Sequence

from iarena.arening.ArenaBehaviors import ArenaContext, ArenaTurnRecord, IArenaObserver, IArenaStopCondition
from iarena.arening.GenericArena import GenericArena
from iarena.interfacing.IGameRules import IGameRules
from iarena.interfacing.IMovement import IMovement
from iarena.interfacing.IPlayer import IPlayer, ITerminalPlayer
from iarena.interfacing.IPosition import IPosition
from iarena.interfacing.ScoreBoard import ScoreBoard
from iarena.utilizing.protocoling import as_text, supports_text_rendering

OutputFunction = Callable[[str], object]


class TerminalArena(GenericArena):
    """Arena implementation that prints game state for terminal play/debugging."""

    def __init__(
        self,
        rules: IGameRules,
        players: Sequence[IPlayer],
        position: IPosition | None = None,
        stop_conditions: Sequence[IArenaStopCondition] | None = None,
        observers: Sequence[IArenaObserver] | None = None,
        raise_on_stop: bool = True,
        output_function: OutputFunction = print,
    ) -> None:
        """Initialize terminal arena and validate text-rendering requirements.

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
        self._require_text_rendering(self.rules, value_name="rules")
        self._require_text_rendering(self.position, value_name="position")

    def _require_text_rendering(self, value: object, value_name: str) -> None:
        """Validate that one value implements the text-rendering protocol.

        Args:
            value: Value to validate.
            value_name: Friendly label used in error messages.

        Returns:
            None.
        """
        if not supports_text_rendering(value):
            raise TypeError(f"TerminalArena requires {value_name} to implement ITextRenderable")

    def _on_game_start(self, context: ArenaContext) -> None:
        """Print game rules when a terminal game starts.

        Args:
            context: Initial arena context.

        Returns:
            None.
        """
        self._output_function("Rules:")
        self._output_function(as_text(context.rules))

    def _on_turn_start(self, context: ArenaContext, player_index: int) -> None:
        """Print turn header and current position before requesting movement.

        Args:
            context: Current arena context.
            player_index: Index of player that must act now.

        Returns:
            None.
        """
        self._require_text_rendering(context.position, value_name="position")
        self._output_function(f"Turn {context.turn_count + 1}, player {player_index}")
        self._output_function(as_text(context.position))

    def _on_turn_end(self, turn_record: ArenaTurnRecord, context: ArenaContext) -> None:
        """Print selected movement after a turn has been applied.

        Args:
            turn_record: Data from the completed turn.
            context: Arena state after the completed turn.

        Returns:
            None.
        """
        del context
        self._require_text_rendering(turn_record.movement, value_name="movement")
        self._output_function(f"Player {turn_record.player_index} selected movement: {as_text(turn_record.movement)}")

    def _on_game_end(self, final_position: IPosition, final_score: ScoreBoard, reason: str | None) -> None:
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

    def _request_movement(self, player: IPlayer, player_index: int) -> IMovement:
        """Request one movement, preferring terminal-capable players when available.

        Args:
            player: Active player instance.
            player_index: Index of the active player.

        Returns:
            Movement selected by the active player.
        """
        if isinstance(player, ITerminalPlayer):
            return player.play_from_terminal(self.position)
        return super()._request_movement(player=player, player_index=player_index)
