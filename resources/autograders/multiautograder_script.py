import argparse
import sys
from pathlib import Path
import zipfile
from tempfile import TemporaryDirectory, mkdtemp

from IArena.grader.MultipleAutoGrader import MultipleAutoGrader

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
        "-z", "--zip-file",
        type=str,
        required=True,
        help="Path to the zip file with the code."
    )

    parser.add_argument(
        "-r", "--result-file",
        type=str,
        required=True,
        help="Name of the result csv file."
    )

    parser.add_argument(
        "-d", "--debug",
        action="store_true",
        help="Enable debug mode."
    )

    parser.add_argument(
        "--keep-tmp",
        action="store_true",
        help="Keep temporary extracted files for debugging.",
    )

    return parser.parse_args()


def main():
    """Main entry point of the script."""

    # Parse args
    args = parse_args()
    configuration_file_str = str(args.configuration_file)
    zip_file_str = str(args.zip_file)
    result_file_str = str(args.result_file)
    debug_mode = args.debug
    keep_tmp = args.keep_tmp

    # Build and run multi autograder
    grader = MultipleAutoGrader.from_zip(
        configuration_filename=configuration_file_str,
        zip_filename=zip_file_str,
    )

    # Grade all
    grader.grade_all(debug=debug_mode)

    # Write results to CSV
    grader.write_csv(result_file_str)



if __name__ == "__main__":
    main()
