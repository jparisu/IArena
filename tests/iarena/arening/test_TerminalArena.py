"""Tests for terminal-focused arena behavior."""

from __future__ import annotations

from collections.abc import Iterator

import pytest

from iarena.arening.TerminalArena import TerminalArena
from iarena.interfacing.IGameRules import IGameRules
from iarena.interfacing.IMovement import IMovement
from iarena.interfacing.IPosition import IPosition
from iarena.interfacing.ScoreBoard import ScoreBoard
from ._dummy_game import DummyMovement, DummyRules, TerminalCapablePlayer


class NonTextPosition(IPosition):
    """Position class that does not implement text-rendering protocol."""

    def next_player(self) -> int:
        """Return next player index.

        Args:
            None.

        Returns:
            Always ``0``.
        """
        return 0


class NonTextRules(IGameRules):
    """Rules class that does not implement text-rendering protocol."""

    def n_players(self) -> int:
        """Return number of players.

        Args:
            None.

        Returns:
            Always ``1``.
        """
        return 1

    def first_position(self) -> IPosition:
        """Return initial position.

        Args:
            None.

        Returns:
            Position without text rendering.
        """
        return NonTextPosition()

    def next_position(self, movement: IMovement, position: IPosition) -> IPosition:
        """Return unchanged position.

        Args:
            movement: Unused movement.
            position: Current position.

        Returns:
            Same position.
        """
        del movement
        return position

    def possible_movements(self, position: IPosition) -> Iterator[IMovement]:
        """Yield legal movements.

        Args:
            position: Current position.

        Returns:
            Empty iterator.
        """
        del position
        return iter(())

    def finished(self, position: IPosition) -> bool:
        """Return whether the game is finished.

        Args:
            position: Current position.

        Returns:
            Always ``True``.
        """
        del position
        return True

    def score(self, position: IPosition) -> ScoreBoard:
        """Build score board for one player.

        Args:
            position: Current position.

        Returns:
            Zero scoreboard.
        """
        del position
        return ScoreBoard(1)


def test_terminal_arena_requires_text_renderable_rules() -> None:
    """Terminal arena should reject rules without text rendering support.

    Args:
        None.

    Returns:
        None.
    """
    rules = NonTextRules()
    players = [TerminalCapablePlayer(movement=DummyMovement(label="inc", amount=1.0))]

    with pytest.raises(TypeError):
        TerminalArena(rules=rules, players=players)


def test_terminal_arena_prints_state_and_uses_terminal_player_entrypoint() -> None:
    """Terminal arena should render text and prefer terminal-capable player hook.

    Args:
        None.

    Returns:
        None.
    """
    outputs: list[str] = []
    movement = DummyMovement(label="inc", amount=1.0)
    rules = DummyRules(n_players=1, max_turns=1, allowed_movements=(movement,))
    player = TerminalCapablePlayer(movement=movement)
    arena = TerminalArena(
        rules=rules,
        players=[player],
        output_function=outputs.append,
    )

    result = arena.play()

    assert result.get_score(0) == 1.0
    assert player.terminal_calls == 1
    assert any(line.startswith("Rules:") for line in outputs)
    assert any(line.startswith("Turn 1") for line in outputs)
    assert any("selected movement" in line for line in outputs)
