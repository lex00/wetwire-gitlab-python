# Quick Start

This guide will help you get started with wetwire-gitlab in minutes.

## Installation

```bash
pip install wetwire-gitlab
# or with uv
uv add wetwire-gitlab
```

## Create Your First Pipeline

### 1. Initialize a Project

Create a new directory with the following structure:

```
my-project/
├── ci/
│   ├── __init__.py
│   ├── jobs.py
│   └── pipeline.py
└── pyproject.toml
```

### 2. Configure pyproject.toml

```toml
[project]
name = "my-project"
version = "0.1.0"

[tool.wetwire-gitlab]
package = "ci"
```

### 3. Define Your Pipeline

**ci/pipeline.py:**

```python
from wetwire_gitlab.pipeline import Pipeline

pipeline = Pipeline(stages=["test", "deploy"])
```

**ci/jobs.py:**

```python
from wetwire_gitlab.intrinsics import CI, Rules, When
from wetwire_gitlab.pipeline import Job, Rule

test = Job(
    name="test",
    stage="test",
    image="python:3.11",
    script=[
        "pip install -e .[dev]",
        "pytest",
    ],
)

deploy = Job(
    name="deploy",
    stage="deploy",
    image="python:3.11",
    script=[
        "echo 'Deploying...'",
    ],
    rules=[
        Rule(if_=f"{CI.COMMIT_BRANCH} == {CI.DEFAULT_BRANCH}", when=When.MANUAL),
    ],
)
```

**ci/__init__.py:**

```python
from .jobs import deploy, test
from .pipeline import pipeline

__all__ = ["deploy", "pipeline", "test"]
```

### 4. Generate .gitlab-ci.yml

```bash
wetwire-gitlab build
```

This generates:

```yaml
stages:
  - test
  - deploy

test:
  stage: test
  image: python:3.11
  script:
    - pip install -e .[dev]
    - pytest

deploy:
  stage: deploy
  image: python:3.11
  script:
    - echo 'Deploying...'
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
      when: manual
```

## Common Commands

```bash
# Generate .gitlab-ci.yml
wetwire-gitlab build

# Validate the pipeline
wetwire-gitlab validate

# List discovered jobs
wetwire-gitlab list

# Lint your pipeline code
wetwire-gitlab lint

# Import existing .gitlab-ci.yml
wetwire-gitlab import .gitlab-ci.yml
```

## Next Steps

- See [Examples](../examples/) for complete pipeline examples
- Read [CLI Reference](CLI.md) for all commands
- Check [Lint Rules](LINT_RULES.md) for code quality guidelines
