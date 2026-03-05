"""Tests for the Streamlit application entrypoint."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest


class _FakeStreamlit:
    """Small Streamlit-like test double used by entrypoint tests."""

    def __init__(self) -> None:
        """Initialize fake state.

        Args:
            None.

        Returns:
            None.
        """
        self.page_config_calls: list[dict[str, object]] = []

    def set_page_config(self, page_title: str, layout: str) -> None:
        """Record page configuration calls.

        Args:
            page_title: Requested page title.
            layout: Requested layout mode.

        Returns:
            None.
        """
        self.page_config_calls.append({"page_title": page_title, "layout": layout})


def _load_streamlit_app_module() -> ModuleType:
    """Load ``app/streamlit_app.py`` as a Python module for testing.

    Args:
        None.

    Returns:
        Loaded module object.
    """
    file_path = Path(__file__).resolve().parents[2] / "app" / "streamlit_app.py"
    spec = importlib.util.spec_from_file_location("test_app_streamlit_app", file_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to build import spec for app/streamlit_app.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_main_configures_streamlit_and_renders_index(monkeypatch: pytest.MonkeyPatch) -> None:
    """Main entrypoint should configure page and render the game index.

    Args:
        monkeypatch: Pytest monkeypatch fixture.

    Returns:
        None.
    """
    module = _load_streamlit_app_module()
    fake_streamlit = _FakeStreamlit()
    expected_index = object()
    calls: list[tuple[object, object]] = []

    monkeypatch.setattr("iarena.apping.build_default_game_index", lambda: expected_index)
    monkeypatch.setattr(
        "iarena.apping.render_games_index_page",
        lambda streamlit_api, game_index: calls.append((streamlit_api, game_index)),
    )

    module.main(fake_streamlit)

    assert fake_streamlit.page_config_calls == [{"page_title": "IArena", "layout": "wide"}]
    assert calls == [(fake_streamlit, expected_index)]


def test_ensure_project_src_on_path(monkeypatch: pytest.MonkeyPatch) -> None:
    """Entrypoint helper should add the repository ``src`` directory to ``sys.path``.

    Args:
        monkeypatch: Pytest monkeypatch fixture.

    Returns:
        None.
    """
    module = _load_streamlit_app_module()
    initial_sys_path: list[str] = ["/tmp/a", "/tmp/b"]
    monkeypatch.setattr(module.sys, "path", initial_sys_path)

    module._ensure_project_src_on_path()
    module._ensure_project_src_on_path()

    expected_src = str((Path(__file__).resolve().parents[2] / "src").resolve())
    assert initial_sys_path[0] == expected_src
    assert initial_sys_path.count(expected_src) == 1
