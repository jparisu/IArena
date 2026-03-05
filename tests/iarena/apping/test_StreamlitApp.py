"""Tests for generic Streamlit apping render helpers."""

from __future__ import annotations

from collections.abc import Iterator, Mapping
from dataclasses import dataclass
from typing import Any, cast

import pytest

from iarena.apping.AppingEngine import PlaybackController, run_single_player_optimization_game
from iarena.apping.AppingModels import OptimizationGamePage, OptimizationViewState
from iarena.apping.StreamlitApp import (
    StreamlitGameIndex,
    build_default_game_index,
    render_games_index_page,
    render_single_player_optimization_page,
)
from iarena.interfacing.IGameRules import IGameRules
from iarena.interfacing.IMovement import IMovement
from iarena.interfacing.IPlayer import IPlayer
from iarena.interfacing.IPosition import IPosition
from iarena.interfacing.ScoreBoard import ScoreBoard


@dataclass(frozen=True, slots=True)
class DummyMovement(IMovement):
    """Simple movement with one numeric value."""

    value: float


@dataclass(frozen=True, slots=True)
class DummyPosition(IPosition):
    """Simple position used by Streamlit app tests."""

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
    """Simple one-player rules for Streamlit app tests."""

    def __init__(self, max_turns: int = 2) -> None:
        """Initialize deterministic rules.

        Args:
            max_turns: Turn count that ends the game.

        Returns:
            None.
        """
        self._max_turns = max_turns

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
            Position with zero turns and score.
        """
        return DummyPosition(turns=0, score=0.0)

    def next_position(self, movement: IMovement, position: IPosition) -> IPosition:
        """Apply movement and return successor position.

        Args:
            movement: Movement selected by player.
            position: Current position.

        Returns:
            Successor position.
        """
        if not isinstance(position, DummyPosition):
            raise TypeError("position must be DummyPosition")
        gain = float(getattr(movement, "value", 1.0))
        return DummyPosition(turns=position.turns + 1, score=position.score + gain)

    def possible_movements(self, position: IPosition) -> Iterator[IMovement]:
        """Yield legal movements.

        Args:
            position: Current position.

        Returns:
            Iterator with one movement.
        """
        del position
        yield DummyMovement(value=1.0)

    def finished(self, position: IPosition) -> bool:
        """Return whether game reached turn cap.

        Args:
            position: Current position.

        Returns:
            ``True`` when turn count reaches max.
        """
        if not isinstance(position, DummyPosition):
            raise TypeError("position must be DummyPosition")
        return position.turns >= self._max_turns

    def score(self, position: IPosition) -> ScoreBoard:
        """Return scoreboard from current position score.

        Args:
            position: Current position.

        Returns:
            Scoreboard for one player.
        """
        if not isinstance(position, DummyPosition):
            raise TypeError("position must be DummyPosition")
        board = ScoreBoard(1)
        board.define_score(0, position.score)
        return board

    def is_movement_possible(self, movement: IMovement, position: IPosition) -> bool:
        """Accept any movement object.

        Args:
            movement: Movement to evaluate.
            position: Current position.

        Returns:
            Always ``True``.
        """
        del movement, position
        return True


class DummyPlayer(IPlayer):
    """Player returning movement with fixed value."""

    def __init__(self, value: float = 1.0) -> None:
        """Initialize fixed movement player.

        Args:
            value: Movement value returned by ``play``.

        Returns:
            None.
        """
        super().__init__(name="DummyPlayer")
        self._value = value

    def play(self, position: IPosition) -> IMovement:
        """Return deterministic movement.

        Args:
            position: Current position.

        Returns:
            Movement with fixed value.
        """
        del position
        return DummyMovement(value=self._value)


class DummyPlayablePlayer(IPlayer):
    """Playable-only player that selects movement from UI context."""

    def play(self, position: IPosition) -> IMovement:
        """Reject non-UI execution.

        Args:
            position: Current position.

        Returns:
            Never returns.
        """
        del position
        raise RuntimeError("DummyPlayablePlayer requires play_from_ui()")

    def play_from_ui(self, position: IPosition, ui_context: Any | None = None) -> IMovement:
        """Pick first movement from UI-provided movement list.

        Args:
            position: Current position.
            ui_context: Mapping with ``possible_movements``.

        Returns:
            Selected movement.
        """
        del position
        if not isinstance(ui_context, Mapping):
            raise ValueError("ui_context must be mapping")
        movements = tuple(cast(IMovement, movement) for movement in ui_context["possible_movements"])
        return movements[0]


class FakeContainer:
    """Small Streamlit-like container test double."""

    def __init__(self) -> None:
        """Initialize default fake widget state.

        Args:
            None.

        Returns:
            None.
        """
        self.button_values: dict[str, list[bool]] = {}
        self.selectbox_value: str | None = None
        self.file_upload_value: object | None = None
        self.slider_value: int | None = None
        self.radio_value: str | None = None
        self.messages: list[str] = []
        self.progress_values: list[float] = []
        self.code_values: list[str] = []

    def markdown(self, value: str) -> None:
        """Store markdown text.

        Args:
            value: Markdown text.

        Returns:
            None.
        """
        self.messages.append(value)

    def write(self, value: object) -> None:
        """Store generic rendered value.

        Args:
            value: Rendered value.

        Returns:
            None.
        """
        self.messages.append(str(value))

    def subheader(self, value: str) -> None:
        """Store subheader text.

        Args:
            value: Subheader value.

        Returns:
            None.
        """
        self.messages.append(value)

    def code(self, value: str) -> None:
        """Store code panel text.

        Args:
            value: Code string.

        Returns:
            None.
        """
        self.code_values.append(value)

    def button(self, label: str, **kwargs: Any) -> bool:
        """Return programmed button state.

        Args:
            label: Button label.
            **kwargs: Unused keyword arguments.

        Returns:
            Programmed boolean state.
        """
        del kwargs
        values = self.button_values.get(label, [])
        if not values:
            return False
        return values.pop(0)

    def selectbox(
        self,
        label: str,
        options: tuple[str, ...] | tuple[Any, ...],
        **kwargs: Any,
    ) -> object:
        """Return selected option.

        Args:
            label: Selectbox label.
            options: Available options.

        Returns:
            Selected option.
        """
        del label, kwargs
        if self.selectbox_value is None:
            return options[0]
        return self.selectbox_value

    def number_input(
        self,
        label: str,
        min_value: int,
        max_value: int,
        value: int,
        step: int,
    ) -> int:
        """Return provided default value.

        Args:
            label: Number input label.
            min_value: Minimum value.
            max_value: Maximum value.
            value: Default value.
            step: Increment step.

        Returns:
            Default value.
        """
        del label, min_value, max_value, step
        return value

    def file_uploader(self, label: str, type: list[str]) -> object | None:
        """Return configured uploaded file object.

        Args:
            label: Uploader label.
            type: Allowed extensions.

        Returns:
            Uploaded object or ``None``.
        """
        del label, type
        return self.file_upload_value

    def slider(self, label: str, min_value: int, max_value: int, value: int) -> int:
        """Return configured slider value.

        Args:
            label: Slider label.
            min_value: Minimum value.
            max_value: Maximum value.
            value: Default value.

        Returns:
            Selected integer value.
        """
        del label, min_value, max_value
        if self.slider_value is None:
            return value
        return self.slider_value

    def progress(self, value: float) -> None:
        """Store progress values.

        Args:
            value: Progress ratio.

        Returns:
            None.
        """
        self.progress_values.append(value)

    def expander(self, label: str, expanded: bool = False) -> FakeContainer:
        """Return nested container for collapsible content.

        Args:
            label: Expander label.
            expanded: Initial expanded state.

        Returns:
            Same fake container.
        """
        del label, expanded
        return self

    def tabs(self, labels: list[str]) -> tuple[FakeContainer, ...]:
        """Return a tuple with one tab container per label.

        Args:
            labels: Tab labels.

        Returns:
            Tuple containing this same container for each label.
        """
        return tuple(self for _ in labels)

    def columns(self, n_columns: int) -> tuple[FakeContainer, ...]:
        """Return nested fake containers for column layouts.

        Args:
            n_columns: Number of columns.

        Returns:
            Tuple containing this same container for each column.
        """
        return tuple(self for _ in range(n_columns))

    def radio(
        self,
        label: str,
        options: tuple[str, ...],
        format_func: Any,
    ) -> str:
        """Return configured sidebar radio selection.

        Args:
            label: Radio label.
            options: Available options.
            format_func: Option formatter.

        Returns:
            Selected option key.
        """
        del label, format_func
        if self.radio_value is None:
            return options[0]
        return self.radio_value


class FakeStreamlit:
    """Streamlit module-like object used in render tests."""

    def __init__(self) -> None:
        """Initialize fake streamlit module state.

        Args:
            None.

        Returns:
            None.
        """
        self.session_state: dict[str, object] = {}
        self.configuration_column = FakeContainer()
        self.position_column = FakeContainer()
        self.movement_column = FakeContainer()
        self.left_column = self.configuration_column
        self.center_column = self.position_column
        self.sidebar = FakeContainer()
        self.subheaders: list[str] = []
        self.rerun_calls = 0

    def subheader(self, value: str) -> None:
        """Store rendered subheader.

        Args:
            value: Subheader value.

        Returns:
            None.
        """
        self.subheaders.append(value)

    def columns(self, spec: list[int]) -> tuple[FakeContainer, ...]:
        """Return fake columns matching requested count.

        Args:
            spec: Column width specification.

        Returns:
            Tuple with fake containers.
        """
        if len(spec) == 3:
            return (self.configuration_column, self.position_column, self.movement_column)
        if len(spec) == 2:
            return (self.left_column, self.center_column)
        return tuple(self.left_column for _ in spec)

    def rerun(self) -> None:
        """Record one rerun request.

        Args:
            None.

        Returns:
            None.
        """
        self.rerun_calls += 1


def _build_test_page(max_turns: int = 2, include_playable: bool = False) -> OptimizationGamePage:
    """Build a generic test page used by Streamlit tests.

    Args:
        max_turns: Turn cap for generated dummy rules.
        include_playable: Whether to include playable player option.

    Returns:
        Configured optimization page.
    """

    def render_configuration(container: object) -> Mapping[str, object]:
        """Return empty test configuration.

        Args:
            container: Unused container.

        Returns:
            Empty mapping.
        """
        del container
        return {}

    def build_rules(values: Mapping[str, object]) -> IGameRules:
        """Build deterministic test rules.

        Args:
            values: Unused values mapping.

        Returns:
            Dummy rules.
        """
        del values
        return DummyRules(max_turns=max_turns)

    def render_position(container: FakeContainer, view_state: OptimizationViewState) -> None:
        """Render simple position summary.

        Args:
            container: Target container.
            view_state: Current view state.

        Returns:
            None.
        """
        container.write(f"turn={view_state.frame.turn_index}")

    def render_secret(container: FakeContainer, view_state: OptimizationViewState) -> None:
        """Render secret summary text.

        Args:
            container: Target container.
            view_state: Current view state.

        Returns:
            None.
        """
        container.code(f"secret-turn={view_state.frame.turn_index}")

    extra_factories: dict[str, Any] = {}
    if include_playable:
        extra_factories["Playable"] = DummyPlayablePlayer

    return OptimizationGamePage(
        key="dummy",
        title="Dummy",
        render_configuration=render_configuration,
        build_rules=build_rules,
        render_position=render_position,
        default_player_factory=lambda: DummyPlayer(value=1.0),
        extra_player_factories=extra_factories,
        render_secret_information=render_secret,
    )


def test_streamlit_game_index_validation_and_lookup() -> None:
    """Game index should validate uniqueness and resolve pages by key.

    Args:
        None.

    Returns:
        None.
    """
    page = _build_test_page()
    game_index = StreamlitGameIndex([page])

    assert game_index.keys() == ("dummy",)
    assert game_index.page_for("dummy") is page
    with pytest.raises(KeyError):
        game_index.page_for("missing")
    with pytest.raises(ValueError):
        StreamlitGameIndex([])
    with pytest.raises(ValueError):
        StreamlitGameIndex([page, page])


def test_render_single_page_without_started_game_shows_placeholder() -> None:
    """Page renderer should show placeholder when no replay exists yet.

    Args:
        None.

    Returns:
        None.
    """
    streamlit_api = FakeStreamlit()
    render_single_player_optimization_page(streamlit_api=streamlit_api, page=_build_test_page())

    assert "Dummy" in streamlit_api.subheaders
    assert any("Configure the game" in message for message in streamlit_api.center_column.messages)


def test_render_single_page_start_runs_game_and_renders_view() -> None:
    """Start action should execute game and store replay/controller in session.

    Args:
        None.

    Returns:
        None.
    """
    streamlit_api = FakeStreamlit()
    streamlit_api.configuration_column.button_values = {"Start": [True]}

    render_single_player_optimization_page(streamlit_api=streamlit_api, page=_build_test_page())
    render_single_player_optimization_page(streamlit_api=streamlit_api, page=_build_test_page())

    replay_key = "iarena.apping.dummy.replay"
    controller_key = "iarena.apping.dummy.controller"
    assert replay_key in streamlit_api.session_state
    assert controller_key in streamlit_api.session_state
    assert any("turn=" in message for message in streamlit_api.position_column.messages)
    assert any("Current score" in message for message in streamlit_api.movement_column.messages)


def test_render_single_page_uses_uploaded_player_when_available() -> None:
    """Uploaded source should override selected built-in player factory.

    Args:
        None.

    Returns:
        None.
    """
    streamlit_api = FakeStreamlit()
    streamlit_api.configuration_column.button_values = {"Start": [True]}
    streamlit_api.configuration_column.file_upload_value = (
        "class UploadedPlayer(IPlayer):\n"
        "    def play(self, position):\n"
        "        del position\n"
        "        class UploadedMovement:\n"
        "            value = 2.0\n"
        "        return UploadedMovement()\n"
    )

    render_single_player_optimization_page(streamlit_api=streamlit_api, page=_build_test_page())

    replay = streamlit_api.session_state["iarena.apping.dummy.replay"]
    assert hasattr(replay, "final_score")
    assert replay.final_score.get_score(0) == 4.0


def test_render_single_page_autoplay_advances_and_requests_rerun(monkeypatch: pytest.MonkeyPatch) -> None:
    """Autoplay mode should advance one frame and request a rerun.

    Args:
        monkeypatch: Pytest monkeypatch helper.

    Returns:
        None.
    """
    streamlit_api = FakeStreamlit()
    rules = DummyRules(max_turns=2)
    replay = run_single_player_optimization_game(rules=rules, player=DummyPlayer(value=1.0))
    controller = PlaybackController(total_frames=len(replay.frames))
    controller.play()
    streamlit_api.session_state["iarena.apping.dummy.replay"] = replay
    streamlit_api.session_state["iarena.apping.dummy.controller"] = controller
    streamlit_api.session_state["iarena.apping.dummy.state"] = "REVIEWING"

    monkeypatch.setattr("iarena.apping.StreamlitPlayModes.time.sleep", lambda _: None)
    render_single_player_optimization_page(streamlit_api=streamlit_api, page=_build_test_page())

    assert controller.current_index() == 1
    assert streamlit_api.rerun_calls == 1


def test_render_single_page_supports_interactive_playable_flow() -> None:
    """Playable players should execute turn-by-turn and then switch to replay mode.

    Args:
        None.

    Returns:
        None.
    """
    streamlit_api = FakeStreamlit()
    streamlit_api.configuration_column.selectbox_value = "Playable"
    streamlit_api.configuration_column.button_values = {"Start": [True]}

    render_single_player_optimization_page(
        streamlit_api=streamlit_api,
        page=_build_test_page(max_turns=1, include_playable=True),
    )
    render_single_player_optimization_page(
        streamlit_api=streamlit_api,
        page=_build_test_page(max_turns=1, include_playable=True),
    )

    assert "iarena.apping.dummy.replay" in streamlit_api.session_state
    assert "iarena.apping.dummy.controller" in streamlit_api.session_state
    assert "iarena.apping.dummy.interactive" not in streamlit_api.session_state


def test_render_games_index_page_selects_sidebar_game() -> None:
    """Main index renderer should route to the selected game page.

    Args:
        None.

    Returns:
        None.
    """
    streamlit_api = FakeStreamlit()
    page = _build_test_page()
    game_index = StreamlitGameIndex([page])
    streamlit_api.sidebar.radio_value = "dummy"

    render_games_index_page(streamlit_api=streamlit_api, game_index=game_index)

    assert "Dummy" in streamlit_api.subheaders


def test_build_default_game_index_contains_goldmine() -> None:
    """Default index builder should include built-in GoldMine page.

    Args:
        None.

    Returns:
        None.
    """
    default_index = build_default_game_index()

    assert "goldmine" in default_index.keys()
