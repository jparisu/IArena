from __future__ import annotations

import json
from pathlib import Path
from typing import get_args, get_origin, get_type_hints

import pytest

from iarena.grading.AutoGrader import AutoGrader
from iarena.grading.Exam import Exam
from iarena.grading.MatchReport import MatchReport


class _Exam:
    def __init__(self) -> None:
        self.grade_calls = 0
        self.score_calls = 0

    def grade(self) -> list[list[MatchReport]]:
        self.grade_calls += 1
        report = MatchReport()
        report.moves = 1
        report.total_time_s = 0.1
        report.score = 1.0
        report.messages = {}
        return [[report]]

    def score(self) -> float:
        self.score_calls += 1
        return 7.5


def test_grade_delegates_to_exam_grader() -> None:
    auto = AutoGrader()
    exam = _Exam()
    auto.grader = exam  # type: ignore[assignment]

    reports = auto.grade()

    assert exam.grade_calls == 1
    assert len(reports) == 1


def test_score_delegates_to_exam_grader() -> None:
    auto = AutoGrader()
    exam = _Exam()
    auto.grader = exam  # type: ignore[assignment]

    value = auto.score()

    assert exam.score_calls == 1
    assert value == 7.5


def test_grade_raises_runtime_error_when_grader_is_missing() -> None:
    auto = AutoGrader()

    with pytest.raises(RuntimeError, match="requires `grader`"):
        _ = auto.grade()


def test_grade_method_declares_expected_return_annotation() -> None:
    annotation = get_type_hints(AutoGrader.grade)["return"]

    assert get_origin(annotation) is list
    nested = get_args(annotation)[0]
    assert get_origin(nested) is list
    assert get_args(nested) == (MatchReport,)


def test_from_files_builds_autograder_with_exam_reader(tmp_path: Path) -> None:
    configuration_file = tmp_path / "exam.yaml"
    player_file = tmp_path / "player.py"

    configuration_file.write_text(
        "\n".join(
            [
                "game: hanoi",
                "trials:",
                "  - args:",
                "      n_pegs: 3",
                "      n_disks: 1",
            ],
        ),
        encoding="utf-8",
    )
    player_file.write_text(
        "\n".join(
            [
                "from __future__ import annotations",
                "",
                "from iarena.playing.LoadPlayer import LoadPlayer",
                "from iarena.gaming.Movement import Movement",
                "from iarena.gaming.Position import Position",
                "",
                "class TmpPlayer(LoadPlayer):",
                "    def play(self, pos: Position) -> Movement:",
                "        return next(pos.get_rules().possible_movements(pos))",
                "",
                "    def authors(self) -> list[str]:",
                "        return ['Tester']",
                "",
                "PLAYER = TmpPlayer()",
            ],
        ),
        encoding="utf-8",
    )

    autograder = AutoGrader.from_files(str(configuration_file), str(player_file))

    assert autograder.configuration_file == str(configuration_file)
    assert autograder.player_file == str(player_file)
    assert isinstance(autograder.grader, Exam)


def test_from_files_accepts_notebook_players_with_token(tmp_path: Path) -> None:
    configuration_file = tmp_path / "exam.yaml"
    player_file = tmp_path / "player.ipynb"

    configuration_file.write_text(
        "\n".join(
            [
                "game: hanoi",
                "trials:",
                "  - args:",
                "      n_pegs: 3",
                "      n_disks: 1",
            ],
        ),
        encoding="utf-8",
    )
    player_file.write_text(
        json.dumps(
            {
                "cells": [
                    {"cell_type": "code", "source": ["x = 1\n"]},
                    {
                        "cell_type": "code",
                        "source": [
                            "from __future__ import annotations\n",
                            "from iarena.playing.LoadPlayer import LoadPlayer\n",
                            "from iarena.gaming.Movement import Movement\n",
                            "from iarena.gaming.Position import Position\n",
                            "\n",
                            "class TmpPlayer(LoadPlayer):\n",
                            "    def play(self, pos: Position) -> Movement:\n",
                            "        return next(pos.get_rules().possible_movements(pos))\n",
                            "\n",
                            "    def authors(self) -> list[str]:\n",
                            "        return ['Notebook Tester']\n",
                            "\n",
                            "# CUSTOM_PLAYER_TOKEN\n",
                            "PLAYER = TmpPlayer()\n",
                        ],
                    },
                ],
            },
        ),
        encoding="utf-8",
    )

    autograder = AutoGrader.from_files(str(configuration_file), str(player_file), token="CUSTOM_PLAYER_TOKEN")

    assert autograder.configuration_file == str(configuration_file)
    assert autograder.player_file == str(player_file)
    assert autograder.token == "CUSTOM_PLAYER_TOKEN"
    assert isinstance(autograder.grader, Exam)
