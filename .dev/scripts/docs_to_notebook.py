#!/usr/bin/env python3
"""
Convert Python code fences in a Markdown file into a Jupyter notebook.

Usage:
    python md_to_ipynb.py input.md
    python md_to_ipynb.py input.md -o output.ipynb

Behavior:
- Extracts fenced code blocks marked as Python:
    ```python
    ...
    ```
  and also common variants like:
    ```py
    ```
- Creates one notebook code cell per extracted block.
- Ignores non-Python fences.

This is useful for turning Markdown tutorials into notebooks for execution/testing.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
from typing import List


PYTHON_FENCE_RE = re.compile(
    r"(^|\n)```(?:python|py)\s*\n(.*?)\n```(?=\n|$)",
    re.DOTALL | re.IGNORECASE,
)


def extract_python_blocks(markdown_text: str) -> List[str]:
    """Return all Python fenced code blocks from markdown text."""
    matches = PYTHON_FENCE_RE.findall(markdown_text)
    return [code.rstrip() + "\n" for _, code in matches]


def make_notebook(cells: List[str]) -> dict:
    """Build a minimal Jupyter notebook structure."""
    return {
        "cells": [
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": code.splitlines(keepends=True),
            }
            for code in cells
        ],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {
                "name": "python",
                "version": sys.version.split()[0],
            },
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


def convert_markdown_to_notebook(input_path: pathlib.Path, output_path: pathlib.Path) -> None:
    """Read markdown, extract Python blocks, and write notebook."""
    markdown_text = input_path.read_text(encoding="utf-8")
    code_blocks = extract_python_blocks(markdown_text)

    if not code_blocks:
        raise ValueError(f"No Python code fences found in: {input_path}")

    notebook = make_notebook(code_blocks)
    output_path.write_text(json.dumps(notebook, indent=2), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert Python code fences in a Markdown file into a .ipynb notebook."
    )
    parser.add_argument("input_md", type=pathlib.Path, help="Path to input Markdown file")
    parser.add_argument(
        "-o",
        "--output",
        type=pathlib.Path,
        help="Path to output notebook file (default: same name with .ipynb extension)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_path: pathlib.Path = args.input_md

    if not input_path.exists():
        print(f"Error: file not found: {input_path}", file=sys.stderr)
        return 1

    if not input_path.is_file():
        print(f"Error: not a file: {input_path}", file=sys.stderr)
        return 1

    output_path = args.output or input_path.with_suffix(".ipynb")

    try:
        convert_markdown_to_notebook(input_path, output_path)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"Notebook written to: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
