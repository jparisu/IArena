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
        type=str,
        required=True,
        help="Path to the configuration file."
    )

    parser.add_argument(
        "-x", "--code-file",
        type=str,
        required=True,
        help="Path to the code file."
    )

    return parser.parse_args()


def main():
    """Main entry point of the script."""
    args = parse_args()

    configuration_file_str = str(args.configuration_file)
    code_file_str = str(args.code_file)

    # Grade code
    IndividualCompleteAutoGrader(configuration_filename=configuration_file_str, player_filename=code_file_str).grade()


if __name__ == "__main__":
    main()
