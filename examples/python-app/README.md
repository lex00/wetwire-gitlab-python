# Python Application Example

A basic Python CI/CD pipeline demonstrating test, lint, and deploy stages.

## Structure

```
python-app/
├── ci/
│   ├── __init__.py
│   ├── jobs.py      # Job definitions
│   └── pipeline.py  # Pipeline configuration
├── pyproject.toml
└── README.md
```

## Pipeline Stages

1. **test** - Run pytest with coverage
2. **lint** - Run ruff linter
3. **deploy** - Deploy to production (manual trigger)

## Usage

```bash
# Generate .gitlab-ci.yml
wetwire-gitlab build

# Validate the generated pipeline
wetwire-gitlab validate

# List discovered jobs
wetwire-gitlab list
```

## Generated Output

The pipeline generates jobs that:
- Run tests on Python 3.11, 3.12, 3.13
- Check code with ruff linter
- Deploy to production on manual approval (default branch only)
