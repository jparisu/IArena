"""Execution and replay helpers for Streamlit-based optimization games."""

from __future__ import annotations

from iarena.apping.AppingModels import OptimizationReplay, OptimizationReplayFrame
from iarena.arening.ArenaBehaviors import clone_score_board
from iarena.arening.ArenaFactory import ArenaFactory
from iarena.interfacing.IGameRules import IGameRules
from iarena.interfacing.IPlayer import IPlayer


class PlaybackController:
    """Track replay playback state for interactive UI controls."""

    def __init__(self, total_frames: int, current_index: int = 0) -> None:
        """Initialize playback state.

        Args:
            total_frames: Number of available replay frames.
            current_index: Initial active frame index.

        Returns:
            None.
        """
        if total_frames <= 0:
            raise ValueError("total_frames must be >= 1")
        if current_index < 0 or current_index >= total_frames:
            raise IndexError(f"current_index {current_index} out of range [0, {total_frames - 1}]")
        self._total_frames = total_frames
        self._current_index = current_index
        self._is_playing = False

    def total_frames(self) -> int:
        """Return number of frames tracked by this controller.

        Args:
            None.

        Returns:
            Number of frames.
        """
        return self._total_frames

    def current_index(self) -> int:
        """Return active replay frame index.

        Args:
            None.

        Returns:
            Active frame index.
        """
        return self._current_index

    def is_playing(self) -> bool:
        """Return whether autoplay is active.

        Args:
            None.

        Returns:
            ``True`` when autoplay is active.
        """
        return self._is_playing

    def play(self) -> None:
        """Enable autoplay mode.

        Args:
            None.

        Returns:
            None.
        """
        self._is_playing = self._current_index < (self._total_frames - 1)

    def pause(self) -> None:
        """Disable autoplay mode.

        Args:
            None.

        Returns:
            None.
        """
        self._is_playing = False

    def reset(self) -> None:
        """Move replay to first frame and disable autoplay.

        Args:
            None.

        Returns:
            None.
        """
        self._current_index = 0
        self._is_playing = False

    def step_forward(self) -> int:
        """Advance one frame when possible.

        Args:
            None.

        Returns:
            New active frame index.
        """
        if self._current_index < (self._total_frames - 1):
            self._current_index += 1
        if self._current_index >= (self._total_frames - 1):
            self._is_playing = False
        return self._current_index

    def step_backward(self) -> int:
        """Go back one frame when possible.

        Args:
            None.

        Returns:
            New active frame index.
        """
        if self._current_index > 0:
            self._current_index -= 1
        return self._current_index

    def seek(self, frame_index: int) -> int:
        """Jump to one specific frame index.

        Args:
            frame_index: Target frame index.

        Returns:
            New active frame index.
        """
        if frame_index < 0 or frame_index >= self._total_frames:
            raise IndexError(f"frame index {frame_index} out of range [0, {self._total_frames - 1}]")
        self._current_index = frame_index
        if self._current_index >= (self._total_frames - 1):
            self._is_playing = False
        return self._current_index

    def progress_ratio(self) -> float:
        """Return playback progress in ``[0.0, 1.0]``.

        Args:
            None.

        Returns:
            Playback progress ratio.
        """
        if self._total_frames == 1:
            return 1.0
        return self._current_index / float(self._total_frames - 1)


def load_player_class_from_python_source(source_code: str) -> type[IPlayer]:
    """Load the first ``IPlayer`` subclass defined in source code.

    Args:
        source_code: Python source code containing one or more class
            definitions.

    Returns:
        First discovered ``IPlayer`` subclass.
    """
    execution_namespace: dict[str, object] = {"__builtins__": __builtins__, "IPlayer": IPlayer}
    exec(source_code, execution_namespace)  # noqa: S102

    player_classes: list[type[IPlayer]] = []
    for value in execution_namespace.values():
        if isinstance(value, type) and issubclass(value, IPlayer) and value is not IPlayer:
            player_classes.append(value)

    if not player_classes:
        raise ValueError("uploaded source must define at least one IPlayer subclass")
    return player_classes[0]


def read_uploaded_python_source(uploaded_file: object) -> str:
    """Read UTF-8 source text from one uploaded Streamlit file object.

    Args:
        uploaded_file: Streamlit uploaded-file object, bytes, or plain string.

    Returns:
        Decoded Python source text.
    """
    if isinstance(uploaded_file, str):
        return uploaded_file
    if isinstance(uploaded_file, bytes):
        return uploaded_file.decode("utf-8")

    if hasattr(uploaded_file, "getvalue"):
        raw_value = uploaded_file.getvalue()
    elif hasattr(uploaded_file, "read"):
        raw_value = uploaded_file.read()
    else:
        raise TypeError("uploaded_file must provide getvalue() or read()")

    if isinstance(raw_value, bytes):
        return raw_value.decode("utf-8")
    if isinstance(raw_value, str):
        return raw_value
    raise TypeError("uploaded_file content must be bytes or str")


def run_single_player_optimization_game(
    rules: IGameRules,
    player: IPlayer,
    turn_limit: int | None = 5_000,
) -> OptimizationReplay:
    """Run one single-player game and store frame-by-frame replay data.

    Args:
        rules: Rules object for the game.
        player: Player instance used for the only player slot.
        turn_limit: Optional maximum number of turns before early stop.

    Returns:
        Replay data ready to be consumed by Streamlit UI.
    """
    if rules.n_players() != 1:
        raise ValueError(f"run_single_player_optimization_game requires n_players() == 1, got {rules.n_players()}")

    arena = ArenaFactory.build(
        rules=rules,
        players=[player],
        turn_limit=turn_limit,
        store_information=True,
        raise_on_stop=False,
    )
    final_score = arena.play()
    record = arena.game_record()
    if record is None:
        raise RuntimeError("arena did not provide game history despite store_information=True")

    positions = record.positions()
    movements = record.movements()
    frames: list[OptimizationReplayFrame] = []
    for frame_index, position in enumerate(positions):
        movement_to_next = movements[frame_index] if frame_index < len(movements) else None
        frames.append(
            OptimizationReplayFrame(
                turn_index=frame_index,
                position=position,
                score=clone_score_board(rules.current_score(position)),
                movement_to_next=movement_to_next,
            )
        )

    return OptimizationReplay(
        rules=rules,
        frames=tuple(frames),
        final_score=clone_score_board(final_score),
        end_reason=record.end_reason,
    )
