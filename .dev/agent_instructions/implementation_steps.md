# Steps

| Package                               | 1 | 2 | 3 | 4 | 5 |
|---------------------------------------|---|---|---|---|---|
| iarena.utilizing                      | X | . | . | . | . |
| iarena.utilizing.mapping              | X | X | X | X |   |
| iarena.utilizing.structuring          | X | X | X | X |   |
| iarena.utilizing.protocoling          | X | X | . | . | . |
| iarena.utilizing.timing               | X | X | X | X |   |
| iarena.utilizing.randoming            | X | X | X | X |   |
| iarena.gaming                         | X | X | . | . | . |
| iarena.gaming.hanoi                   | X | X | X | X |   |
| iarena.playing                        | X | X | . | - |   |
| iarena.scoring                        | X | X | X | - |   |
| iarena.arening                        | X | X | X | X |   |
| iarena.visualizing                    | X | X | . | . | . |
| iarena.visualizing.terminal_frontend  | X | X | . | X |   |
| iarena.visualizing.streamlit_frontend | X | X | . | X |   |
| iarena.grading                        | X | X | X | X |   |
| iarena.apps                           |   | . | . | . | . |
| iarena.apps.terminal                  |   |   |   |   |   |
| iarena.apps.streamlit                 |   |   |   |   |   |

---

# 1

Design: [skeleton.py](.dev/design/skeleton.py)
Goal: initialize package `iarena.grading`

1. Create every folder and subfolder for the package.
2. Create each file. One file per class. A file that only has a class must be called equal to the class name.
3. Each file must have a docstring commented its use.
4. Create each class (no implementation neither methods). Avoid non implementation comments.
5. Widely comment each class with its purpose and use.
6. Write down every __init__ file required.

---

# 2

Design: [skeleton.py](.dev/design/skeleton.py)
Goal: skeleton package `iarena.playing`

1. In each file, create the methods with their docstrings, but without implementation.
    a. Create each non abstract method with `raise NotImplementedError`.
2. Widely comment each method with arguments and return types.
3. Types must be set in signature without quotes, using TYPE_CHECKING if necessary.
4. Add API docs for each class and each method.

---

# 3

Design: [skeleton.py](.dev/design/skeleton.py)
Goal: test package `iarena.grading`

1. Create the test files inside `tests`. Follow same directory structure as in `src`. One test file per file in the package.
    a. Abstract classes or methods do not require tests.
    b. Visualization or interface elements do not require tests.
    c. No need for tests for __init__ files.
2. In each test file, create unittests for every method in the corresponding file.
3. Implement the test with the expected behavior of the method.

Note: tests will fail after this step, this is fine.

---

# 4

Design: [skeleton.py](.dev/design/skeleton.py)
Goal: implement package `iarena.scoring`

1. Implement each method inside the package.
    a. If you need to create a new protected methods, create them with a docstring and starting with an underscore.
    b. If you need to create a new public method or class, ask first.
    c. If you require to modify the design, ask first.
2. Every public method or design modification must be asked, and documented in [skeleton.py](.dev/design/skeleton.py). It also requires to add the corresponding test in the test file.

---

# 5

Design: [skeleton.py](.dev/design/skeleton.py)
Goal: check package `iarena.utilizing.structuring`

1. Run `pytest -q` to check that all tests pass.
2. Run `pre-commit run` to check that all pre-commit hooks pass.

---
