# Multi-Stage Pipeline Example

A complex multi-stage pipeline demonstrating job dependencies and parallel execution.

## Structure

```
multi-stage/
├── ci/
│   ├── __init__.py
│   ├── jobs.py      # Job definitions
│   └── pipeline.py  # Pipeline configuration
├── pyproject.toml
└── README.md
```

## Pipeline Stages

1. **prepare** - Setup and install dependencies
2. **build** - Parallel builds (frontend, backend, docs)
3. **test** - Run tests (unit, integration, e2e)
4. **quality** - Code quality checks (lint, security scan)
5. **deploy** - Deploy to environments

## Features

- Parallel job execution within stages
- Job dependencies with `needs`
- Artifact passing between jobs
- Environment-based deployments

## Usage

```bash
# Generate .gitlab-ci.yml
wetwire-gitlab build

# View the job graph
wetwire-gitlab graph --format=mermaid
```
