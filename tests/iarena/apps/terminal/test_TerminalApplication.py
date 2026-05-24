"""Tests for the terminal application orchestration flow."""

from __future__ import annotations

import json
from pathlib import Path

from iarena.apps.terminal.TerminalApplication import TerminalApplication
from iarena.gaming.hanoi.HanoiConfiguration import HanoiConfiguration
from iarena.gaming.hanoi.HanoiGame import HanoiGame
from iarena.playing.PolyvalentRandomPlayer import PolyvalentRandomPlayer


class _TerminalIO:
    """Simple test double for terminal input/output callables."""

    def __init__(self, inputs: list[str]) -> None:
        self._inputs = list(inputs)
        self.outputs: list[str] = []

    def input(self, prompt: str = "") -> str:
        self.outputs.append(prompt)
        if not self._inputs:
            raise RuntimeError("No input left in test IO stub.")
        return self._inputs.pop(0)

    def output(self, message: str) -> None:
        self.outputs.append(message)


def test_ask_for_game_returns_goldmine_terminal_game() -> None:
    io = _TerminalIO(inputs=["0"])
    app = TerminalApplication(input_fnc=io.input, output_fnc=io.output)

    game = app.ask_for_game()

    assert game.name() == "goldmine"


def test_ask_for_configuration_default_uses_game_default_configuration() -> None:
    io = _TerminalIO(inputs=["2"])
    app = TerminalApplication(input_fnc=io.input, output_fnc=io.output)
    app._game = HanoiGame.instance()

    configuration = app.ask_for_configuration()

    assert isinstance(configuration, HanoiConfiguration)
    assert configuration.n_pegs == 3
    assert configuration.disks == [0, 0, 0]


def test_ask_for_configuration_from_yaml_file(tmp_path: Path) -> None:
    config_path = tmp_path / "hanoi.yaml"
    config_path.write_text("n_pegs: 4\ndisks: [0, 0]\n", encoding="utf-8")

    io = _TerminalIO(inputs=["0", str(config_path)])
    app = TerminalApplication(input_fnc=io.input, output_fnc=io.output)
    app._game = HanoiGame.instance()

    configuration = app.ask_for_configuration()

    assert isinstance(configuration, HanoiConfiguration)
    assert configuration.n_pegs == 4
    assert configuration.disks == [0, 0]


def test_ask_for_configuration_guided_prompt_uses_hanoi_hook() -> None:
    io = _TerminalIO(inputs=["1", "4", "2"])
    app = TerminalApplication(input_fnc=io.input, output_fnc=io.output)
    app._game = HanoiGame.instance()

    configuration = app.ask_for_configuration()

    assert isinstance(configuration, HanoiConfiguration)
    assert configuration.n_pegs == 4
    assert configuration.disks == [0, 0]


def test_run_supports_hanoi_default_configuration_with_random_player() -> None:
    io = _TerminalIO(inputs=["0", "2", "1"])
    app = TerminalApplication(input_fnc=io.input, output_fnc=io.output, max_turns=200)

    app.run()

    assert app.arena is not None
    assert app.view is not None
    assert any("Final Scoreboard" in output for output in io.outputs)
    assert any("polyvalent-random" in output for output in io.outputs)
    assert any("STATE START" in output for output in io.outputs)


def test_ask_for_player_loads_player_from_python_file(tmp_path: Path) -> None:
    player_file = tmp_path / "custom_player.py"
    player_file.write_text(
        """
from iarena.playing.LoadPlayer import LoadPlayer

class _CustomLoadPlayer(LoadPlayer):
    def play(self, pos):
        return list(pos.get_rules().possible_movements(pos))[0]

    def authors(self) -> list[str]:
        return ["Terminal Test"]

    def name(self) -> str:
        return "terminal-loaded-player"

PLAYER = _CustomLoadPlayer()
""".strip(),
        encoding="utf-8",
    )
    io = _TerminalIO(inputs=["1", str(player_file)])
    app = TerminalApplication(input_fnc=io.input, output_fnc=io.output)
    app.view = object()

    player = app.ask_for_player(slot_index=0, player_classes=[PolyvalentRandomPlayer])

    assert player.name() == "terminal-loaded-player"


def test_ask_for_player_loads_player_from_notebook_file(tmp_path: Path) -> None:
    player_file = tmp_path / "custom_player.ipynb"
    player_file.write_text(
        json.dumps(
            {
                "cells": [
                    {
                        "cell_type": "code",
                        "source": [
                            "from iarena.playing.LoadPlayer import LoadPlayer\n",
                            "\n",
                            "class _CustomLoadPlayer(LoadPlayer):\n",
                            "    def play(self, pos):\n",
                            "        return list(pos.get_rules().possible_movements(pos))[0]\n",
                            "\n",
                            "    def authors(self) -> list[str]:\n",
                            "        return ['Terminal Notebook Test']\n",
                            "\n",
                            "    def name(self) -> str:\n",
                            "        return 'terminal-notebook-loaded-player'\n",
                            "\n",
                            "PLAYER = _CustomLoadPlayer()\n",
                        ],
                    },
                ],
            },
        ),
        encoding="utf-8",
    )
    io = _TerminalIO(inputs=["1", str(player_file)])
    app = TerminalApplication(input_fnc=io.input, output_fnc=io.output)
    app.view = object()

    player = app.ask_for_player(slot_index=0, player_classes=[PolyvalentRandomPlayer])

    assert player.name() == "terminal-notebook-loaded-player"
