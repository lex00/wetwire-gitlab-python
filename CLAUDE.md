# wetwire-gitlab (Python)

Part of the [wetwire](https://github.com/lex00/wetwire) ecosystem.

Generate GitLab CI/CD configuration from typed Python declarations.

## Syntax Principles

All configurations use typed Python dataclasses. No raw dictionaries, no string templates.

### Jobs

```python
from wetwire_gitlab.pipeline import Job, Artifacts
from wetwire_gitlab.intrinsics import Rules

build = Job(
    name="build",
    stage="build",
    script=["make build"],
    artifacts=Artifacts(paths=["build/"]),
)
```

### Pipelines

```python
from wetwire_gitlab.pipeline import Pipeline

pipeline = Pipeline(stages=["build", "test", "deploy"])
```

### CI Variables

Use typed variable namespaces instead of raw strings:

```python
from wetwire_gitlab.intrinsics import CI, GitLab, MR

# CI variables
CI.COMMIT_SHA          # $CI_COMMIT_SHA
CI.DEFAULT_BRANCH      # $CI_DEFAULT_BRANCH

# User context
GitLab.USER_LOGIN      # $GITLAB_USER_LOGIN

# Merge request context
MR.SOURCE_BRANCH       # $CI_MERGE_REQUEST_SOURCE_BRANCH_NAME
```

### Pre-defined Rules

Use typed rule constants:

```python
from wetwire_gitlab.intrinsics import Rules

deploy = Job(
    name="deploy",
    rules=[Rules.ON_DEFAULT_BRANCH],  # Not raw if expressions
)
```

### Job Dependencies

Use direct Job references instead of strings for type-safe dependencies:

```python
from wetwire_gitlab.pipeline import Job

build = Job(name="build", stage="build", script=["make build"])

# Direct Job reference (preferred - type-safe)
test = Job(
    name="test",
    stage="test",
    script=["make test"],
    needs=[build],  # Direct reference to Job instance
)

# String reference (still supported for backwards compatibility)
deploy = Job(
    name="deploy",
    stage="deploy",
    script=["make deploy"],
    needs=["test"],  # String reference
)
```

## Package Structure

```
wetwire_gitlab/
├── pipeline/           # Core types: Job, Pipeline, Rule, Artifacts, Cache
├── intrinsics/         # CI, GitLab, MR variables; When, Rules constants
├── linter/             # 19 lint rules (WGL001-WGL019)
├── importer/           # YAML to Python conversion
├── discover/           # AST-based discovery
├── template/           # Dependency ordering
├── serialize/          # Python to YAML conversion
└── validation/         # glab integration
```

## Lint Rules (WGL001-WGL019)

- **WGL001**: Use typed component wrappers
- **WGL002**: Use Rule dataclass instead of raw dict
- **WGL003**: Use predefined variables from intrinsics
- **WGL004**: Use Cache dataclass instead of raw dict
- **WGL005**: Use Artifacts dataclass instead of raw dict
- **WGL006**: Use typed stage constants
- **WGL007**: Duplicate job names
- **WGL008**: File contains too many jobs
- **WGL009**: Use predefined Rules constants
- **WGL010**: Use typed When constants
- **WGL011**: Missing stage in Job
- **WGL012**: Use CachePolicy constants
- **WGL013**: Use ArtifactsWhen constants
- **WGL014**: Missing script in Job
- **WGL015**: Missing name in Job
- **WGL016**: Use Image dataclass
- **WGL017**: Empty rules list
- **WGL018**: Needs without stage
- **WGL019**: Manual without allow_failure

## Key Principles

1. **Typed dataclasses** — Use Job, Pipeline, Rule, Artifacts classes
2. **Intrinsics package** — Use CI.*, GitLab.*, MR.* for variables
3. **Pre-defined rules** — Use Rules.ON_DEFAULT_BRANCH etc.
4. **Flat declarations** — Extract complex configs to named variables
5. **Direct references** — Use Job references in needs/dependencies for type safety

## Build

```bash
wetwire-gitlab build
# Outputs .gitlab-ci.yml
```

## Project Structure

```
my-project/
├── ci/
│   ├── __init__.py
│   ├── pipeline.py     # Pipeline definition
│   ├── jobs.py         # Job definitions
│   └── stages.py       # Stage constants
└── .gitlab-ci.yml      # Generated YAML output
```
