"""Tests for TicTacToeASCIIView."""

import pytest

from iarena.game.GameMove import GameMove
from iarena.games.tictactoe.TicTacToeASCIIView import TicTacToeASCIIView
from iarena.games.tictactoe.TicTacToeMove import TicTacToeMove
from iarena.games.tictactoe.TicTacToeState import EMPTY, PLAYER_O, PLAYER_X, TicTacToeState
from iarena.interface.Interface import Interface
from iarena.view.View import View


class _RecordingInterface(Interface):
    """Test interface that records rendered output and serves scripted input."""

    def __init__(self, scripted_input: str = "") -> None:
        super().__init__(view=None)
        self.rendered: list[str] = []
        self._input = scripted_input

    def render(self, content: str) -> None:
        self.rendered.append(content)

    def ask(self, prompt: str) -> str:
        return self._input


@pytest.fixture()
def view() -> TicTacToeASCIIView:
    return TicTacToeASCIIView()


@pytest.fixture()
def empty_state() -> TicTacToeState:
    return TicTacToeState()


class TestTicTacToeASCIIViewClass:
    def test_is_view_subclass(self) -> None:
        assert issubclass(TicTacToeASCIIView, View)

    def test_instantiation(self) -> None:
        assert isinstance(TicTacToeASCIIView(), TicTacToeASCIIView)


class TestTicTacToeASCIIViewRenderState:
    # --- Happy path ---

    def test_render_state_calls_interface_render(
        self, view: TicTacToeASCIIView, empty_state: TicTacToeState
    ) -> None:
        iface = _RecordingInterface()
        view.render_state(empty_state, iface)
        assert len(iface.rendered) > 0

    def test_render_state_output_contains_board_chars(
        self, view: TicTacToeASCIIView, empty_state: TicTacToeState
    ) -> None:
        iface = _RecordingInterface()
        view.render_state(empty_state, iface)
        full_output = "\n".join(iface.rendered)
        # Board must show some content
        assert len(full_output) > 0

    def test_render_state_shows_x_mark(self, view: TicTacToeASCIIView) -> None:
        board = [[PLAYER_X, EMPTY, EMPTY], [EMPTY, EMPTY, EMPTY], [EMPTY, EMPTY, EMPTY]]
        state = TicTacToeState(board=board)
        iface = _RecordingInterface()
        view.render_state(state, iface)
        full_output = "\n".join(iface.rendered)
        assert "X" in full_output

    def test_render_state_shows_o_mark(self, view: TicTacToeASCIIView) -> None:
        board = [[EMPTY, PLAYER_O, EMPTY], [EMPTY, EMPTY, EMPTY], [EMPTY, EMPTY, EMPTY]]
        state = TicTacToeState(board=board)
        iface = _RecordingInterface()
        view.render_state(state, iface)
        full_output = "\n".join(iface.rendered)
        assert "O" in full_output

    # --- Corner cases ---

    def test_render_full_board_no_error(self, view: TicTacToeASCIIView) -> None:
        board = [
            [PLAYER_X, PLAYER_O, PLAYER_X],
            [PLAYER_O, PLAYER_X, PLAYER_O],
            [PLAYER_O, PLAYER_X, PLAYER_O],
        ]
        state = TicTacToeState(board=board)
        iface = _RecordingInterface()
        view.render_state(state, iface)  # must not raise


class TestTicTacToeASCIIViewAsk:
    # --- Happy path ---

    def test_ask_returns_tictactoe_move(self, view: TicTacToeASCIIView) -> None:
        iface = _RecordingInterface(scripted_input="1,2")
        move = view.ask(iface)
        assert isinstance(move, TicTacToeMove)

    def test_ask_returns_correct_cell(self, view: TicTacToeASCIIView) -> None:
        iface = _RecordingInterface(scripted_input="0,0")
        move = view.ask(iface)
        assert move.row == 0
        assert move.col == 0

    def test_ask_returns_game_move(self, view: TicTacToeASCIIView) -> None:
        iface = _RecordingInterface(scripted_input="2,1")
        move = view.ask(iface)
        assert isinstance(move, GameMove)

    # --- Corner cases ---

    def test_ask_all_valid_cells(self, view: TicTacToeASCIIView) -> None:
        for row in range(3):
            for col in range(3):
                iface = _RecordingInterface(scripted_input=f"{row},{col}")
                move = view.ask(iface)
                assert move.row == row
                assert move.col == col

    # --- Failure cases ---

    def test_ask_invalid_input_raises(self, view: TicTacToeASCIIView) -> None:
        iface = _RecordingInterface(scripted_input="bad input")
        with pytest.raises(ValueError):
            view.ask(iface)

    def test_ask_out_of_bounds_raises(self, view: TicTacToeASCIIView) -> None:
        iface = _RecordingInterface(scripted_input="3,3")
        with pytest.raises(ValueError):
            view.ask(iface)
