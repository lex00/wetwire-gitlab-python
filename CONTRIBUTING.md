# Contributing to wetwire-gitlab

Thank you for your interest in contributing to wetwire-gitlab!

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/lex00/wetwire-gitlab-python.git
   cd wetwire-gitlab-python
   ```

2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies (including dev tools):
   ```bash
   pip install -e ".[dev]"
   ```

4. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```

5. Run tests to verify setup:
   ```bash
   pytest
   ```

## Code Style

- Follow [PEP 8](https://peps.python.org/pep-0008/) conventions
- Use type hints for all function signatures
- Run linting before committing:
  ```bash
  ruff check src/ tests/
  ruff format src/ tests/
  ```
- Run type checking:
  ```bash
  pyright src/
  ```

### Key Principles

1. **Typed dataclasses** - Use `Job`, `Pipeline`, `Rule`, `Artifacts` classes
2. **Intrinsics package** - Use `CI.*`, `GitLab.*`, `MR.*` for variables
3. **Pre-defined rules** - Use `Rules.ON_DEFAULT_BRANCH` etc.
4. **Flat declarations** - Extract complex configs to named variables

See [CLAUDE.md](CLAUDE.md) for detailed syntax guidelines.

## Pull Request Process

1. Create a feature branch from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes following the code style guidelines

3. Add or update tests for your changes

4. Run the full test suite:
   ```bash
   pytest
   ```

5. Run linting and fix any issues:
   ```bash
   ruff check --fix src/ tests/
   ruff format src/ tests/
   ```

6. Commit with a descriptive message:
   ```bash
   git commit -m "feat: add new feature description"
   ```

7. Push and create a pull request:
   ```bash
   git push origin feature/your-feature-name
   ```

8. Fill out the PR template with:
   - Summary of changes
   - Test plan
   - Any breaking changes

## Commit Message Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation changes
- `test:` - Test additions or fixes
- `refactor:` - Code refactoring
- `chore:` - Maintenance tasks

## Running Specific Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/cli/test_main.py

# Run with coverage report
pytest --cov=wetwire_gitlab --cov-report=html

# Run excluding slow tests
pytest -m "not slow"
```

## Project Structure

```
src/wetwire_gitlab/
├── pipeline/      # Core types: Job, Pipeline, Rule, Artifacts, Cache
├── intrinsics/    # CI, GitLab, MR variables; When, Rules constants
├── linter/        # Lint rules (WGL001-WGL025)
├── importer/      # YAML to Python conversion
├── serialize/     # Python to YAML conversion
└── validation/    # glab integration
```

## Questions?

Open an issue for discussion or questions about contributing.
