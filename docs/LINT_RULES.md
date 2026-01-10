# Lint Rules

wetwire-gitlab includes 11 lint rules to help maintain pipeline code quality.

## Rule Summary

| Code | Name | Description |
|------|------|-------------|
| WGL001 | Use typed component wrappers | Use typed classes instead of raw dicts |
| WGL002 | Use Rule dataclass | Use Rule() instead of raw dict rules |
| WGL003 | Use predefined variables | Use CI.* instead of string variables |
| WGL004 | Use Cache dataclass | Use Cache() instead of raw dict cache |
| WGL005 | Use Artifacts dataclass | Use Artifacts() instead of raw dict artifacts |
| WGL006 | Use typed stage constants | Consider using stage constants |
| WGL007 | Duplicate job names | Multiple jobs have the same name |
| WGL008 | File too large | File contains too many jobs |
| WGL009 | Use predefined Rules | Use Rules.ON_DEFAULT_BRANCH etc. |
| WGL010 | Use typed When constants | Use When.MANUAL instead of strings |
| WGL011 | Missing stage | Jobs should have explicit stage |

## Detailed Rules

### WGL001: Use typed component wrappers

Use typed component classes instead of raw dictionaries for configuration.

**Bad:**

```python
job = Job(
    name="test",
    include={"template": "Jobs/Test.gitlab-ci.yml"},  # Raw dict
)
```

**Good:**

```python
from wetwire_gitlab.templates import Test

job = Job(
    name="test",
    include=Test().to_include(),
)
```

### WGL002: Use Rule dataclass

Use the `Rule` dataclass instead of raw dictionaries for job rules.

**Bad:**

```python
job = Job(
    name="deploy",
    rules=[{"if": "$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH"}],  # Raw dict
)
```

**Good:**

```python
from wetwire_gitlab.pipeline import Rule

job = Job(
    name="deploy",
    rules=[Rule(if_="$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH")],
)
```

### WGL003: Use predefined variables

Use typed variable references from intrinsics instead of string variables.

**Bad:**

```python
job = Job(
    name="deploy",
    rules=[Rule(if_="$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH")],
)
```

**Good:**

```python
from wetwire_gitlab.intrinsics import CI

job = Job(
    name="deploy",
    rules=[Rule(if_=f"{CI.COMMIT_BRANCH} == {CI.DEFAULT_BRANCH}")],
)
```

### WGL004: Use Cache dataclass

Use the `Cache` dataclass for cache configuration.

**Bad:**

```python
job = Job(
    name="build",
    cache={"key": "npm", "paths": ["node_modules/"]},  # Raw dict
)
```

**Good:**

```python
from wetwire_gitlab.pipeline import Cache

cache = Cache(key="npm", paths=["node_modules/"])
job = Job(
    name="build",
    cache=cache,
)
```

### WGL005: Use Artifacts dataclass

Use the `Artifacts` dataclass for artifact configuration.

**Bad:**

```python
job = Job(
    name="build",
    artifacts={"paths": ["dist/"]},  # Raw dict
)
```

**Good:**

```python
from wetwire_gitlab.pipeline import Artifacts

job = Job(
    name="build",
    artifacts=Artifacts(paths=["dist/"]),
)
```

### WGL006: Use typed stage constants

Consider defining stage constants for reusability and consistency.

**Suggestion:**

```python
# stages.py
BUILD = "build"
TEST = "test"
DEPLOY = "deploy"

# jobs.py
from .stages import BUILD, TEST

job = Job(name="compile", stage=BUILD)
```

### WGL007: Duplicate job names

Multiple jobs have the same name, which will cause conflicts.

**Bad:**

```python
# file1.py
test = Job(name="test", ...)

# file2.py
test = Job(name="test", ...)  # Duplicate!
```

**Good:**

```python
# file1.py
test_unit = Job(name="test-unit", ...)

# file2.py
test_integration = Job(name="test-integration", ...)
```

### WGL008: File too large

A file contains too many job definitions. Consider splitting into multiple files.

**Default threshold:** 20 jobs per file

**Suggestion:**

```
ci/
├── jobs/
│   ├── build.py      # Build-related jobs
│   ├── test.py       # Test jobs
│   └── deploy.py     # Deployment jobs
└── pipeline.py
```

### WGL009: Use predefined Rules constants

Use predefined rule constants for common patterns like default branch deployment.

**Bad:**

```python
job = Job(
    name="deploy",
    rules=[Rule(if_="$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH")],
)
```

**Good:**

```python
from wetwire_gitlab.intrinsics import Rules

job = Job(
    name="deploy",
    rules=[Rules.ON_DEFAULT_BRANCH],
)
```

Available predefined rules:
- `Rules.ON_DEFAULT_BRANCH` - Run on default branch only
- `Rules.ON_TAG` - Run on tags only
- `Rules.ON_MERGE_REQUEST` - Run on merge request pipelines

### WGL010: Use typed When constants

Use typed `When` constants instead of string literals for the `when` attribute.

**Bad:**

```python
job = Job(
    name="deploy",
    when="manual",  # String literal
)
```

**Good:**

```python
from wetwire_gitlab.intrinsics import When

job = Job(
    name="deploy",
    when=When.MANUAL,
)
```

Available constants:
- `When.MANUAL` - Manual trigger
- `When.ALWAYS` - Always run
- `When.NEVER` - Never run
- `When.ON_SUCCESS` - Run on success (default)
- `When.ON_FAILURE` - Run on failure
- `When.DELAYED` - Delayed execution

### WGL011: Missing stage

Jobs should have an explicit `stage` attribute for clarity and maintainability.

**Bad:**

```python
job = Job(
    name="build",
    script=["make build"],
    # No stage specified - relies on default
)
```

**Good:**

```python
job = Job(
    name="build",
    stage="build",
    script=["make build"],
)
```

## Running the Linter

```bash
# Lint current directory
wetwire-gitlab lint

# Lint specific path
wetwire-gitlab lint src/ci

# Run specific rules
wetwire-gitlab lint -r WGL001 -r WGL003

# Output as JSON
wetwire-gitlab lint --format json
```

## Auto-Fix

Some rules support automatic fixing. Use the `--fix` flag to apply fixes:

```bash
# Fix issues in current directory
wetwire-gitlab lint --fix

# Fix issues in specific file
wetwire-gitlab lint --fix src/ci/jobs.py
```

### Auto-Fixable Rules

| Code | Auto-fixable | Fix Description |
|------|--------------|-----------------|
| WGL001 | No | - |
| WGL002 | No | - |
| WGL003 | No | - |
| WGL004 | No | - |
| WGL005 | No | - |
| WGL006 | No | - |
| WGL007 | No | - |
| WGL008 | No | - |
| WGL009 | No | - |
| WGL010 | **Yes** | Converts `when="manual"` to `when=When.MANUAL` and adds import |
| WGL011 | No | - |

### Programmatic Auto-Fix

You can also use the auto-fix functions programmatically:

```python
from wetwire_gitlab.linter import fix_code, fix_file

# Fix code string
fixed_code = fix_code(source_code)

# Fix file (read-only)
fixed_code = fix_file("src/ci/jobs.py")

# Fix file and write changes
fix_file("src/ci/jobs.py", write=True)
```

## Disabling Rules

Rules can be disabled per-file using comments:

```python
# wetwire-gitlab: disable=WGL003
job = Job(
    name="legacy",
    rules=[Rule(if_="$CI_COMMIT_BRANCH")],  # Uses raw variable
)
```
