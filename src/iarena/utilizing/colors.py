"""Color parsing helpers."""

from __future__ import annotations

from typing import Any


class Color(str):
    """Normalized hexadecimal color string."""

    @staticmethod
    def _normalize_hex(value: str) -> str:
        text = value.strip().lower()
        if not text.startswith("#"):
            text = f"#{text}"

        if len(text) == 4:
            text = f"#{text[1] * 2}{text[2] * 2}{text[3] * 2}"

        if len(text) != 7:
            raise ValueError(f"Invalid color value: {value!r}")

        int(text[1:], 16)
        return text

    @classmethod
    def from_string(cls, value: str) -> "Color":
        """Build from a textual color representation."""
        return cls(cls._normalize_hex(value))

    @classmethod
    def from_value(cls, value: Any) -> "Color":
        """Build from a tuple/list rgb triplet or string value."""
        if isinstance(value, cls):
            return value

        if isinstance(value, str):
            return cls.from_string(value)

        if isinstance(value, (tuple, list)) and len(value) == 3:
            channels: list[int] = []
            for channel in value:
                channel_int = int(channel)
                if channel_int < 0 or channel_int > 255:
                    raise ValueError(f"RGB channel out of range: {channel!r}")
                channels.append(channel_int)
            return cls(f"#{channels[0]:02x}{channels[1]:02x}{channels[2]:02x}")

        raise TypeError(f"Unsupported color value: {value!r}")
