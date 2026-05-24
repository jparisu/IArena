"""Declares the streamlit container wrapper type used by visualization architecture."""

from __future__ import annotations


class StreamlitContainer:
    """Lightweight wrapper around one streamlit-like render container.

    Purpose:
        Provides a stable container type for streamlit views while still accepting
        native streamlit container objects.
    How it works:
        Stores one wrapped object and delegates rendering calls/attributes to it.
    Used for:
        Keeping streamlit view contracts type-safe without directly depending on
        streamlit classes in core modules.
    Public Attributes:
        container (object | None): Wrapped streamlit-like container object.
    """

    container: object | None

    def __init__(self, container: object | None = None) -> None:
        """Create one container wrapper.

        Args:
            container: Optional wrapped streamlit-like object exposing render APIs.

        Returns:
            None.
        """
        self.container = container

    def __getattr__(self, item: str) -> object:
        """Delegate unknown attributes to the wrapped container.

        Args:
            item: Attribute name requested on this wrapper.

        Returns:
            object: Attribute value resolved from the wrapped container.

        Raises:
            AttributeError: If no wrapped container exists or it lacks `item`.
        """
        if self.container is None:
            raise AttributeError(f"StreamlitContainer has no wrapped container for attribute '{item}'.")
        return getattr(self.container, item)

    def write(self, message: object) -> None:
        """Write content to the wrapped container when supported.

        Args:
            message: Payload to render.

        Returns:
            None.
        """
        writer = getattr(self.container, "write", None)
        if callable(writer):
            writer(message)

    def markdown(self, message: str, **kwargs: object) -> None:
        """Render markdown content to the wrapped container when supported.

        Args:
            message: Markdown text payload.
            **kwargs: Additional keyword arguments forwarded to markdown backend.

        Returns:
            None.
        """
        markdown_writer = getattr(self.container, "markdown", None)
        if callable(markdown_writer):
            markdown_writer(message, **kwargs)

    def text(self, message: str) -> None:
        """Render plain text content to the wrapped container when supported.

        Args:
            message: Text payload.

        Returns:
            None.
        """
        text_writer = getattr(self.container, "text", None)
        if callable(text_writer):
            text_writer(message)
