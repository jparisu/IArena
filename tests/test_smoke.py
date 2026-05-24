from iarena import __version__


def test_version_exposed() -> None:
    assert __version__ == "3.0.0"
