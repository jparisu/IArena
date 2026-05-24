
How to import modules from the src directory in scripts or notebooks without installing the package.

## Import in .py

``` python
#####################################################################################
# Add ../../src/ to the system path to import the necessary modules
import sys
import os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src'))
sys.path.insert(0, project_root)
#####################################################################################
```

## Import in notebook

``` python
import sys
from pathlib import Path

# path to the directory that contains your package
sys.path.append(str(Path("../../src")))
```
