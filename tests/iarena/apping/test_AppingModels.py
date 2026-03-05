"""Tests for apping data models."""

from __future__ import annotations

from collections.abc import Iterator, Mapping
from dataclasses import dataclass

import pytest

from iarena.apping.AppingModels import (
    OptimizationGamePage,
    OptimizationReplay,
    OptimizationReplayFrame,
)
from iarena.interfacing.IGameRules import IGameRules
from iarena.interfacing.IMovement import IMovement
from iarena.interfacing.IPlayer import IPlayer
from iarena.interfacing.IPosition import IPosition
from iarena.interfacing.ScoreBoard import ScoreBoard


@dataclass(frozen=True, slots=True)
class DummyMovement(IMovement):
    """Simple movement for apping model tests."""

    amount: float


@dataclass(frozen=True, slots=True)
class DummyPosition(IPosition):
    """Simple position with turn count."""

    turns: int

    def next_player(self) -> int:
        """Return active player index.

        Args:
            None.

        Returns:
            Always ``0``.
        """
        return 0


class DummyRules(IGameRules):
    """Deterministic one-player rules for apping model tests."""

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
            Initial dummy position.
        """
        return DummyPosition(turns=0)

    def next_position(self, movement: IMovement, position: IPosition) -> IPosition:
        """Apply movement by incrementing turn count.

        Args:
            movement: Movement to apply.
            position: Current position.

        Returns:
            Successor position.
        """
        del movement
        if not isinstance(position, DummyPosition):
            raise TypeError("position must be DummyPosition")
        return DummyPosition(turns=position.turns + 1)

    def possible_movements(self, position: IPosition) -> Iterator[IMovement]:
        """Yield the only legal movement.

        Args:
            position: Current position.

        Returns:
            Iterator with one movement.
        """
        del position
        yield DummyMovement(amount=1.0)

    def finished(self, position: IPosition) -> bool:
        """Return whether game reached two turns.

        Args:
            position: Current position.

        Returns:
            ``True`` when turns are at least ``2``.
        """
        if not isinstance(position, DummyPosition):
            raise TypeError("position must be DummyPosition")
        return position.turns >= 2

    def score(self, position: IPosition) -> ScoreBoard:
        """Return current score as negative turn count.

        Args:
            position: Current position.

        Returns:
            Scoreboard with one score.
        """
        if not isinstance(position, DummyPosition):
            raise TypeError("position must be DummyPosition")
        board = ScoreBoard(1)
        board.define_score(0, float(-position.turns))
        return board


class FixedMovementPlayer(IPlayer):
    """Player that always returns one fixed movement."""

    def __init__(self, movement: DummyMovement) -> None:
        """Initialize player with fixed movement.

        Args:
            movement: Movement returned by ``play``.

        Returns:
            None.
        """
        super().__init__(name="FixedMovementPlayer")
        self._movement = movement

    def play(self, position: IPosition) -> IMovement:
        """Return configured movement.

        Args:
            position: Current position.

        Returns:
            Fixed movement.
        """
        del position
        return self._movement


def _build_replay() -> OptimizationReplay:
    """Build one deterministic replay object for model tests.

    Args:
        None.

    Returns:
        Replay with three frames.
    """
    movement = DummyMovement(amount=1.0)
    rules = DummyRules()
    position_0 = rules.first_position()
    position_1 = rules.next_position(movement=movement, position=position_0)
    position_2 = rules.next_position(movement=movement, position=position_1)
    frames = (
        OptimizationReplayFrame(
            turn_index=0,
            position=position_0,
            score=rules.current_score(position_0),
            movement_to_next=movement,
        ),
        OptimizationReplayFrame(
            turn_index=1,
            position=position_1,
            score=rules.current_score(position_1),
            movement_to_next=movement,
        ),
        OptimizationReplayFrame(
            turn_index=2,
            position=position_2,
            score=rules.current_score(position_2),
            movement_to_next=None,
        ),
    )
    return OptimizationReplay(rules=rules, frames=frames, final_score=rules.current_score(position_2), end_reason=None)


def test_replay_total_turns_and_frame_access() -> None:
    """Replay should expose turn count and indexed frame access.

    Args:
        None.

    Returns:
        None.
    """
    replay = _build_replay()

    assert replay.total_turns() == 2
    assert replay.frame_at(1).turn_index == 1


def test_replay_frame_access_validates_bounds() -> None:
    """Frame accessor should reject out-of-range indexes.

    Args:
        None.

    Returns:
        None.
    """
    replay = _build_replay()

    with pytest.raises(IndexError):
        replay.frame_at(-1)
    with pytest.raises(IndexError):
        replay.frame_at(3)


def test_game_page_includes_default_random_and_extra_players() -> None:
    """Game page should expose default/random players plus custom factories.

    Args:
        None.

    Returns:
        None.
    """
    movement = DummyMovement(amount=1.0)

    def render_configuration(container: object) -> Mapping[str, object]:
        """Return fixed configuration.

        Args:
            container: Unused Streamlit-like container.

        Returns:
            Empty configuration.
        """
        del container
        return {}

    def build_rules(values: Mapping[str, object]) -> DummyRules:
        """Return deterministic rules.

        Args:
            values: Unused configuration values.

        Returns:
            One-player dummy rules.
        """
        del values
        return DummyRules()

    def render_position(container: object, view_state: object) -> None:
        """No-op renderer used by the test page.

        Args:
            container: Unused Streamlit-like container.
            view_state: Unused frame state.

        Returns:
            None.
        """
        del container, view_state

    page = OptimizationGamePage(
        key="dummy",
        title="Dummy",
        render_configuration=render_configuration,
        build_rules=build_rules,
        render_position=render_position,
        default_player_factory=lambda: FixedMovementPlayer(movement=movement),
        extra_player_factories={"Fixed": lambda: FixedMovementPlayer(movement=movement)},
    )

    factories = page.available_player_factories()

    assert set(factories) == {"Game default", "Random", "Visual (generic)", "Fixed"}
    assert isinstance(factories["Game default"](), FixedMovementPlayer)
    assert isinstance(factories["Fixed"](), FixedMovementPlayer)
