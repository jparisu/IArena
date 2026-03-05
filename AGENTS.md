# Agent Instructions

All AI assistants working in this repository must follow:

1. `AGENTS.md`
2. `CONTRIBUTING.md`

## Mandatory behavior

- Apply these standards as hard requirements, not suggestions.
- Every Python file must include a module-level docstring.
- Every class must include a docstring.
- Every function/method must include a docstring with:
  - description
  - arguments
  - return value
- All function/method arguments and return values must be strongly typed.
- Add/update unit tests for every new class and every new method/function.
- Follow `tests/` structure to mirror `src/` structure.
- Reuse existing code when possible. If shared behavior is needed, create generic classes in `src/iarena/utilizing` and reuse them across modules.
- Update `docs/` for any user-facing behavior or API change.
- Run required validations before finishing work:
  - `pre-commit run --all-files`
  - `pytest -q`
  - If some checks fail, report them but do not take extreme actions like reverting or blocking changes.


## Conflict resolution

If instructions conflict, use this order:

1. Direct maintainer/user request for the current task.
2. `AGENTS.md`
3. `CONTRIBUTING.md`

If a rule cannot be satisfied, state it explicitly and explain the constraint in the final response.
