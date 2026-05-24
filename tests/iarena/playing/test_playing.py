"""Tests for the playing package skeleton contracts."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from iarena.gaming.Movement import Movement
from iarena.playing.LoadPlayer import LoadPlayer
from iarena.playing.Player import Player
from iarena.playing.PlayerIndex import PlayerIndex
from iarena.playing.PolyvalentRandomPlayer import PolyvalentRandomPlayer
from iarena.playing.PolyvalentStreamlitPlayer import PolyvalentStreamlitPlayer
from iarena.playing.PolyvalentTerminalPlayer import PolyvalentTerminalPlayer
from iarena.utilizing.randoming.RandomGenerator import RandomGenerator
from iarena.visualizing.streamlit_frontend.StreamlitSession import StreamlitSession


class _DummyMovement(Movement):
    def __init__(self, label: str) -> None:
        self.label = label

    def __repr__(self) -> str:
        return self.label

    def __eq__(self, other: object) -> bool:
        return isinstance(other, _DummyMovement) and self.label == other.label


class _DummyRules:
    def __init__(self, movements: list[_DummyMovement]) -> None:
        self._movements = movements

    def possible_movements(self, pos: object) -> list[_DummyMovement]:
        _ = pos
        return list(self._movements)


class _DummyPosition:
    def __init__(self, rules: _DummyRules) -> None:
        self._rules = rules

    def get_rules(self) -> _DummyRules:
        return self._rules


class _DummyRender:
    def __init__(self, inputs: list[str]) -> None:
        self._inputs = inputs
        self.output: list[str] = []

    def output_fnc(self, text: str) -> None:
        self.output.append(text)

    def input_fnc(self, prompt: str = "") -> str:
        self.output.append(prompt)
        return self._inputs.pop(0)


class _DummyStreamlitRender:
    def capture_input(self, state: StreamlitSession) -> Movement:
        return _DummyMovement(str(state.get("streamlit_choice", "none")))


def test_player_cannot_be_instantiated_without_implementing_abstract_methods() -> None:
    class _IncompletePlayer(Player):
        pass

    with pytest.raises(TypeError):
        _IncompletePlayer()


def test_load_player_default_name_is_stable() -> None:
    class _MinimalLoadPlayer(LoadPlayer):
        def play(self, pos: _DummyPosition) -> _DummyMovement:
            _ = pos
            return _DummyMovement("choice")

        def authors(self) -> list[str]:
            return ["Tester"]

    assert _MinimalLoadPlayer().name() == "load-player"


def test_load_player_default_starting_game_does_nothing() -> None:
    class _MinimalLoadPlayer(LoadPlayer):
        def play(self, pos: _DummyPosition) -> _DummyMovement:
            _ = pos
            return _DummyMovement("choice")

        def authors(self) -> list[str]:
            return ["Tester"]

    player = _MinimalLoadPlayer()
    player.starting_game(rules=object(), player_index=PlayerIndex(0))


def test_load_player_from_file_loads_player_instance(tmp_path: Path) -> None:
    player_file = tmp_path / "custom_player.py"
    player_file.write_text(
        """
from iarena.playing.LoadPlayer import LoadPlayer

class _CustomPlayer(LoadPlayer):
    def play(self, pos):
        return "movement"

    def authors(self) -> list[str]:
        return ["Author A"]

PLAYER = _CustomPlayer()
""".strip(),
        encoding="utf-8",
    )

    loaded_player = LoadPlayer.from_file(str(player_file))

    assert isinstance(loaded_player, LoadPlayer)
    assert loaded_player.authors() == ["Author A"]
    assert loaded_player.name() == "load-player"


def test_load_player_from_file_requires_player_variable(tmp_path: Path) -> None:
    player_file = tmp_path / "missing_player.py"
    player_file.write_text(
        """
from iarena.playing.LoadPlayer import LoadPlayer

class _CustomPlayer(LoadPlayer):
    def play(self, pos):
        return "movement"

    def authors(self) -> list[str]:
        return ["Author A"]
""".strip(),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Missing required variable 'PLAYER'"):
        LoadPlayer.from_file(str(player_file))


def test_load_player_from_file_rejects_invalid_player_type(tmp_path: Path) -> None:
    player_file = tmp_path / "invalid_player.py"
    player_file.write_text("PLAYER = object()", encoding="utf-8")

    with pytest.raises(TypeError, match="PLAYER must be an instance of Player"):
        LoadPlayer.from_file(str(player_file))


def test_load_player_from_file_rejects_missing_file(tmp_path: Path) -> None:
    missing_file = tmp_path / "absent_player.py"

    with pytest.raises(FileNotFoundError, match="File not found|No such file"):
        LoadPlayer.from_file(str(missing_file))


def test_load_player_from_notebook_file_loads_player_from_token_cell(tmp_path: Path) -> None:
    notebook_file = tmp_path / "custom_player.ipynb"
    notebook_file.write_text(
        json.dumps(
            {
                "cells": [
                    {"cell_type": "code", "source": ["x = 1\n"]},
                    {
                        "cell_type": "code",
                        "source": [
                            "from iarena.playing.LoadPlayer import LoadPlayer\n",
                            "\n",
                            "class _CustomPlayer(LoadPlayer):\n",
                            "    def play(self, pos):\n",
                            "        return 'movement'\n",
                            "\n",
                            "    def authors(self) -> list[str]:\n",
                            "        return ['Notebook Author']\n",
                            "\n",
                            "PLAYER = _CustomPlayer()\n",
                        ],
                    },
                ],
            },
        ),
        encoding="utf-8",
    )

    loaded_player = LoadPlayer.from_file(str(notebook_file))

    assert isinstance(loaded_player, LoadPlayer)
    assert loaded_player.authors() == ["Notebook Author"]


def test_load_player_from_notebook_file_requires_matching_token(tmp_path: Path) -> None:
    notebook_file = tmp_path / "missing_token.ipynb"
    notebook_file.write_text(
        json.dumps(
            {
                "cells": [
                    {
                        "cell_type": "code",
                        "source": ["PLAYER = object()\n"],
                    },
                ],
            },
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="No notebook code cell contains token"):
        LoadPlayer.from_file(str(notebook_file), token="CUSTOM_TOKEN")


def test_load_player_from_file_accepts_player_subclass_not_inheriting_load_player(tmp_path: Path) -> None:
    player_file = tmp_path / "custom_base_player.py"
    player_file.write_text(
        """
from iarena.playing.Player import Player

class _CustomPlayer(Player):
    def play(self, pos):
        return "movement"

    def starting_game(self, rules, player_index) -> None:
        _ = (rules, player_index)

PLAYER = _CustomPlayer(name="plain-player")
""".strip(),
        encoding="utf-8",
    )

    loaded_player = LoadPlayer.from_file(str(player_file))

    assert isinstance(loaded_player, Player)
    assert loaded_player.name() == "plain-player"


def test_polyvalent_terminal_player_name_is_stable() -> None:
    assert PolyvalentTerminalPlayer().name() == "polyvalent-terminal"


def test_polyvalent_terminal_player_plays_selected_movement_by_index() -> None:
    movements = [_DummyMovement("left"), _DummyMovement("right")]
    rules = _DummyRules(movements)
    position = _DummyPosition(rules)
    player = PolyvalentTerminalPlayer()
    player.render = _DummyRender(inputs=["1"])

    chosen = player.play(position)

    assert chosen == _DummyMovement("right")
    assert player.render.output[:2] == ["Select one movement by index:", "0: left"]


def test_polyvalent_terminal_player_reprompts_on_invalid_index() -> None:
    rules = _DummyRules([_DummyMovement("only")])
    position = _DummyPosition(rules)
    player = PolyvalentTerminalPlayer()
    player.render = _DummyRender(inputs=["3", "0"])

    chosen = player.play(position)

    assert chosen == _DummyMovement("only")
    assert any("out of bounds" in message for message in player.render.output)


def test_polyvalent_terminal_player_starting_game_stores_context() -> None:
    player = PolyvalentTerminalPlayer()
    rules = object()
    player_index = PlayerIndex(0)

    player.starting_game(rules=rules, player_index=player_index)

    assert player._rules is rules
    assert player._player_index == player_index


def test_polyvalent_random_player_name_is_stable() -> None:
    assert PolyvalentRandomPlayer().name() == "polyvalent-random"


def test_polyvalent_random_player_returns_one_legal_movement() -> None:
    movements = [_DummyMovement("m0"), _DummyMovement("m1"), _DummyMovement("m2")]
    rules = _DummyRules(movements)
    position = _DummyPosition(rules)
    player = PolyvalentRandomPlayer()
    player.rng = RandomGenerator(seed=7)

    chosen = player.play(position)

    assert chosen in movements


def test_polyvalent_random_player_rejects_empty_legal_movements() -> None:
    rules = _DummyRules([])
    position = _DummyPosition(rules)
    player = PolyvalentRandomPlayer()
    player.rng = RandomGenerator(seed=0)

    with pytest.raises(ValueError, match="No legal movements available"):
        player.play(position)


def test_polyvalent_random_player_starting_game_initializes_context_and_rng() -> None:
    player = PolyvalentRandomPlayer()
    rules = object()
    player_index = PlayerIndex(1)

    player.starting_game(rules=rules, player_index=player_index)

    assert player._rules is rules
    assert player._player_index == player_index
    assert isinstance(player.rng, RandomGenerator)


def test_polyvalent_streamlit_player_name_is_stable() -> None:
    assert PolyvalentStreamlitPlayer().name() == "polyvalent-streamlit"


def test_polyvalent_streamlit_player_prefers_selected_movement_from_session_state() -> None:
    player = PolyvalentStreamlitPlayer()
    player.render = _DummyStreamlitRender()
    selected_movement = _DummyMovement("picked")
    player.set_session_state(StreamlitSession({"selected_movement": selected_movement}))

    chosen = player.play(_DummyPosition(_DummyRules([])))

    assert chosen == selected_movement


def test_polyvalent_streamlit_player_delegates_to_view_capture_input_without_selected_movement() -> None:
    player = PolyvalentStreamlitPlayer()
    player.render = _DummyStreamlitRender()
    player.set_session_state(StreamlitSession({"streamlit_choice": "captured"}))

    chosen = player.play(_DummyPosition(_DummyRules([])))

    assert chosen == _DummyMovement("captured")


def test_polyvalent_streamlit_player_starting_game_stores_context_and_initializes_session() -> None:
    player = PolyvalentStreamlitPlayer()
    rules = object()
    player_index = PlayerIndex(2)

    player.starting_game(rules=rules, player_index=player_index)

    assert player._rules is rules
    assert player._player_index == player_index
    assert isinstance(player._session_state, StreamlitSession)
