# Developer Guide

This guide is for contributors to wetwire-gitlab-python.

## Development Setup

### Prerequisites

- Python 3.11 or later
- uv (recommended) or pip

### Clone and Install

```bash
git clone https://github.com/lex00/wetwire-gitlab-python.git
cd wetwire-gitlab-python

# Install with dev dependencies
uv sync --group dev

# Or with pip
pip install -e ".[dev]"
```

### Verify Installation

```bash
# Run tests
uv run pytest

# Run linter
uv run ruff check src tests

# Run type checker
uv run ty check src
```

## Project Structure

```
wetwire-gitlab-python/
├── src/wetwire_gitlab/     # Main package
├── tests/                   # Test files
├── examples/                # Example projects
├── docs/                    # Documentation
├── pyproject.toml          # Project configuration
├── CHANGELOG.md            # Version history
├── CLAUDE.md               # AI assistant guidelines
└── README.md               # Project overview
```

## Development Workflow

### 1. Create a Branch

```bash
git checkout -b feat/my-feature
# or
git checkout -b fix/my-bugfix
```

### 2. Make Changes

Follow these guidelines:

- Use type hints for all function parameters and returns
- Add docstrings for public functions and classes
- Keep functions focused and small
- Write tests for new functionality

### 3. Run Tests

```bash
# Run all tests
uv run pytest

# Run specific tests
uv run pytest tests/test_pipeline.py

# Run with coverage
uv run pytest --cov=src
```

### 4. Run Linters

```bash
# Check style
uv run ruff check src tests

# Auto-fix issues
uv run ruff check --fix src tests

# Type check
uv run ty check src
```

### 5. Commit Changes

Follow conventional commits:

```bash
git commit -m "feat: add new feature"
git commit -m "fix: resolve bug in X"
git commit -m "docs: update documentation"
git commit -m "test: add tests for Y"
```

### 6. Create Pull Request

Push and create a PR:

```bash
git push -u origin feat/my-feature
gh pr create
```

## Testing

### Test Structure

```
tests/
├── test_pipeline.py        # Pipeline type tests
├── test_discover.py        # Discovery tests
├── test_serialize.py       # Serialization tests
├── test_linter.py          # Lint rule tests
├── test_importer.py        # Import tests
├── test_examples.py        # Example project tests
└── ...
```

### Writing Tests

```python
class TestMyFeature:
    """Tests for my feature."""

    def test_basic_functionality(self):
        """Feature does X correctly."""
        result = my_function()
        assert result == expected

    def test_edge_case(self):
        """Feature handles edge case Y."""
        with pytest.raises(ValueError):
            my_function(invalid_input)
```

### Test Fixtures

```python
import pytest

@pytest.fixture
def sample_job():
    """Create a sample job for testing."""
    return Job(name="test", stage="test", script=["echo test"])

def test_with_fixture(sample_job):
    assert sample_job.name == "test"
```

## Code Style

### Python Style

- Follow PEP 8
- Use ruff for formatting and linting
- Maximum line length: 88 characters (ruff default)

### Type Hints

```python
def process_job(job: Job, options: dict[str, Any] | None = None) -> str:
    """Process a job and return YAML.

    Args:
        job: The job to process.
        options: Optional processing options.

    Returns:
        YAML string representation.
    """
    ...
```

### Docstrings

Use Google-style docstrings:

```python
def my_function(param1: str, param2: int) -> bool:
    """Short description.

    Longer description if needed, explaining the function's
    purpose and behavior.

    Args:
        param1: Description of param1.
        param2: Description of param2.

    Returns:
        Description of return value.

    Raises:
        ValueError: When param2 is negative.
    """
    ...
```

## Adding Features

### New Pipeline Type

1. Create dataclass in `src/wetwire_gitlab/pipeline/`
2. Add to `pipeline/__init__.py` exports
3. Update serialization if needed
4. Add tests
5. Update documentation

### New CLI Command

1. Add handler in `src/wetwire_gitlab/cli/main.py`
2. Register subparser with arguments
3. Implement command logic
4. Add tests in `tests/test_cli.py`
5. Document in `docs/CLI.md`

### New Lint Rule

1. Add rule class in `src/wetwire_gitlab/linter/rules.py`
2. Register in `linter/linter.py`
3. Add tests in `tests/test_linter.py`
4. Document in `docs/LINT_RULES.md`

## Release Process

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Create PR for release
4. After merge, tag release:

```bash
git tag v0.2.0
git push --tags
```

## Getting Help

- Check existing issues on GitHub
- Read the documentation
- Ask in pull request comments
