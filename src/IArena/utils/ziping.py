
import os
import zipfile
import tempfile
from typing import List

def unzip_get_files(
        zip_filename: str,
        extract_to: str = None
    ) -> List[str]:
    """
    Unzip a zip file to a temporary directory and return the list of extracted files.

    If extract_to is None, a temporary directory will be created.
    """
    if not os.path.exists(zip_filename):
        raise FileNotFoundError(f"Zip file {zip_filename} does not exist.")

    if extract_to is None:
        extract_to = tempfile.mkdtemp()

    with zipfile.ZipFile(zip_filename, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

    # Get the list of extracted files
    extracted_files = []
    for root, dirs, files in os.walk(extract_to):
        for file in files:
            extracted_files.append(os.path.join(root, file))

    return extracted_files
