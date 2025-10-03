import argparse
import sys
from pathlib import Path

from IArena.grader.AutoGrader import IndividualCompleteAutoGrader



def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Process configuration and code files."
    )

    parser.add_argument(
        "-c", "--configuration-file",
        type=Path,
        required=True,
        help="Path to the configuration file."
    )

    parser.add_argument(
        "-x", "--code-file",
        type=Path,
        required=True,
        help="Path to the code file."
    )

    return parser.parse_args()


def main():
    """Main entry point of the script."""
    args = parse_args()

    if not args.configuration_file.exists():
        print("Error: Configuration file not found!", file=sys.stderr)
        sys.exit(1)

    if not args.code_file.exists():
        print("Error: Code file not found!", file=sys.stderr)
        sys.exit(1)

    # Grade code
    IndividualCompleteAutoGrader(configuration_filename=args.configuration_file, player_filename=args.code_file).grade()


if __name__ == "__main__":
    main()
