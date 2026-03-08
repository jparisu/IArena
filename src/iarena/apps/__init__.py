"""Application entrypoints for interactive and executable IArena workflows."""

from .streamlit import StreamlitApplication
from .terminal import TerminalApplication

__all__ = ["TerminalApplication", "StreamlitApplication"]
