"""Streamlit entrypoint for the IArena multi-game application."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


def _project_root() -> Path:
    """Return repository root path for this application.

    Args:
        None.

    Returns:
        Absolute path to repository root directory.
    """
    return Path(__file__).resolve().parents[1]


def _src_directory() -> Path:
    """Return source-directory path containing the ``iarena`` package.

    Args:
        None.

    Returns:
        Absolute path to ``src`` directory.
    """
    return _project_root() / "src"


def _ensure_project_src_on_path() -> None:
    """Ensure local ``src`` directory is importable in script execution mode.

    Args:
        None.

    Returns:
        None.
    """
    src_directory = str(_src_directory())
    if src_directory not in sys.path:
        sys.path.insert(0, src_directory)


def main(streamlit_api: Any | None = None) -> None:
    """Run the Streamlit IArena app.

    Args:
        streamlit_api: Optional Streamlit-compatible module-like object. If
            ``None``, imports and uses the real ``streamlit`` module.

    Returns:
        None.
    """
    _ensure_project_src_on_path()
    from iarena.apping import build_default_game_index, render_games_index_page

    if streamlit_api is None:
        import streamlit as streamlit_module

        streamlit_api = streamlit_module

    streamlit_api.set_page_config(page_title="IArena", layout="wide")
    render_games_index_page(
        streamlit_api=streamlit_api,
        game_index=build_default_game_index(),
    )


if __name__ == "__main__":
    main()
