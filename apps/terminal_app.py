"""Executable terminal entrypoint for IArena's terminal application."""

from __future__ import annotations

import sys
from pathlib import Path


def _ensure_src_on_path() -> None:
    """Ensure local `src` directory is importable when running from repository root."""
    repository_root = Path(__file__).resolve().parent.parent
    src_path = repository_root / "src"
    if src_path.exists():
        resolved_src = str(src_path)
        if resolved_src not in sys.path:
            sys.path.insert(0, resolved_src)


_ensure_src_on_path()

from iarena.apps.terminal import TerminalApplication  # noqa: E402


def main() -> None:
    """Run the terminal application main flow."""
    TerminalApplication().main()


if __name__ == "__main__":
    main()
