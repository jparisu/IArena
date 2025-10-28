import argparse
import sys
from pathlib import Path
import zipfile
from tempfile import TemporaryDirectory, mkdtemp

from IArena.grader.AutoGrader import MultipleAutoGrader

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


def extract_zip_to_tmp(zip_path: Path, keep_tmp: bool) -> Path:
    """
    Extract ZIP to a temp directory and return its path.
    If keep_tmp=False, returns a TemporaryDirectory-managed path that
    will be deleted by the caller's context manager.
    """
    if keep_tmp:
        tmpdir = mkdtemp(prefix="_multiautograder_")
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(tmpdir)
        return Path(tmpdir)
    else:
        # We'll delegate cleanup to the surrounding TemporaryDirectory context
        # by extracting into that directory.
        raise RuntimeError(
            "extract_zip_to_tmp(keep_tmp=False) is only used within a TemporaryDirectory context."
        )


def get_ipynb_files(directory: Path) -> list[Path]:
    """Get a list of all .ipynb files in the given directory."""
    return list(directory.rglob("*.ipynb"))


def main():
    """Main entry point of the script."""

    # Parse args
    args = parse_args()
    configuration_file_str = str(args.configuration_file)
    zip_file_str = str(args.zip_file)
    result_file_str = str(args.result_file)
    debug_mode = args.debug
    keep_tmp = args.keep_tmp

    # Extract zip to temp directory
    zip_path = Path(zip_file_str)
    files_dir = extract_zip_to_tmp(zip_path, keep_tmp=keep_tmp)
    files = get_ipynb_files(files_dir)

    # Build and run multi autograder
    grader = MultipleAutoGrader(
        configuration_filename=configuration_file_str,
        notebook_filenames=[str(f) for f in files],
        result_filename=result_file_str,
    )



if __name__ == "__main__":
    main()
