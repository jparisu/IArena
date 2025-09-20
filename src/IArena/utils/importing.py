from typing import List
import json
import tempfile
import importlib.util
import sys
import os
import uuid
from pathlib import Path


def import_class_from_module(
            module_path: str,
            class_name: str,
        ) -> type:
    """
    Dynamically load a class from a module.
    """
    module = __import__(module_path, fromlist=[class_name],)
    return getattr(module, class_name)



def get_cell_from_ipynb(
            notebook_path: str,
            markers: List[str],
        ) -> str:
    """
    Execute a Jupyter notebook cell that contains one of the specified markers with a new temporary .py file.
    """
    # load notebook
    with open(notebook_path, encoding="utf-8") as f:
        nb = json.load(f)

    # find the cell
    code_cells = [c for c in nb["cells"] if c.get("cell_type") == "code"]
    src = None
    for cell in code_cells:
        text = "".join(cell.get("source", []))
        if any(m in text for m in markers):
            src = text
            break
    if src is None:
        raise ValueError(f"No cell with markers {markers} found")

    return src


def execute_str_as_module(
            code_str: str,
        ) -> object:
    """
    Execute a string of code as a new temporary .py file.
    """
    # write to temp file
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as tmp:
        tmp.write(code_str)
        tmp_path = tmp.name

    # import as a module
    mod_name = f"submission_{uuid.uuid4().hex}"
    spec = importlib.util.spec_from_file_location(mod_name, tmp_path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = mod
    spec.loader.exec_module(mod)

    # cleanup
    os.remove(tmp_path)

    return mod


def extract_marker_values(filename: str, marker: str) -> List[str]:
    """
    Find all lines starting with a marker (e.g. '@AUTHOR:') in a .py or .ipynb file.
    Returns a list of the values after the marker (ignores blanks).
    """
    path = Path(filename)
    results: List[str] = []

    if path.suffix == ".ipynb":
        with open(path, encoding="utf-8") as f:
            nb = json.load(f)
        for cell in nb.get("cells", []):
            if cell.get("cell_type") != "code":
                continue
            for line in cell.get("source", []):
                line = line.strip()
                if marker in line:
                    value = line.split(marker, 1)[-1].strip()
                    if value:
                        results.append(value)

    elif path.suffix == ".py":
        with open(path, encoding="utf-8") as f:
            for raw in f:
                line = raw.strip()
                if marker in line:
                    value = line.split(marker, 1)[-1].strip()
                    if value:
                        results.append(value)

    else:
        raise ValueError(f"Unsupported file type: {path.suffix}")

    return results
