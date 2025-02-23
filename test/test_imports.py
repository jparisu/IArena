import importlib.util
import os
import pytest

src_directory = "src"  # Adjust if your source files are in a different directory
library_name = "IArena"

@pytest.mark.parametrize("file_path", [
    os.path.join(dp, f) for dp, dn, filenames in os.walk(src_directory)
    for f in filenames if f.endswith('.py') and not f.startswith('__init__')
])
def test_import_module(file_path):
    # Generate the import module as library.module.file from src dir
    module_name = file_path[file_path.index(library_name):]
    # Remove final .py
    module_name = module_name[:-3]
    # Replace os path separator with .
    module_name = module_name.replace(os.path.sep, ".")

    # TEST to import the module
    print("Testing import of: " + module_name)
    module = importlib.import_module(module_name)
