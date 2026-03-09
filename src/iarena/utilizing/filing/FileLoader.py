"""Defines text file-loading helpers for local paths and online URLs."""

from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse
from urllib.request import urlopen


class FileLoader:
    """Utility class that reads text content from local files or URLs.

    Purpose:
        Provide a single entry point to read text from local paths and HTTP(S)
        resources.
    How it works:
        Detects whether `filename` is an HTTP(S) URL and delegates to online
        fetching when enabled; otherwise it reads from local disk.
    Used for:
        Loading configuration or data files regardless of whether they are
        stored locally or hosted online.
    Public Attributes:
        None declared at class level in this utility class.
    """

    @classmethod
    def read_file(cls, filename: str, allow_online: bool = True) -> str:
        """Read one file from local disk or from an online URL.

        What it does:
            Returns text content for `filename`.
        How it works:
            If `filename` is an HTTP(S) URL, the method fetches it when
            `allow_online` is true; otherwise it raises an error.
            For non-URL values, it reads the local file as UTF-8 text.
        Args:
            filename (str): Local file path or HTTP(S) URL.
            allow_online (bool): Whether online URL loading is permitted.
        Returns:
            str: File content decoded as UTF-8 text.
        Raises:
            PermissionError: If `filename` is an HTTP(S) URL and online reads
                are disabled.
            FileNotFoundError: If local file path does not exist.
            IsADirectoryError: If local file path points to a directory.
            OSError: If reading from disk or URL fails.
        """
        _ = cls
        parsed = urlparse(filename)
        is_http_url = parsed.scheme in {"http", "https"} and bool(parsed.netloc)
        if is_http_url:
            if not allow_online:
                raise PermissionError("Online file loading is disabled by `allow_online=False`.")
            with urlopen(filename, timeout=30) as response:  # noqa: S310
                return response.read().decode("utf-8")

        source_path = Path(filename)
        if source_path.is_dir():
            raise IsADirectoryError(f"Expected a file path, got directory: {source_path}")
        return source_path.read_text(encoding="utf-8")
