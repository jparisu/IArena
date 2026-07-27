# IArena

`IArena` is a Python project scaffolded from this template.

## Features

- Modern `src/`-layout packaging
- Ruff, mypy, pytest, coverage, and pre-commit
- MkDocs + mkdocstrings documentation



## Installation

From Git:

```bash
python -m pip install "git+https://github.com/jparisu/iarena.git"
```

From a local checkout:

```bash
python -m pip install .
```

For development:

```bash
python -m pip install -e ".[dev]"
pre-commit install
```

## Quick Start

```python
import iarena

print(iarena.__version__)
```



## Development

Useful commands:

```bash
make install
make install-current
make lint
make test
make docs
```

## License

Licensed under the Apache 2.0 License.
