"""Tests for streamlit application orchestration helpers."""

from __future__ import annotations

from pathlib import Path

from iarena.apps.streamlit.StreamlitApplication import StreamlitApplication
from iarena.gaming.goldmine.GoldMineGame import GoldMineGame
from iarena.gaming.goldmine.GoldMineStreamlitView import GoldMineStreamlitView
from iarena.gaming.hanoi.HanoiConfiguration import HanoiConfiguration
from iarena.gaming.hanoi.HanoiGame import HanoiGame
from iarena.gaming.hanoi.HanoiStreamlitView import HanoiStreamlitView
from iarena.gaming.tictactoe.TicTacToeGame import TicTacToeGame
from iarena.gaming.tictactoe.TicTacToeStreamlitView import TicTacToeStreamlitView
from iarena.playing.LoadPlayer import LoadPlayer
from iarena.playing.PolyvalentRandomPlayer import PolyvalentRandomPlayer
from iarena.playing.PolyvalentTerminalPlayer import PolyvalentTerminalPlayer


def test_available_games_include_streamlit_supported_games() -> None:
    app = StreamlitApplication()

    games = app._available_games()
    game_names = {game.name() for game in games}

    assert "hanoi" in game_names
    assert "goldmine" in game_names
    assert "tictactoe" in game_names


def test_streamlit_renderer_classes_include_hanoi_streamlit_view() -> None:
    app = StreamlitApplication()

    renderers = app._streamlit_renderer_classes(HanoiGame.instance())

    assert HanoiStreamlitView in renderers


def test_streamlit_renderer_classes_include_tictactoe_streamlit_view() -> None:
    app = StreamlitApplication()

    renderers = app._streamlit_renderer_classes(TicTacToeGame.instance())

    assert TicTacToeStreamlitView in renderers


def test_streamlit_renderer_classes_include_goldmine_streamlit_view() -> None:
    app = StreamlitApplication()

    renderers = app._streamlit_renderer_classes(GoldMineGame.instance())

    assert GoldMineStreamlitView in renderers


def test_player_classes_filter_excludes_terminal_human_player() -> None:
    app = StreamlitApplication()

    player_classes = app._player_classes(HanoiGame.instance())

    assert PolyvalentRandomPlayer in player_classes
    assert PolyvalentTerminalPlayer not in player_classes


def test_default_player_index_prefers_polyvalent_random_when_available() -> None:
    app = StreamlitApplication()
    player_classes = app._player_classes(HanoiGame.instance())

    default_index = app._default_player_index(player_classes)

    assert player_classes[default_index] is PolyvalentRandomPlayer


def test_default_configuration_uses_hanoi_default_setup() -> None:
    app = StreamlitApplication()

    configuration = app._default_configuration(HanoiGame.instance(), HanoiConfiguration)

    assert isinstance(configuration, HanoiConfiguration)
    assert configuration.n_pegs == 3
    assert configuration.disks == [0, 0, 0]


def test_load_player_from_file_returns_player_instance(tmp_path: Path) -> None:
    player_file = tmp_path / "streamlit_custom_player.py"
    player_file.write_text(
        """
from iarena.playing.LoadPlayer import LoadPlayer

class _CustomLoadPlayer(LoadPlayer):
    def play(self, pos):
        return list(pos.get_rules().possible_movements(pos))[0]

    def authors(self) -> list[str]:
        return ["Streamlit Test"]

PLAYER = _CustomLoadPlayer()
""".strip(),
        encoding="utf-8",
    )
    app = StreamlitApplication()

    player = app._load_player_from_file(str(player_file))

    assert isinstance(player, LoadPlayer)


def test_instantiate_players_accepts_loaded_player_entries() -> None:
    class _InlineLoadPlayer(LoadPlayer):
        def __init__(self) -> None:
            self.was_started = False

        def play(self, pos):
            return list(pos.get_rules().possible_movements(pos))[0]

        def authors(self) -> list[str]:
            return ["Inline Streamlit Test"]

        def starting_game(self, rules, player_index) -> None:
            self.was_started = True

    app = StreamlitApplication()
    rules = HanoiGame.instance().generate_rules(HanoiConfiguration(n_pegs=3, disks=[0, 0, 0]))
    player = _InlineLoadPlayer()

    players = app._instantiate_players(player_entries=[player], view=HanoiStreamlitView(), rules=rules)

    assert len(players) == 1
    assert players[0] is player
    assert player.was_started is True


def test_load_player_from_uploaded_file_returns_player_instance() -> None:
    class _UploadedFile:
        def __init__(self, payload: bytes) -> None:
            self._payload = payload

        def getvalue(self) -> bytes:
            return self._payload

    uploaded_file = _UploadedFile(
        b"""
from iarena.playing.LoadPlayer import LoadPlayer

class _UploadedLoadPlayer(LoadPlayer):
    def play(self, pos):
        return list(pos.get_rules().possible_movements(pos))[0]

    def authors(self) -> list[str]:
        return ["Uploaded Streamlit Test"]

PLAYER = _UploadedLoadPlayer()
""".strip(),
    )
    app = StreamlitApplication()

    player = app._load_player_from_uploaded_file(uploaded_file)

    assert isinstance(player, LoadPlayer)
