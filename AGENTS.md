# AGENTS.md

Purpose: define minimal rules for AI agents working in this repository.

Keep behavior predictable, safe, and consistent with existing code.

---

## Priorities

Follow these in order:

1. Correctness and safety
2. Follow existing repository patterns
3. Complete the requested task
4. Tests
5. Documentation

---

## Repository baseline principles

Agents must preserve the overall design of the repository.

Guidelines:

* Prefer small, readable functions.
* Prefer explicit behavior over hidden side effects.
* Reuse existing utilities and abstractions.
* Keep documentation in files, classes and functions.
* Keep tests aligned with the structure of the source code.
* Abstract classes, protocols, interface and imports/exports do not require tests.

When unsure, follow the patterns already present in the codebase.

---

## Repository design decisions

* Files
    * Every class has its own file, named after the class.
    * Every file has a docstring describing its purpose and use.
* Classes
    * Every class has a docstring describing its purpose and use.
    * Every class has a clear public API in `docs`
* Functions
    * Every method has a docstring describing its purpose, arguments and return type.
    * Every method will be typed with type hints.
    * Types must be set in signature without quotes, using TYPE_CHECKING if necessary.
* Tests
    * Every test file is located in `tests` and follows the same directory structure as the source code.
    * Every method will have one or several unittests describing its expected behavior.
    * Abstract methods or visualization methods do not require tests.
    * No need for tests for __init__ files.
* Documentation
    * Every file, class and method has a docstring describing its purpose and use.
    * Every class and method is documented in `docs` with API docs.
    * README and documentation files are updated when relevant.

---


## Tasks

The user may specify a task to guide the agent.
If no task is provided, infer it from the request.

### task:generic

Generic default task that may include any combination of the rest of the tasks.

### task:design

Used for architecture and structural changes.

* Analyze the current structure first.
* Propose or implement improvements to modules, boundaries, or abstractions.
* Avoid unnecessary churn outside the design scope.

### task:develop

Used for implementing functionality.

* Implement the requested behavior.
* Edit the necessary files.
* Reuse existing patterns and utilities.

### task:docs

Used for documentation work.

* Add or improve docstrings.
* Update README or documentation files when relevant.
* Avoid modifying functional code unless necessary.

### task:test

Used for creating or improving tests.

* Add focused tests for the requested behavior.
* Mirror the structure of the source code when possible.
* Prefer deterministic tests.

### task:check

Used for validation and repository health.

* Run tests `pytest -q`
* Run linters `pre-commit run`
* Fix failures or lint issues.
* Do not introduce new features.

### task:query

Used for answering questions about the repository.

* Prefer explanation over code changes.
* Reference relevant files, classes, or modules.
* Default to read-only unless edits are explicitly requested.
