"""Tests for dynamic Python file loading helpers."""

from __future__ import annotations

import importlib
from pathlib import Path

import pytest

from iarena.utilizing.filing.Loader import Loader


def test_loader_load_file_returns_requested_variables(tmp_path: Path) -> None:
    source_file = tmp_path / "dummy_payload.py"
    source_file.write_text(
        """
NUMBER = 7
WORDS = ["alpha", "beta"]
FLAG = True
""".strip(),
        encoding="utf-8",
    )

    payload = Loader.load_file(
        filename=str(source_file),
        variable_names=["NUMBER", "WORDS", "FLAG"],
        force_types=["int", "list", "bool"],
    )

    assert payload["NUMBER"] == 7
    assert payload["WORDS"] == ["alpha", "beta"]
    assert payload["FLAG"] is True


def test_loader_load_file_rejects_missing_variable(tmp_path: Path) -> None:
    source_file = tmp_path / "dummy_missing.py"
    source_file.write_text("ONLY = 1", encoding="utf-8")

    with pytest.raises(ValueError, match="Missing required variable 'PLAYER'"):
        Loader.load_file(filename=str(source_file), variable_names=["PLAYER"])


def test_loader_load_file_rejects_type_mismatch(tmp_path: Path) -> None:
    source_file = tmp_path / "dummy_wrong_type.py"
    source_file.write_text("VALUE = 12", encoding="utf-8")

    with pytest.raises(ValueError, match="must be of type 'str'"):
        Loader.load_file(filename=str(source_file), variable_names=["VALUE"], force_types=["str"])


def test_loader_load_file_rejects_invalid_force_types_length(tmp_path: Path) -> None:
    source_file = tmp_path / "dummy_length.py"
    source_file.write_text("VALUE = 12", encoding="utf-8")

    with pytest.raises(ValueError, match="same length as variable_names"):
        Loader.load_file(filename=str(source_file), variable_names=["VALUE"], force_types=["int", "str"])


def test_loader_load_file_supports_online_sources(monkeypatch: pytest.MonkeyPatch) -> None:
    module = importlib.import_module("iarena.utilizing.filing.PythonLoader")
    monkeypatch.setattr(
        module.FileLoader,
        "read_file",
        classmethod(lambda cls, filename, allow_online=True: "VALUE = 42\n"),
    )

    payload = Loader.load_file(filename="https://example.com/player.py", variable_names=["VALUE"])

    assert payload["VALUE"] == 42
