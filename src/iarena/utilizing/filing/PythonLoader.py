"""Provides helpers to execute Python files and extract typed module variables."""

from __future__ import annotations

import hashlib
from types import ModuleType
from typing import Any

from iarena.utilizing.filing.FileLoader import FileLoader


class PythonLoader:
    """Utility class for loading Python files and reading selected variables.

    Purpose:
        Provides the `PythonLoader` type within the IArena architecture.
    How it works:
        Executes one Python module from disk and returns requested module-level variables.
    Used for:
        Loading user-defined data or objects from standalone Python scripts.
    Public Attributes:
        None declared at class level in this utility class.
    """

    @classmethod
    def _load_module(cls, filename: str) -> ModuleType:
        """Execute one Python source file and return its loaded module object.

        What it does:
            Loads Python source from one local path or URL and executes it.
        How it works:
            Reads source text through `FileLoader`, executes it in one module
            namespace, and returns the populated module instance.
        Args:
            filename (str): Local path or HTTP(S) URL to execute.
        Returns:
            ModuleType: Executed module object containing module-level variables.
        Raises:
            FileNotFoundError: If local `filename` does not exist.
            IsADirectoryError: If local `filename` points to a directory.
            OSError: If the source content cannot be read.
            ImportError: If the file cannot be imported or executed as a module.
        """
        _ = cls
        source_code = FileLoader.read_file(filename=filename)
        stable_suffix = hashlib.sha256(filename.encode("utf-8")).hexdigest()[:12]
        module_name = f"_iarena_loader_{stable_suffix}"
        module = ModuleType(module_name)
        module.__file__ = filename

        try:
            compiled = compile(source_code, filename, "exec")
            exec(compiled, module.__dict__)  # noqa: S102  # pylint: disable=exec-used
        except Exception as exc:
            raise ImportError(f"Failed to execute file: {filename}") from exc
        return module

    @classmethod
    def load_file(
        cls,
        filename: str,
        variable_names: list[str],
        force_types: list[str] | None = None,
    ) -> dict[str, Any]:
        """Load variables from one Python file with optional runtime type-name validation.

        What it does:
            Executes a file and extracts specific module variables by name.
        How it works:
            Loads the module once, validates requested variable presence, and optionally enforces declared type names.
        Args:
            filename (str): Path to the Python source file to execute.
            variable_names (list[str]): Names of variables expected in the module.
            force_types (list[str] | None): Optional list of expected runtime type names aligned with `variable_names`.
        Returns:
            dict[str, Any]: Mapping from requested variable names to loaded values.
        Raises:
            ValueError: If `variable_names` is empty, if one variable is missing, or if type constraints fail.
        """
        if not variable_names:
            raise ValueError("At least one variable name must be provided.")

        if force_types is not None and len(force_types) != len(variable_names):
            raise ValueError("force_types must have the same length as variable_names.")

        module = cls._load_module(filename=filename)
        loaded_variables: dict[str, Any] = {}

        for index, variable_name in enumerate(variable_names):
            if not hasattr(module, variable_name):
                raise ValueError(f"Missing required variable '{variable_name}' in file: {filename}")

            value = getattr(module, variable_name)
            if force_types is not None:
                expected_type_name = force_types[index]
                loaded_type_name = type(value).__name__
                if loaded_type_name != expected_type_name:
                    raise ValueError(
                        f"Variable '{variable_name}' must be of type '{expected_type_name}', got '{loaded_type_name}'.",
                    )
            loaded_variables[variable_name] = value

        return loaded_variables
