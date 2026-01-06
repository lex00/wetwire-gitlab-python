# wetwire-gitlab

A Python library for generating GitLab CI/CD configuration from typed Python declarations.

## Installation

```bash
pip install wetwire-gitlab
```

## Quick Start

Define your pipeline using typed Python dataclasses:

```python
from wetwire_gitlab.pipeline import Job, Pipeline, Rule, Artifacts
from wetwire_gitlab.intrinsics import CI, When, Rules
from wetwire_gitlab.serialize import build_pipeline_yaml

# Define jobs
build = Job(
    name="build",
    stage="build",
    script=["make build"],
    artifacts=Artifacts(paths=["build/"]),
)

test = Job(
    name="test",
    stage="test",
    script=["pytest"],
    needs=["build"],
)

deploy = Job(
    name="deploy",
    stage="deploy",
    script=["make deploy"],
    rules=[Rule(if_=f"{CI.COMMIT_BRANCH} == {CI.DEFAULT_BRANCH}")],
    needs=["test"],
)

# Define pipeline
pipeline = Pipeline(stages=["build", "test", "deploy"])

# Generate YAML
yaml_output = build_pipeline_yaml(pipeline, [build, test, deploy])
print(yaml_output)
```

## Features

### Pipeline Types

Typed dataclasses for all GitLab CI/CD configuration:

- `Job` - Job configuration with script, rules, artifacts, cache, etc.
- `Pipeline` - Top-level pipeline with stages, workflow, includes
- `Rule` - Conditional execution rules
- `Artifacts` - Build artifact configuration
- `Cache` - Cache configuration with keys and policies
- `Include` - Include local, remote, template, or component files
- `Workflow` - Pipeline-level rules and name

### Intrinsics

Pre-defined CI/CD variables and constants:

```python
from wetwire_gitlab.intrinsics import CI, GitLab, MR, When, CachePolicy, Rules

# CI variables
CI.COMMIT_SHA          # $CI_COMMIT_SHA
CI.COMMIT_BRANCH       # $CI_COMMIT_BRANCH
CI.DEFAULT_BRANCH      # $CI_DEFAULT_BRANCH
CI.PIPELINE_SOURCE     # $CI_PIPELINE_SOURCE

# User context
GitLab.USER_LOGIN      # $GITLAB_USER_LOGIN
GitLab.USER_EMAIL      # $GITLAB_USER_EMAIL

# Merge request context
MR.SOURCE_BRANCH       # $CI_MERGE_REQUEST_SOURCE_BRANCH_NAME
MR.TARGET_BRANCH       # $CI_MERGE_REQUEST_TARGET_BRANCH_NAME

# Pre-defined rules
Rules.ON_DEFAULT_BRANCH
Rules.ON_TAG
Rules.ON_MERGE_REQUEST
Rules.MANUAL
```

### Serialization

Convert typed objects to YAML:

```python
from wetwire_gitlab.serialize import to_yaml, to_dict, build_pipeline_yaml

# Single object
yaml_str = to_yaml(job)

# Full pipeline with jobs
yaml_str = build_pipeline_yaml(pipeline, jobs)
```

### AST Discovery

Discover Job and Pipeline declarations in Python source files:

```python
from wetwire_gitlab.discover import discover_in_directory, discover_jobs

# Discover all jobs and pipelines in a directory
result = discover_in_directory(Path("src/"))
print(f"Found {len(result.jobs)} jobs and {len(result.pipelines)} pipelines")

# Discover jobs in a single file
jobs = discover_jobs(Path("ci/jobs.py"))
```

### Linting

Check pipeline definitions for common issues:

```python
from wetwire_gitlab.linter import lint_file, lint_directory

# Lint a single file
result = lint_file(Path("ci/jobs.py"))
for issue in result.issues:
    print(f"{issue.code}: {issue.message} at line {issue.line_number}")

# Lint a directory
result = lint_directory(Path("src/"))
```

Lint rules:
- `WGL001` - Use typed component wrappers
- `WGL002` - Use Rule dataclass instead of raw dict
- `WGL003` - Use predefined variables from intrinsics
- `WGL004` - Use Cache dataclass instead of raw dict
- `WGL005` - Use Artifacts dataclass instead of raw dict
- `WGL006` - Use typed stage constants
- `WGL007` - Duplicate job names
- `WGL008` - File contains too many jobs

### YAML Import

Parse existing `.gitlab-ci.yml` files:

```python
from wetwire_gitlab.importer import parse_gitlab_ci_file

pipeline = parse_gitlab_ci_file(Path(".gitlab-ci.yml"))
print(f"Stages: {pipeline.stages}")
for job in pipeline.jobs:
    print(f"Job: {job.name}, Stage: {job.stage}")
```

### Validation

Validate pipelines using the GitLab CLI:

```python
from wetwire_gitlab.validation import validate_pipeline, is_glab_installed

if is_glab_installed():
    result = validate_pipeline(yaml_content)
    if result.valid:
        print("Pipeline is valid!")
    else:
        for error in result.errors:
            print(f"Error: {error}")
```

### Template Building

Order jobs by dependencies for YAML generation:

```python
from wetwire_gitlab.template import order_jobs_for_yaml, detect_cycle

# Check for circular dependencies
has_cycle, cycle_nodes = detect_cycle(dependency_graph)

# Order jobs so dependencies come first
ordered_jobs = order_jobs_for_yaml(discovered_jobs)
```

## CLI

```bash
# Build pipeline YAML from Python definitions
wetwire-gitlab build

# Validate pipeline
wetwire-gitlab validate

# Lint pipeline definitions
wetwire-gitlab lint

# List discovered jobs and pipelines
wetwire-gitlab list

# Import existing .gitlab-ci.yml
wetwire-gitlab import .gitlab-ci.yml
```

## Development

```bash
# Install dev dependencies
uv sync --group dev

# Run tests
uv run pytest

# Run linter
uv run ruff check src tests

# Run type checker
uv run ty check src
```

## License

MIT
