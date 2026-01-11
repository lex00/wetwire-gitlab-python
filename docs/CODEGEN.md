# Code Generation

This document describes how wetwire-gitlab-python generates `.gitlab-ci.yml` from Python code.

## Overview

wetwire-gitlab transforms Python dataclass declarations into GitLab CI/CD configuration. The process follows a six-stage pipeline:

```
┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌───────────┐  ┌──────────┐
│ DISCOVER │→│ VALIDATE │→│ EXTRACT  │→│  ORDER   │→│ SERIALIZE │→│   EMIT   │
└──────────┘  └──────────┘  └──────────┘  └──────────┘  └───────────┘  └──────────┘
```

## Pipeline Stages

### 1. DISCOVER

**Purpose**: Find Job and Pipeline declarations in Python source files without executing code.

**Implementation**: `discover/scanner.py`

The discovery stage uses Python's `ast` module to statically analyze source files:

```python
# Source being analyzed
build = Job(
    name="build",
    stage="build",
    script=["make build"],
)
```

The scanner walks the AST looking for:
- Variable assignments where the value is a `Job()` or `Pipeline()` call
- Extracts the variable name and call arguments
- Records file path and line numbers for error reporting

**Output**: List of `DiscoveredJob` records containing:
- Job name (from `name=` argument)
- Variable name (Python identifier)
- File path and line number
- Dependencies (from `needs=` argument)

### 2. VALIDATE

**Purpose**: Check that the discovered configuration is valid before execution.

**Implementation**: `linter/` package

Validation includes:
- **Reference checking**: All job names in `needs` must exist
- **Cycle detection**: No circular dependencies (WGL024)
- **Uniqueness**: Job names must be unique across files
- **Secret detection**: No hardcoded credentials (WGL025)
- **Type checking**: Proper use of typed constants

Validation runs 25 lint rules (WGL001-WGL025) that check for:
- Use of typed dataclasses vs raw dictionaries
- Use of predefined constants (Rules, When, Images, Services)
- Proper job configuration (stage, script, image)
- Security issues (secrets, passwords)

### 3. EXTRACT

**Purpose**: Execute Python code to obtain runtime Job and Pipeline instances.

**Implementation**: `runner/loader.py`

The extraction stage:
1. Imports the Python module dynamically
2. Finds all module-level objects
3. Filters for `Job` and `Pipeline` instances
4. Collects their fully-resolved values

This stage is necessary because:
- Variables may be computed dynamically
- String interpolation happens at runtime
- Conditional logic may affect values

```python
# Example: Runtime value computation
ENVIRONMENTS = ["dev", "staging", "prod"]
deploy_jobs = [
    Job(name=f"deploy-{env}", stage="deploy", ...)
    for env in ENVIRONMENTS
]
```

### 4. ORDER

**Purpose**: Sort jobs by dependencies using topological order.

**Implementation**: `template/ordering.py`

Uses Kahn's algorithm for topological sorting:

1. Build directed graph from job dependencies:
   ```
   build → test → deploy
          ↘ lint ↗
   ```

2. Calculate in-degrees (number of incoming edges)

3. Process nodes with zero in-degree first

4. Detect cycles if not all nodes are visited

**Output**: Ordered list of jobs respecting dependencies.

### 5. SERIALIZE

**Purpose**: Convert Python dataclass instances to YAML-compatible dictionaries.

**Implementation**: `serialize/converter.py`, `serialize/yaml_builder.py`

Serialization handles:

1. **Field name transformation**:
   - `snake_case` → `kebab-case` (Python convention to YAML convention)
   - `before_script` → `before_script` (some fields keep underscores)

2. **Type conversion**:
   - Dataclasses → dictionaries
   - Enums → string values
   - Lists → YAML arrays

3. **Special handling**:
   - `Job` references in `needs` → job name strings
   - Intrinsic variables → `$CI_*` strings
   - `None` values → omitted from output

4. **Rule transformation**:
   ```python
   Rule(if_="$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH")
   # becomes
   {"if": "$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH"}
   ```

### 6. EMIT

**Purpose**: Generate final YAML output.

**Implementation**: `cli/commands/build.py`

The emit stage:
1. Assembles the full pipeline structure
2. Adds `stages:` declaration
3. Adds global configuration (`default:`, `variables:`, etc.)
4. Writes YAML using `yaml.dump()` with specific formatting options
5. Optionally generates build manifest (with `--manifest` flag)

## Discovery Process Details

### AST Visitor Pattern

```python
class JobVisitor(ast.NodeVisitor):
    """Visit AST nodes to find Job declarations."""

    def visit_Assign(self, node: ast.Assign) -> None:
        """Handle: job_name = Job(...)"""
        if isinstance(node.value, ast.Call):
            func = node.value.func
            if isinstance(func, ast.Name) and func.id == "Job":
                self._extract_job(node)

    def _extract_job(self, node: ast.Assign) -> None:
        # Extract name from Job(name="...") keyword
        # Extract needs from Job(needs=[...]) keyword
        # Record file and line information
```

### Handling Different Import Styles

The scanner handles multiple import patterns:

```python
# Direct import
from wetwire_gitlab.pipeline import Job

# Wildcard import
from wetwire_gitlab.pipeline import *

# Aliased import
from wetwire_gitlab.pipeline import Job as GitLabJob
```

## Serialization Rules

### Job Serialization

| Python Field | YAML Key | Notes |
|-------------|----------|-------|
| `name` | (key) | Used as job key, not in body |
| `stage` | `stage` | |
| `script` | `script` | |
| `before_script` | `before_script` | |
| `after_script` | `after_script` | |
| `image` | `image` | Supports string or Image dataclass |
| `variables` | `variables` | Dict[str, str] |
| `rules` | `rules` | List of Rule dataclasses |
| `needs` | `needs` | Job refs → job names |
| `artifacts` | `artifacts` | Artifacts dataclass → dict |
| `cache` | `cache` | Cache dataclass → dict |
| `services` | `services` | List of Service dataclasses |
| `environment` | `environment` | String or dict |

### Intrinsic Variable Serialization

```python
CI.COMMIT_SHA          # → "$CI_COMMIT_SHA"
CI.DEFAULT_BRANCH      # → "$CI_DEFAULT_BRANCH"
GitLab.USER_LOGIN      # → "$GITLAB_USER_LOGIN"
MR.SOURCE_BRANCH       # → "$CI_MERGE_REQUEST_SOURCE_BRANCH_NAME"
```

### Rule Serialization

```python
Rule(if_="$CI_COMMIT_TAG")
# → {"if": "$CI_COMMIT_TAG"}

Rules.ON_DEFAULT_BRANCH
# → {"if": "$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH"}

Rules.ON_MERGE_REQUEST
# → {"if": "$CI_MERGE_REQUEST_IID"}
```

## Error Handling

### Discovery Errors

- File not found
- Syntax errors in Python files
- Invalid import statements

### Validation Errors

- Unknown job references
- Circular dependencies
- Duplicate job names
- Lint rule violations

### Extraction Errors

- Import failures
- Runtime exceptions in code
- Missing required fields

### Serialization Errors

- Unsupported types
- Invalid field values
- Circular references in data

## Performance Considerations

1. **AST-first approach**: Discovery uses static analysis to avoid executing user code until necessary

2. **Parallel file scanning**: Multiple files can be scanned concurrently

3. **Caching**: Discovery results can be cached based on file modification times

4. **Lazy loading**: Jobs are only fully extracted when needed

## Related Documentation

- [INTERNALS.md](INTERNALS.md) - Package structure and extension points
- [LINT_RULES.md](LINT_RULES.md) - Complete list of lint rules
- [CLI.md](CLI.md) - Command-line interface usage
