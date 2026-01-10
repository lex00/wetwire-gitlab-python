# Import Workflow

This guide explains how to convert existing `.gitlab-ci.yml` files to wetwire-gitlab Python code.

## Overview

The import workflow converts your YAML configuration into typed Python dataclasses, enabling:

- Type safety and IDE autocomplete
- Linting and code quality checks
- Version control-friendly diffs
- Programmatic pipeline manipulation

## Basic Import

```bash
wetwire-gitlab import .gitlab-ci.yml
```

This creates a `ci/` directory with:

```
ci/
├── __init__.py    # Exports all jobs and pipeline
├── jobs.py        # Job definitions
└── pipeline.py    # Pipeline configuration
```

## Import Options

### Output Directory

```bash
# Import to custom directory
wetwire-gitlab import -o src/pipeline .gitlab-ci.yml
```

### Single File Mode

```bash
# Generate single file instead of directory
wetwire-gitlab import --single-file .gitlab-ci.yml
```

Creates `ci.py` with all definitions.

### Skip Scaffold

```bash
# Don't create __init__.py files
wetwire-gitlab import --no-scaffold .gitlab-ci.yml
```

## What Gets Imported

### Jobs

YAML jobs are converted to `Job` dataclass instances:

**YAML:**

```yaml
test:
  stage: test
  image: python:3.11
  script:
    - pytest
  artifacts:
    paths:
      - coverage.xml
```

**Python:**

```python
from wetwire_gitlab.pipeline import Artifacts, Job

test = Job(
    name="test",
    stage="test",
    image="python:3.11",
    script=["pytest"],
    artifacts=Artifacts(paths=["coverage.xml"]),
)
```

### Rules

Rule dictionaries become `Rule` dataclass instances:

**YAML:**

```yaml
deploy:
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
      when: manual
```

**Python:**

```python
from wetwire_gitlab.pipeline import Job, Rule

deploy = Job(
    name="deploy",
    rules=[
        Rule(if_="$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH", when="manual"),
    ],
)
```

### Includes

Include statements become `Include` dataclass instances:

**YAML:**

```yaml
include:
  - template: Jobs/Test.gitlab-ci.yml
  - local: .gitlab/ci/deploy.yml
```

**Python:**

```python
from wetwire_gitlab.pipeline import Include

includes = [
    Include(template="Jobs/Test.gitlab-ci.yml"),
    Include(local=".gitlab/ci/deploy.yml"),
]
```

### Variables

Pipeline variables are converted to dictionaries:

**YAML:**

```yaml
variables:
  NODE_VERSION: "18"
  CACHE_KEY: "$CI_COMMIT_REF_SLUG"
```

**Python:**

```python
from wetwire_gitlab.pipeline import Pipeline

pipeline = Pipeline(
    variables={
        "NODE_VERSION": "18",
        "CACHE_KEY": "$CI_COMMIT_REF_SLUG",
    },
)
```

## Post-Import Improvements

After importing, consider these enhancements:

### 1. Use Intrinsics

Replace string variables with typed references:

```python
# Before
Rule(if_="$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH")

# After
from wetwire_gitlab.intrinsics import CI

Rule(if_=f"{CI.COMMIT_BRANCH} == {CI.DEFAULT_BRANCH}")
```

### 2. Use Predefined Rules

Replace common patterns with predefined rules:

```python
# Before
rules=[Rule(if_="$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH")]

# After
from wetwire_gitlab.intrinsics import Rules

rules=[Rules.ON_DEFAULT_BRANCH]
```

### 3. Extract Common Configuration

Create shared variables for reusable config:

```python
# cache.py
from wetwire_gitlab.pipeline import Cache

npm_cache = Cache(
    key="${CI_COMMIT_REF_SLUG}",
    paths=["node_modules/"],
)

# jobs.py
from .cache import npm_cache

build = Job(name="build", cache=npm_cache, ...)
test = Job(name="test", cache=npm_cache, ...)
```

## Round-Trip Testing

Verify your import produces equivalent output:

```bash
# 1. Import the YAML
wetwire-gitlab import .gitlab-ci.yml -o ci/

# 2. Generate new YAML
wetwire-gitlab build -o .gitlab-ci.new.yml

# 3. Compare (should be semantically equivalent)
diff .gitlab-ci.yml .gitlab-ci.new.yml
```

## Troubleshooting

### Unsupported Features

Some advanced GitLab CI features may not be fully supported:

- `!reference` tags
- Complex `extends` hierarchies
- Anchors and aliases

These will be imported as raw dictionaries with comments.

### Large Files

For files with many jobs, consider:

1. Import with single file mode
2. Split into logical modules
3. Run linter to identify issues

```bash
wetwire-gitlab import --single-file .gitlab-ci.yml
wetwire-gitlab lint ci.py
```
