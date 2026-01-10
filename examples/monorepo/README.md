# Monorepo Example

A monorepo pipeline with dynamic child pipelines and change detection.

## Structure

```
monorepo/
├── ci/
│   ├── __init__.py
│   ├── jobs.py      # Job definitions
│   └── pipeline.py  # Pipeline configuration
├── pyproject.toml
└── README.md
```

## Pipeline Stages

1. **detect** - Detect changes in each package
2. **trigger** - Trigger child pipelines for changed packages

## Features

- Change detection using git diff
- Dynamic child pipeline generation
- Package-specific CI/CD
- Parallel package builds

## Usage

```bash
# Generate .gitlab-ci.yml
wetwire-gitlab build

# Validate the generated pipeline
wetwire-gitlab validate
```

## Monorepo Structure

```
packages/
├── frontend/
│   └── .gitlab-ci.yml  # Child pipeline
├── backend/
│   └── .gitlab-ci.yml  # Child pipeline
└── shared/
    └── .gitlab-ci.yml  # Child pipeline
```
