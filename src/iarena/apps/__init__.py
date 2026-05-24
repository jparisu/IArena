"""Application entrypoints for interactive and executable IArena workflows."""

from iarena.apps.streamlit import StreamlitApplication
from iarena.apps.terminal import TerminalApplication

__all__ = ["TerminalApplication", "StreamlitApplication"]
