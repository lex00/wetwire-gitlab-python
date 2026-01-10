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
from wetwire_gitlab.pipeline import *

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
from wetwire_gitlab.pipeline import *

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
from wetwire_gitlab.pipeline import *

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
from wetwire_gitlab.pipeline import *

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
from wetwire_gitlab.intrinsics import *

Rule(if_=f"{CI.COMMIT_BRANCH} == {CI.DEFAULT_BRANCH}")
```

### 2. Use Predefined Rules

Replace common patterns with predefined rules:

```python
# Before
rules=[Rule(if_="$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH")]

# After
from wetwire_gitlab.intrinsics import *

rules=[Rules.ON_DEFAULT_BRANCH]
```

### 3. Extract Common Configuration

Create shared variables for reusable config:

```python
# cache.py
from wetwire_gitlab.pipeline import *

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

## Testing Methodology

### Import Testing

The import functionality is tested against a comprehensive corpus of GitLab CI templates located in `tests/fixtures/templates/`. These templates cover a wide range of GitLab CI features and patterns.

### Test Coverage

The test corpus includes templates for:

**Basic Patterns (01-07)**
- Single job pipelines
- Multi-stage pipelines
- Variables and environment configuration
- Artifacts and caching

**Advanced Features (08-20)**
- Docker images and services
- Include statements (local, template, remote)
- Environment deployments
- Parallel and matrix jobs
- Job tags and runner configuration
- Retry and timeout settings
- Coverage reports
- Before/after scripts
- Trigger jobs and child pipelines

**Real-World Projects (21+)**
- Python projects with testing and deployment
- Node.js projects with build pipelines
- Docker-based build and release workflows
- Complex DAG dependencies

### Round-Trip Testing

Every template undergoes round-trip testing:

1. **Parse**: YAML → Internal Representation (IR)
2. **Generate**: IR → Python code (validated for syntax)
3. **Convert**: IR → Typed objects (Job, Pipeline, etc.)
4. **Serialize**: Typed objects → YAML
5. **Compare**: Original YAML ≈ Generated YAML (semantic equivalence)

The semantic comparison verifies that:
- All configuration keys are preserved
- Values are equivalent (ignoring formatting)
- List orders are maintained
- Nested structures are correct

### Success Rate Metrics

The test suite tracks and reports:

- **Import success rate**: Percentage of templates that parse successfully (target: ≥95%)
- **Code generation success rate**: Percentage that generate valid Python (target: ≥95%)
- **Round-trip success rate**: Percentage with semantic equivalence (target: ≥90%)
- **Feature coverage**: Which GitLab CI features are tested (target: ≥80% of essential features)

### Running the Test Suite

```bash
# Run the full template corpus tests
uv run pytest tests/integration/test_template_corpus.py -v

# Run with coverage reports
uv run pytest tests/integration/test_template_corpus.py -v -s

# Run specific test categories
uv run pytest tests/integration/test_template_corpus.py::TestFeatureCoverage -v
uv run pytest tests/integration/test_template_corpus.py::TestSuccessRate -v
```

The `-s` flag displays detailed reports including:
- Feature coverage breakdown
- Success rate statistics
- Any failures with diffs

### Contributing Templates

When adding new GitLab CI features to the importer:

1. Add a representative template to `tests/fixtures/templates/`
2. Follow the naming convention: `NN_feature_name.yml`
3. Ensure the template tests a single feature clearly
4. Run the test suite to verify round-trip equivalence
5. Update feature coverage expectations if adding essential features

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
