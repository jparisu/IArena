from __future__ import annotations

import csv
import json
from pathlib import Path
from zipfile import ZipFile

from iarena.grading.MultiGrader import MultiGrader


def _write_player_file(path: Path, author_name: str, *, valid: bool) -> None:
    if valid:
        path.write_text(
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
                    f"        return ['{author_name}']",
                    "",
                    "PLAYER = TmpPlayer()",
                ],
            ),
            encoding="utf-8",
        )
        return

    path.write_text("BROKEN = True\n", encoding="utf-8")


def _write_configuration(path: Path) -> None:
    path.write_text(
        "\n".join(
            [
                "game: hanoi",
                "move_timeout_s: 0.2",
                "total_timeout_s: 1.0",
                "repetitions: 1",
                "fails_allowed: 0",
                "max_moves: 10",
                "reports:",
                "  - name: base",
                "    args:",
                "      n_pegs: 3",
                "      n_disks: 1",
                "    multi_args:",
                "      n_disks: [1, 2]",
            ],
        ),
        encoding="utf-8",
    )


def _write_configuration_with_trials(path: Path) -> None:
    path.write_text(
        "\n".join(
            [
                "game: hanoi",
                "move_timeout_s: 0.2",
                "total_timeout_s: 1.0",
                "repetitions: 1",
                "fails_allowed: 0",
                "max_moves: 10",
                "trials:",
                "  - name: base",
                "    args:",
                "      n_pegs: 3",
                "      n_disks: 1",
            ],
        ),
        encoding="utf-8",
    )


def _build_zip(path: Path, submissions_dir: Path) -> None:
    with ZipFile(path, "w") as archive:
        for file_path in submissions_dir.rglob("*"):
            if not file_path.is_file():
                continue
            if file_path.suffix not in {".py", ".ipynb"}:
                continue
            archive.write(file_path, arcname=file_path.relative_to(submissions_dir))


def _write_notebook_player_file(path: Path, author_name: str, token: str) -> None:
    path.write_text(
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
                            f"        return ['{author_name}']\n",
                            "\n",
                            f"# {token}\n",
                            "PLAYER = TmpPlayer()\n",
                        ],
                    },
                ],
            },
        ),
        encoding="utf-8",
    )


def test_from_zip_loads_players_and_expands_trials(tmp_path: Path) -> None:
    config_file = tmp_path / "grader.yaml"
    zip_file = tmp_path / "players.zip"
    submissions_dir = tmp_path / "submissions"
    submissions_dir.mkdir()

    _write_configuration(config_file)
    _write_player_file(submissions_dir / "student_a.py", "Alice", valid=True)
    _write_player_file(submissions_dir / "student_b.py", "Bob", valid=False)
    _build_zip(zip_file, submissions_dir)

    grader = MultiGrader.from_zip(str(config_file), str(zip_file), repetitions=2)

    assert len(grader.players) == 2
    assert len(grader.trial_definitions) == 2
    assert all(repetitions == 2 for _, repetitions in grader.trial_definitions)


def test_grade_all_records_success_and_load_errors(tmp_path: Path) -> None:
    config_file = tmp_path / "grader.yaml"
    zip_file = tmp_path / "players.zip"
    submissions_dir = tmp_path / "submissions"
    submissions_dir.mkdir()

    _write_configuration(config_file)
    _write_player_file(submissions_dir / "student_ok.py", "Alice", valid=True)
    _write_player_file(submissions_dir / "student_bad.py", "Bob", valid=False)
    _build_zip(zip_file, submissions_dir)

    grader = MultiGrader.from_zip(str(config_file), str(zip_file), repetitions=1)
    results = grader.grade_all(debug=False)

    assert len(results) == 2
    statuses = {entry["status"] for entry in results}
    assert "graded" in statuses
    assert "load_error" in statuses


def test_write_csv_exports_result_rows(tmp_path: Path) -> None:
    config_file = tmp_path / "grader.yaml"
    zip_file = tmp_path / "players.zip"
    result_file = tmp_path / "result.csv"
    submissions_dir = tmp_path / "submissions"
    submissions_dir.mkdir()

    _write_configuration(config_file)
    _write_player_file(submissions_dir / "student_a.py", "Alice", valid=True)
    _build_zip(zip_file, submissions_dir)

    grader = MultiGrader.from_zip(str(config_file), str(zip_file), repetitions=1)
    grader.grade_all(debug=False)
    grader.write_csv(str(result_file))

    with result_file.open("r", encoding="utf-8", newline="") as csv_file:
        rows = list(csv.DictReader(csv_file))

    assert len(rows) == 1
    assert rows[0]["status"] == "graded"
    assert rows[0]["authors"] == "Alice"


def test_from_zip_accepts_trials_key(tmp_path: Path) -> None:
    config_file = tmp_path / "grader.yaml"
    zip_file = tmp_path / "players.zip"
    submissions_dir = tmp_path / "submissions"
    submissions_dir.mkdir()

    _write_configuration_with_trials(config_file)
    _write_player_file(submissions_dir / "student_a.py", "Alice", valid=True)
    _build_zip(zip_file, submissions_dir)

    grader = MultiGrader.from_zip(str(config_file), str(zip_file), repetitions=1)

    assert len(grader.trial_definitions) == 1


def test_from_zip_loads_notebook_players_with_token(tmp_path: Path) -> None:
    config_file = tmp_path / "grader.yaml"
    zip_file = tmp_path / "players.zip"
    submissions_dir = tmp_path / "submissions"
    submissions_dir.mkdir()

    _write_configuration_with_trials(config_file)
    _write_notebook_player_file(submissions_dir / "student_a.ipynb", "Alice", token="CUSTOM_TOKEN")
    _build_zip(zip_file, submissions_dir)

    grader = MultiGrader.from_zip(str(config_file), str(zip_file), repetitions=1, token="CUSTOM_TOKEN")

    assert len(grader.players) == 1
    assert grader.token == "CUSTOM_TOKEN"
    assert grader.players[0]["player"] is not None
