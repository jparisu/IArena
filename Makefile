.PHONY: venv install install-current ensure-git precommit lint format test docs build clean

VENV ?= .venv
PYTHON ?= python3
PRE_COMMIT_ARGS ?= --all-files
PRE_COMMIT_SKIP ?=
TEST_ARGS ?= tests -v
VENV_PYTHON := $(VENV)/bin/python
VENV_PIP := $(VENV)/bin/pip
VENV_PRE_COMMIT := $(VENV)/bin/pre-commit
VENV_RUFF := $(VENV)/bin/ruff
VENV_MYPY := $(VENV)/bin/mypy
VENV_PYTEST := $(VENV)/bin/pytest
VENV_MKDOCS := $(VENV)/bin/mkdocs
VENV_BUILD := $(VENV)/bin/python -m build

venv:
	$(PYTHON) -m venv $(VENV)

install: venv
	$(VENV_PYTHON) -m pip install --upgrade pip
	$(VENV_PIP) install -e ".[dev]"

install-current:
	python -m pip install --upgrade pip
	python -m pip install -e ".[dev]"

ensure-git:
	@if [ ! -d .git ]; then git init -q; fi

precommit: ensure-git
	SKIP=$(PRE_COMMIT_SKIP) $(VENV_PRE_COMMIT) run $(PRE_COMMIT_ARGS)

lint:
	$(VENV_RUFF) check src tests
	$(VENV_RUFF) format --diff --check src tests
	$(VENV_MYPY) src/iarena

format:
	$(VENV_RUFF) check --fix src tests
	$(VENV_RUFF) format src tests

test:
	$(VENV_PYTEST) $(TEST_ARGS)

docs:
	$(VENV_MKDOCS) build --strict

build:
	$(VENV_BUILD)

test-all: lint format test docs

clean:
	rm -rf build dist .coverage .pytest_cache .mypy_cache .ruff_cache site
