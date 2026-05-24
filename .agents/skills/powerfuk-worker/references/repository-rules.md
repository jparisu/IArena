# Repository Rules

Apply these repository-specific priorities when using `powerfuk-worker`.

## Priority Order

1. Pythonic: optimize for readability, maintainability, reusability, and consistency.
2. Code: prefer correct behavior over stylistic cleanup.
3. Test: add or update tests for behavior changes.
4. Documentation: keep user-facing and developer-facing documentation aligned with the code.
5. Format: apply formatting and lint cleanup after correctness is in place.
6. Size and complexity checks: keep files and logic readable and simple.

## Rule Classification

### Design and Architecture

- Prefer reusable, scalable structures over one-off fixes.
- Reuse existing modules and patterns before introducing new abstractions.
- Keep interfaces explicit and easy to test.

### Code

- Use `PascalCase` for classes.
- Use `snake_case` for functions and variables.
- Use `UPPER_SNAKE_CASE` for constants.
- Add typing annotations to function signatures.
- Write complete docstrings.

### Tests

- Add or update tests for every behavior change.
- Mirror `src/` structure under `tests/`.
- Cover happy path, corner cases, and failure cases.
- Use `tests/manual/` only for checks that require human interaction.

### Documentation

- Update `README.md`, `docs/`, or other user-facing docs when behavior or usage changes.
- Keep developer-facing documentation aligned with implementation decisions.
- Add user-facing changes to `CHANGELOG.md` when relevant.

### Format and Validation

- Run formatting, linting, and tests after correctness work is in place.
- Prefer repository commands when available: `make format`, `make lint`, `make test`, `make docs`.
- Check line length, file size, and complexity constraints before finishing.
