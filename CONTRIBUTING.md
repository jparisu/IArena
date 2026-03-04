# Contributing to iarena

Thank you for your interest in contributing to `iarena`! This document provides guidelines and instructions for contributing to this project.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally
   ```bash
   git clone https://github.com/YOUR_USERNAME/iarena.git
   cd iarena
   ```
3. Create a new branch for your contribution
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Setup

### Prerequisites

- Python 3.12 or higher
- pip

### Installation

1. Install the package in development mode with all dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

2. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```

## Development Workflow

### Code Style

We use several tools to maintain code quality:

- **ruff**: For linting and formatting
- **mypy**: For type checking
- **pytest**: For testing

Run these checks before committing:

```bash
# Format code
ruff format src/ tests/

# Lint code
ruff check src/ tests/

# Type check
mypy src/iarena

# Run tests
pytest tests/
```

### Testing

All contributions should include tests:

1. Write tests in the `tests/` directory
2. Follow existing test patterns
3. Ensure all tests pass:
   ```bash
   pytest tests/ -v
   ```
4. Check test coverage:
   ```bash
   pytest tests/ --cov=iarena --cov-report=term
   ```

### Documentation

Update documentation when adding or changing features:

1. Add/update docstrings in code (Google style)
2. Update relevant documentation files in `docs/`
3. Build documentation locally:
   ```bash
   mkdocs serve
   ```
4. View at http://127.0.0.1:8000/

## Pull Request Process

1. Update CHANGELOG.md with your changes
2. Ensure all tests pass
3. Ensure code meets style guidelines
4. Update documentation as needed
5. Submit a pull request with:
   - Clear description of changes
   - Reference to related issues
   - Screenshots for UI changes (if applicable)

### Pull Request Checklist

- [ ] Code follows style guidelines
- [ ] Tests added/updated and passing
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Pre-commit hooks pass
- [ ] All CI checks pass

## Code Review Process

- Maintainers will review your PR
- Address any requested changes
- Once approved, maintainers will merge your PR

## Reporting Bugs

Create an issue on GitHub with:

- Clear, descriptive title
- Steps to reproduce
- Expected vs actual behavior
- Python version and OS
- Relevant code snippets or error messages

## Suggesting Enhancements

Create an issue with:

- Clear description of the enhancement
- Use cases and benefits
- Possible implementation approach

## Code of Conduct

### Our Standards

- Be respectful and inclusive
- Welcome diverse perspectives
- Accept constructive criticism
- Focus on what's best for the community
- Show empathy towards others

### Unacceptable Behavior

- Harassment or discriminatory language
- Trolling or insulting comments
- Personal or political attacks
- Publishing others' private information
- Other conduct inappropriate in a professional setting

## Questions?

Feel free to open an issue for questions or reach out to the maintainers.

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (see LICENSE file).

## Attribution

This Contributing Guide is adapted from open source best practices.
