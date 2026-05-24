from __future__ import annotations

import pytest

from iarena.arening.Arena import Arena


def test_arena_cannot_be_instantiated_without_implementing_play() -> None:
    class _IncompleteArena(Arena):
        pass

    with pytest.raises(TypeError):
        _IncompleteArena()

