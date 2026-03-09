"""Command-line script to grade one player file against one YAML exam configuration."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def _ensure_src_on_path() -> None:
    """Ensure local `src` directory is importable when running from repository root.

    Returns:
        None.
    """
    repository_root = Path(__file__).resolve().parent.parent
    src_path = repository_root / "src"
    if src_path.exists():
        resolved_src = str(src_path)
        if resolved_src not in sys.path:
            sys.path.insert(0, resolved_src)


_ensure_src_on_path()

from iarena.grading.AutoGrader import AutoGrader  # noqa: E402
from iarena.grading.DebugLevel import DebugLevel  # noqa: E402
from iarena.grading.MatchReport import MatchReport  # noqa: E402


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for the single-player grader script.

    Returns:
        argparse.Namespace: Parsed command-line argument values.
    """
    parser = argparse.ArgumentParser(
        description="Grade one player source file (`.py` or `.ipynb`) using one YAML grading configuration.",
    )
    parser.add_argument(
        "-c",
        "--configuration-file",
        type=str,
        required=True,
        help="Path to the YAML grading configuration file.",
    )
    parser.add_argument(
        "-p",
        "--player-file",
        type=str,
        required=True,
        help="Path to the player file (`.py` or `.ipynb`) exposing `PLAYER`.",
    )
    parser.add_argument(
        "-t",
        "--token",
        type=str,
        default="PLAYER =",
        help="Notebook cell selector token used for `.ipynb` player files.",
    )
    parser.add_argument(
        "-o",
        "--output-file",
        type=str,
        default="",
        help="Optional path to write JSON grading output.",
    )
    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help="Enable debug grading mode.",
    )
    return parser.parse_args()


def _summarize_reports(grouped_reports: list[list[MatchReport]]) -> dict[str, int]:
    """Summarize grouped match reports into high-level counters.

    Args:
        grouped_reports: Nested reports grouped by trial.

    Returns:
        dict[str, int]: Aggregate counters over trials and matches.
    """
    n_trials = len(grouped_reports)
    n_matches = sum(len(trial_reports) for trial_reports in grouped_reports)
    n_error_matches = 0
    n_warning_matches = 0

    for trial_reports in grouped_reports:
        for report in trial_reports:
            messages = getattr(report, "messages", {})
            if messages.get("errors") or messages.get("error"):
                n_error_matches += 1
            if messages.get("warnings"):
                n_warning_matches += 1

    return {
        "n_trials": n_trials,
        "n_matches": n_matches,
        "n_error_matches": n_error_matches,
        "n_warning_matches": n_warning_matches,
    }


def _build_result(args: argparse.Namespace) -> dict[str, Any]:
    """Build the grading result dictionary from command-line inputs.

    Args:
        args: Parsed command-line arguments.

    Returns:
        dict[str, Any]: Serializable grading result payload.
    """
    autograder = AutoGrader.from_files(
        configuration_file=str(args.configuration_file),
        player_file=str(args.player_file),
        token=str(args.token),
    )
    debug_level = DebugLevel.DEBUG if bool(args.debug) else DebugLevel.USER
    grouped_reports = autograder.grader.grade(debug_level=debug_level)
    summary = _summarize_reports(grouped_reports=grouped_reports)

    return {
        "configuration_file": str(args.configuration_file),
        "player_file": str(args.player_file),
        "token": str(args.token),
        "score": float(autograder.grader.score()),
        "debug_level": debug_level.name,
        **summary,
    }


def main() -> None:
    """Run the single-player grading script and print results.

    Returns:
        None.
    """
    args = parse_args()

    try:
        result = _build_result(args=args)
    except Exception as error:  # pragma: no cover - integration behavior
        print(f"Grading failed: {type(error).__name__}: {error}", file=sys.stderr)
        raise SystemExit(1) from error

    serialized_result = json.dumps(result, indent=2, sort_keys=True)
    print(serialized_result)

    output_file = str(args.output_file).strip()
    if output_file:
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(serialized_result + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
