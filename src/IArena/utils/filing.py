
from typing import List, Dict
import yaml
import os
import requests
import tempfile
from IArena.utils.importing import import_class_from_module, get_cell_from_ipynb, execute_str_as_module, extract_marker_values


def read_file_or_url(filename: str) -> str:
    """
    Read a file or URL and return its contents as a string.
    """

    if filename.startswith('http'):
        response = requests.get(filename)
        response.raise_for_status()
        return response.text
    else:
        if not os.path.exists(filename):
            raise FileNotFoundError(f"File {filename} does not exist.")
        with open(filename, 'r') as file:
            return file.read()


def read_yaml(str_file: str) -> Dict:
    """
    Read a YAML str and return its contents as a dictionary.
    """
    return yaml.safe_load(str_file)


def get_vars_from_file(
            filename: str,
            var_names: List[str],
            markers: List[str],
            types_allowed: Dict[str, List[type]] = None
        ) -> Dict[str, object]:
    """
    Given a local python file name, reads and execute the code.

    If it is a .py file, it will be executed directly.
    If it is a .ipynb file, find the code cell that contains any of the markers, and execute its content.
    """

    if not os.path.exists(filename):
        raise FileNotFoundError(f"File {filename} does not exist.")

    code_text = ""

    if filename.endswith('.py'):
        with open(filename, 'r') as file:
            code_text = file.read()

    elif filename.endswith('.ipynb'):
        code_text = get_cell_from_ipynb(filename, markers)

    else:
        raise ValueError(f"Unsupported file extension for file {filename}. Only .py and .ipynb are supported.")

    # Execute the code as a module
    module = execute_str_as_module(code_text)

    vars_dict = {}

    for var_name in var_names:
        # Get the var
        if not hasattr(module, var_name):
            raise ValueError(f"Variable {var_name} not found in file {filename}.")
        var = getattr(module, var_name)

        # Check types
        if var_name in types_allowed:
            allowed_types = types_allowed[var_name]

            if not any(isinstance(var, t) for t in allowed_types):
                allowed_types_names = [t.__name__ for t in allowed_types]
                raise ValueError(f"Variable {var_name} in file {filename} is not of allowed types: {allowed_types_names}. Found type: {type(var).__name__}")

        vars_dict[var_name] = var

    return vars_dict
