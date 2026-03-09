"""Tests for local and online text loading helpers."""

from __future__ import annotations

import importlib
from pathlib import Path

import pytest

from iarena.utilizing.filing.FileLoader import FileLoader


class _DummyResponse:
    """Small context-manager response used to mock urlopen in tests."""

    def __init__(self, content: bytes) -> None:
        self._content = content

    def __enter__(self) -> _DummyResponse:
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        _ = (exc_type, exc, traceback)

    def read(self) -> bytes:
        return self._content


def test_read_file_reads_local_path(tmp_path: Path) -> None:
    source_file = tmp_path / "payload.txt"
    source_file.write_text("local-content", encoding="utf-8")

    content = FileLoader.read_file(str(source_file))

    assert content == "local-content"


def test_read_file_reads_online_url_when_enabled(monkeypatch: pytest.MonkeyPatch) -> None:
    def _fake_urlopen(filename: str, timeout: int) -> _DummyResponse:
        assert filename == "https://example.com/data.txt"
        assert timeout == 30
        return _DummyResponse(b"online-content")

    module = importlib.import_module("iarena.utilizing.filing.FileLoader")
    monkeypatch.setattr(module, "urlopen", _fake_urlopen)

    content = FileLoader.read_file("https://example.com/data.txt", allow_online=True)

    assert content == "online-content"


def test_read_file_rejects_online_url_when_disabled() -> None:
    with pytest.raises(PermissionError, match="allow_online=False"):
        _ = FileLoader.read_file("https://example.com/data.txt", allow_online=False)


def test_read_file_raises_for_directory(tmp_path: Path) -> None:
    with pytest.raises(IsADirectoryError, match="Expected a file path"):
        _ = FileLoader.read_file(str(tmp_path))
