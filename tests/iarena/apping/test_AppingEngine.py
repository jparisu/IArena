"""Tests for apping execution and replay helpers."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass

import pytest

from iarena.apping.AppingEngine import (
    PlaybackController,
    load_player_class_from_python_source,
    read_uploaded_python_source,
    run_single_player_optimization_game,
)
from iarena.interfacing.IGameRules import IGameRules
from iarena.interfacing.IMovement import IMovement
from iarena.interfacing.IPlayer import IPlayer
from iarena.interfacing.IPosition import IPosition
from iarena.interfacing.ScoreBoard import ScoreBoard


@dataclass(frozen=True, slots=True)
class DummyMovement(IMovement):
    """Simple movement with additive score value."""

    value: float


@dataclass(frozen=True, slots=True)
class DummyPosition(IPosition):
    """Position used for replay tests."""

    turns: int
    score: float

    def next_player(self) -> int:
        """Return active player index.

        Args:
            None.

        Returns:
            Always ``0``.
        """
        return 0


class DummyRules(IGameRules):
    """Deterministic single-player rules for replay tests."""

    def __init__(self, max_turns: int, n_players: int = 1) -> None:
        """Initialize deterministic rules.

        Args:
            max_turns: Turn cap that ends the game.
            n_players: Number of players reported by the rules.

        Returns:
            None.
        """
        self._max_turns = max_turns
        self._n_players = n_players

    def n_players(self) -> int:
        """Return number of players.

        Args:
            None.

        Returns:
            Configured number of players.
        """
        return self._n_players

    def first_position(self) -> IPosition:
        """Return initial position.

        Args:
            None.

        Returns:
            Position with zero score and turns.
        """
        return DummyPosition(turns=0, score=0.0)

    def next_position(self, movement: IMovement, position: IPosition) -> IPosition:
        """Apply movement to build next position.

        Args:
            movement: Movement selected by player.
            position: Current position.

        Returns:
            Successor position.
        """
        if not isinstance(movement, DummyMovement):
            raise TypeError("movement must be DummyMovement")
        if not isinstance(position, DummyPosition):
            raise TypeError("position must be DummyPosition")
        return DummyPosition(turns=position.turns + 1, score=position.score + movement.value)

    def possible_movements(self, position: IPosition) -> Iterator[IMovement]:
        """Yield legal movement options.

        Args:
            position: Current position.

        Returns:
            Iterator with one legal movement.
        """
        del position
        yield DummyMovement(value=1.0)

    def finished(self, position: IPosition) -> bool:
        """Return whether game reached turn cap.

        Args:
            position: Current position.

        Returns:
            ``True`` when position turns are at least max turns.
        """
        if not isinstance(position, DummyPosition):
            raise TypeError("position must be DummyPosition")
        return position.turns >= self._max_turns

    def score(self, position: IPosition) -> ScoreBoard:
        """Return scoreboard from position score.

        Args:
            position: Current position.

        Returns:
            One-player scoreboard.
        """
        if not isinstance(position, DummyPosition):
            raise TypeError("position must be DummyPosition")
        board = ScoreBoard(1)
        board.define_score(0, position.score)
        return board


class DummyPlayer(IPlayer):
    """Player that always returns one deterministic movement."""

    def play(self, position: IPosition) -> IMovement:
        """Return one deterministic movement.

        Args:
            position: Current position.

        Returns:
            Deterministic movement.
        """
        del position
        return DummyMovement(value=1.0)


class _FakeUploadGetValue:
    """Fake uploaded file exposing ``getvalue``."""

    def __init__(self, value: bytes) -> None:
        """Initialize fake uploaded object.

        Args:
            value: Raw value returned by ``getvalue``.

        Returns:
            None.
        """
        self._value = value

    def getvalue(self) -> bytes:
        """Return configured raw value.

        Args:
            None.

        Returns:
            Raw byte payload.
        """
        return self._value


class _FakeUploadRead:
    """Fake uploaded file exposing ``read``."""

    def __init__(self, value: str) -> None:
        """Initialize fake uploaded object.

        Args:
            value: Raw value returned by ``read``.

        Returns:
            None.
        """
        self._value = value

    def read(self) -> str:
        """Return configured raw value.

        Args:
            None.

        Returns:
            Raw string payload.
        """
        return self._value


def test_playback_controller_navigation_and_progress() -> None:
    """Controller should manage play, seek, and progress operations.

    Args:
        None.

    Returns:
        None.
    """
    controller = PlaybackController(total_frames=4)

    assert controller.total_frames() == 4
    assert controller.current_index() == 0
    assert controller.progress_ratio() == 0.0

    controller.play()
    assert controller.is_playing() is True
    assert controller.step_forward() == 1
    assert controller.step_backward() == 0
    assert controller.seek(3) == 3
    assert controller.is_playing() is False
    assert controller.progress_ratio() == 1.0

    controller.reset()
    assert controller.current_index() == 0
    assert controller.is_playing() is False


def test_playback_controller_validates_bounds() -> None:
    """Controller should reject invalid constructor and seek values.

    Args:
        None.

    Returns:
        None.
    """
    with pytest.raises(ValueError):
        PlaybackController(total_frames=0)
    with pytest.raises(IndexError):
        PlaybackController(total_frames=3, current_index=3)

    controller = PlaybackController(total_frames=3)
    with pytest.raises(IndexError):
        controller.seek(-1)
    with pytest.raises(IndexError):
        controller.seek(3)


def test_load_player_class_from_python_source() -> None:
    """Source loader should return uploaded ``IPlayer`` subclasses.

    Args:
        None.

    Returns:
        None.
    """
    loaded_class = load_player_class_from_python_source(
        "\n".join(
            [
                "class UploadedPlayer(IPlayer):",
                "    def play(self, position):",
                "        del position",
                "        return object()",
            ]
        )
    )

    assert issubclass(loaded_class, IPlayer)

    with pytest.raises(ValueError):
        load_player_class_from_python_source("class NotAPlayer:\n    pass")


def test_read_uploaded_python_source_supports_multiple_input_shapes() -> None:
    """Upload source reader should handle strings, bytes, and file-like wrappers.

    Args:
        None.

    Returns:
        None.
    """
    assert read_uploaded_python_source("print('a')") == "print('a')"
    assert read_uploaded_python_source(b"print('b')") == "print('b')"
    assert read_uploaded_python_source(_FakeUploadGetValue(b"print('c')")) == "print('c')"
    assert read_uploaded_python_source(_FakeUploadRead("print('d')")) == "print('d')"

    with pytest.raises(TypeError):
        read_uploaded_python_source(object())


def test_run_single_player_optimization_game_builds_replay_frames() -> None:
    """Single-player execution helper should create full replay information.

    Args:
        None.

    Returns:
        None.
    """
    rules = DummyRules(max_turns=3, n_players=1)
    replay = run_single_player_optimization_game(rules=rules, player=DummyPlayer(), turn_limit=20)

    assert replay.total_turns() == 3
    assert replay.frame_at(0).turn_index == 0
    assert replay.frame_at(3).movement_to_next is None
    assert replay.final_score.get_score(0) == 3.0
    assert replay.end_reason is None


def test_run_single_player_optimization_game_requires_one_player_rules() -> None:
    """Single-player execution helper should reject multiplayer rules.

    Args:
        None.

    Returns:
        None.
    """
    with pytest.raises(ValueError):
        run_single_player_optimization_game(rules=DummyRules(max_turns=1, n_players=2), player=DummyPlayer())
