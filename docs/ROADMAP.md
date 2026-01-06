# wetwire-gitlab-python Implementation Plan & Roadmap

## Overview

Build `wetwire-gitlab-python` following the same patterns as `wetwire-aws-python` — a synthesis library that generates GitLab CI/CD configuration YAML from typed Python declarations using dataclasses.

**Scope**: Full GitLab DevOps — CI/CD pipelines, Auto DevOps integration, GitLab Runner configuration, and CI/CD Components.

For the wetwire pattern, see the [Wetwire Specification](https://github.com/lex00/wetwire/blob/main/docs/WETWIRE_SPEC.md).

---

## Key Decisions

- **Validation**: Use `glab ci lint` via subprocess (requires GitLab access)
- **Schema Source**: GitLab's internal CI schema (`app/assets/javascripts/editor/schema/ci.json`)
- **Component Wrappers**: Generate typed wrappers for official `gitlab.com/components/*` catalog
- **Approach**: Full feature parity with wetwire-aws-python

---

## Feature Matrix: wetwire-aws-python → wetwire-gitlab-python

| Feature | wetwire-aws-python | wetwire-gitlab-python |
|---------|-------------------|----------------------|
| **Schema Source** | CloudFormation spec JSON | GitLab CI schema JSON |
| **Schema URL** | AWS CF spec URL | `gitlab.com/gitlab-org/gitlab/-/blob/master/app/assets/javascripts/editor/schema/ci.json` |
| **Secondary Source** | — | CI/CD Component definitions from `gitlab.com/components/*` |
| **Output Format** | CloudFormation JSON/YAML | GitLab CI `.gitlab-ci.yml` YAML |
| **Generated Types** | AWS service dataclasses | Pipeline, Job, Stage, Rules, Triggers + Component wrappers |
| **Intrinsics** | Ref, GetAtt, Sub, Join, etc. | Predefined variables (CI_*, GITLAB_*), input interpolation |
| **Validation** | cfn-lint integration | glab ci lint integration |

---

## Schema Sources

### 1. GitLab CI Schema
- **Location**: `app/assets/javascripts/editor/schema/ci.json` in GitLab repo
- **Raw**: `https://gitlab.com/gitlab-org/gitlab/-/raw/master/app/assets/javascripts/editor/schema/ci.json`
- **Provides**: All CI/CD keywords — jobs, stages, rules, artifacts, cache, triggers, includes

### 2. CI/CD Component Definitions
- **Catalog**: `https://gitlab.com/explore/catalog`
- **Official Group**: `gitlab.com/components/*`
- **Components to generate wrappers for**:
  - `components/sast` — Static Application Security Testing
  - `components/secret-detection` — Secret scanning
  - `components/dependency-scanning` — Dependency vulnerability scanning
  - `components/container-scanning` — Container image scanning
  - `components/dast` — Dynamic Application Security Testing
  - `components/license-scanning` — License compliance
  - `components/coverage-report` — Code coverage reporting
  - (extensible list in config)

### 3. Auto DevOps Templates
- **Location**: `lib/gitlab/ci/templates/Auto-DevOps.gitlab-ci.yml`
- **Provides**: Auto Build, Auto Test, Auto Deploy, Auto DAST stages
- **Templates**: `Jobs/Build.gitlab-ci.yml`, `Jobs/Deploy.gitlab-ci.yml`, etc.

---

## Package Design for Clean Syntax

The package structure enables clean, readable Python code through strategic imports:

### User-Facing Packages

```python
from wetwire_gitlab.intrinsics import CI, GitLab, MR, on_default_branch, on_tag, always
from wetwire_gitlab.pipeline import Job, Rule, Artifacts, Cache, Image
from wetwire_gitlab.components import sast
```

**`intrinsics` module** — Provides helpers:
- `CI` — Predefined CI_* variables (`CI.commit_sha`, `CI.default_branch`)
- `GitLab` — Predefined GITLAB_* variables
- `MR` — Predefined merge request variables
- Pre-defined rules: `on_default_branch`, `on_tag`, `on_merge_request`, `manual_only`
- When constants: `ALWAYS`, `NEVER`, `ON_SUCCESS`, `ON_FAILURE`, `MANUAL`

**`pipeline` module** — Core types:
- `Job` — Job configuration
- `Rule` — Rule configuration
- `Artifacts` — Artifacts configuration
- `Cache` — Cache configuration
- `Image` — Image configuration
- `Environment` — Environment configuration

---

## Generated Package Structure (User Projects)

Both `wetwire-gitlab init` and `wetwire-gitlab import` generate the same package structure:

```bash
# Create new pipeline project
wetwire-gitlab init -o myproject/

# Import existing .gitlab-ci.yml
wetwire-gitlab import .gitlab-ci.yml -o myproject/
```

**Generated structure:**
```
myproject/
├── pyproject.toml             # Package configuration
├── CLAUDE.md                  # AI context for agents
├── README.md
├── .gitignore
│
├── src/
│   └── myproject/
│       ├── __init__.py
│       ├── params.py          # Variables, includes, workflow
│       └── jobs.py            # Job definitions
│
└── tests/
    └── __init__.py
```

**Example jobs.py:**
```python
from wetwire_gitlab.intrinsics import CI, on_default_branch
from wetwire_gitlab.pipeline import Job, Artifacts, Image

# Stages defines pipeline stage order
stages = ["build", "test", "deploy"]

# Extracted nested config
build_artifacts = Artifacts(
    paths=["bin/", "dist/"],
    expire_in="1 week",
)

# Reusable image config
golang_image = Image(name="golang:1.23")

# Build job
build_job = Job(
    name="build",
    stage="build",
    image=golang_image,
    script=["go build -v ./..."],
    artifacts=build_artifacts,
)

# Test job runs after build
test_job = Job(
    name="test",
    stage="test",
    image=golang_image,
    script=["go test -v ./..."],
    needs=[build_job],
    rules=[on_default_branch],
)
```

**Key syntax patterns:**
- `CI.commit_tag` — Attribute access for predefined variables
- `on_default_branch` — Pre-defined rule from intrinsics
- `Job(...)` — Explicit dataclass instantiation
- `golang_image` — Direct variable reference
- `[build_job]` — Job dependencies via variable names

---

## Library Directory Structure

```
wetwire-gitlab-python/
├── .github/
│   └── workflows/
│       ├── ci.yml              # Build/test on push/PR
│       └── publish.yml         # PyPI publishing
│
├── scripts/
│   ├── ci.sh                   # Local CI runner
│   └── import_samples.sh       # Round-trip testing
│
├── src/
│   └── wetwire_gitlab/
│       ├── __init__.py
│       ├── cli/                # CLI application (typer)
│       │   ├── __init__.py
│       │   ├── main.py
│       │   ├── build.py        # Generate .gitlab-ci.yml
│       │   ├── validate.py     # Validate via glab ci lint
│       │   ├── list.py         # List discovered pipelines/jobs
│       │   ├── lint.py         # Code quality rules
│       │   ├── import_.py      # YAML → Python conversion
│       │   └── init.py         # Project scaffolding
│       │
│       ├── discover/           # AST-based pipeline discovery
│       ├── runner/             # Runtime value extraction
│       ├── importer/           # YAML to Python code conversion
│       ├── linter/             # Python code lint rules (WGL001-WGL0XX)
│       ├── template/           # Pipeline YAML builder
│       ├── serialize/          # YAML serialization
│       ├── validation/         # glab ci lint integration
│       │
│       ├── intrinsics.py       # Helper types and functions
│       │
│       ├── pipeline/           # Core pipeline types (hand-written)
│       │   ├── __init__.py
│       │   ├── pipeline.py     # Pipeline dataclass
│       │   ├── job.py          # Job dataclass
│       │   ├── stage.py        # Stage ordering
│       │   ├── rules.py        # Rules (if, changes, exists)
│       │   ├── triggers.py     # Trigger types (push, merge_request, schedule)
│       │   ├── artifacts.py    # Artifacts configuration
│       │   ├── cache.py        # Cache configuration
│       │   ├── variables.py    # Variable contexts (CI_*, GITLAB_*)
│       │   ├── include.py      # Include directives (component, template, etc.)
│       │   └── workflow.py     # Workflow rules
│       │
│       ├── components/         # GENERATED component wrappers
│       │   ├── __init__.py
│       │   ├── sast.py         # Typed wrapper for components/sast
│       │   ├── secret_detection.py
│       │   └── ... (catalog components)
│       │
│       ├── templates/          # Auto DevOps template wrappers
│       │   ├── __init__.py
│       │   ├── autodevops.py   # Auto DevOps full pipeline
│       │   └── build.py        # Jobs/Build.gitlab-ci.yml wrapper
│       │
│       ├── runner_config/      # GitLab Runner config types
│       │   ├── __init__.py
│       │   ├── config.py       # config.toml structure
│       │   ├── executor.py     # Executor types (docker, shell, kubernetes)
│       │   └── runner.py       # Runner registration/config
│       │
│       └── contracts.py        # Protocols and types
│
├── codegen/                    # Code generation tooling
│   ├── fetch.py                # Download CI schema + component specs
│   ├── parse.py                # Parse schemas
│   └── generate.py             # Generate Python types
│
├── docs/
│   ├── ROADMAP.md              # This file
│   ├── FAQ.md
│   ├── QUICK_START.md
│   └── CLI.md
│
├── specs/                      # .gitignore'd (fetched schemas)
│   ├── .gitkeep
│   ├── manifest.json
│   ├── ci-schema.json
│   └── components/
│       ├── sast.yml
│       └── ...
│
├── tests/
├── pyproject.toml
└── README.md
```

---

## CLI Commands

### 1. `wetwire-gitlab build`
- Discover pipeline declarations from Python packages
- Serialize to GitLab CI YAML
- Output to `.gitlab-ci.yml` or custom path

### 2. `wetwire-gitlab validate`
- Run `glab ci lint` on generated YAML
- Report errors in structured format (text/JSON)
- Requires `glab` CLI installed and authenticated

### 3. `wetwire-gitlab list`
- List discovered pipelines and jobs
- Show file locations and dependencies

### 4. `wetwire-gitlab lint`
- Python code quality rules (WGL001-WGL0XX)
- Examples:
  - WGL001: Use typed component wrappers instead of raw `include:component` strings
  - WGL002: Use rules instead of raw YAML expressions
  - WGL003: Use predefined variable constants instead of raw strings
  - WGL004: Use cache dataclass instead of inline dicts
  - WGL005: Use artifacts dataclass instead of inline dicts
  - WGL006: Use typed stage constants

### 5. `wetwire-gitlab import`
- Convert existing `.gitlab-ci.yml` to Python code
- Generate typed declarations
- Scaffold project structure

### 6. `wetwire-gitlab init`
- Create new project with example pipeline
- Generate pyproject.toml, package structure, pipeline definitions

### 7. `wetwire-gitlab design`
- AI-assisted infrastructure design via wetwire-core
- Interactive session with lint feedback loop

### 8. `wetwire-gitlab test`
- Persona-based testing via wetwire-core
- Automated evaluation of code generation quality

### 9. `wetwire-gitlab graph`
- Generate DAG visualization of pipeline jobs
- Formats: `--format dot` (Graphviz), `--format mermaid` (GitHub/GitLab markdown)

---

## CLI Exit Codes

Per the wetwire specification, CLI commands use consistent exit codes:

| Command | Exit 0 | Exit 1 | Exit 2 |
|---------|--------|--------|--------|
| `build` | Success | Error (parse, generation) | — |
| `lint` | No issues | Issues found | Error (parse failure) |
| `import` | Success | Error (parse, generation) | — |
| `validate` | Valid | Invalid (glab ci lint errors) | Error (file not found) |
| `list` | Success | Error | — |
| `init` | Success | Error (dir exists, write fail) | — |

---

## The Declarative Pattern

Wetwire follows a **flat declaration** pattern with **direct variable references**:

```python
# References are variable names, not function calls
needs=[build_job]           # NOT: needs(build_job)

# Nested configs are separate variables
artifacts=build_artifacts   # NOT: artifacts=Artifacts(...)

# Predefined variables via attribute access
if_=CI.default_branch       # NOT: if_="$CI_DEFAULT_BRANCH"
```

### Design: Dataclass Fields

All configuration uses dataclasses with optional fields:

```python
# wetwire-gitlab-python
@dataclass
class Job:
    name: str = ""
    image: Image | None = None      # Optional nested dataclass
    artifacts: Artifacts | None = None
    # ...
```

**Why dataclasses for GitLab CI?**
- **Simpler syntax**: Clean field initialization
- **YAML semantics**: None values and "not set" are equivalent in GitLab CI YAML
- **Serialization**: Use dataclasses-json or custom serialization to omit None values
- **Flat declarations**: Extracted variables assign directly

---

## Architecture: Discovery & Serialization

The key insight from `wetwire-aws-python` is that resource references work through a combination of:
1. **AST-based discovery** — Parse Python source to find module-level assignments
2. **Runtime value extraction** — Import module and access variable values
3. **Custom serialization** — Transform references during serialization

### JobRef Type

```python
# contracts.py
from dataclasses import dataclass
from typing import Any

@dataclass
class JobRef:
    """Reference to another job for needs/dependencies."""
    job: str  # Resolved job name
    artifacts: bool = False  # Whether to download artifacts (optional)

    def to_dict(self) -> str | dict[str, Any]:
        """Serialize to GitLab CI needs format."""
        if self.artifacts:
            return {"job": self.job, "artifacts": True}
        return self.job

    def is_empty(self) -> bool:
        return self.job == ""
```

### Serialization Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                        User's Python Package                         │
│                                                                     │
│  build_job = Job(                                                   │
│      name="build",                                                  │
│      script=["go build ./..."],                                     │
│  )                                                                  │
│                                                                     │
│  test_job = Job(                                                    │
│      needs=[build_job],  # Variable reference                       │
│  )                                                                  │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    1. AST Discovery Phase                           │
│                                                                     │
│  • Parse Python source files                                        │
│  • Find module-level assignments of type Job                        │
│  • Extract: build_job (no deps), test_job (deps: [build_job])       │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  2. Runtime Value Extraction                        │
│                                                                     │
│  • Import user's module                                             │
│  • Access module-level variables                                    │
│  • Serialize to dict, resolving Job references to names             │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    3. Pipeline Building                             │
│                                                                     │
│  • Topological sort jobs by dependencies                            │
│  • Generate YAML in dependency order                                │
│  • Output .gitlab-ci.yml                                            │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        Generated YAML                               │
│                                                                     │
│  build:                                                             │
│    script:                                                          │
│      - go build ./...                                               │
│                                                                     │
│  test:                                                              │
│    needs:                                                           │
│      - build                                                        │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Integration with wetwire-core

Same pattern as wetwire-aws-python:

```python
# RunnerAgent tools for wetwire-gitlab
tools = [
    "init_package",      # wetwire-gitlab init
    "write_file",        # Write Python pipeline code
    "read_file",         # Read files
    "run_lint",          # wetwire-gitlab lint --format json
    "run_build",         # wetwire-gitlab build --format json
    "run_validate",      # wetwire-gitlab validate (glab ci lint)
    "ask_developer",     # Clarification questions
]
```

CLI must support `--format json` for agent integration.

---

## glab Integration

```python
# validation/glab.py
import subprocess
import json
from dataclasses import dataclass

@dataclass
class ValidateResult:
    valid: bool
    errors: list[str] | None = None
    merged_yaml: str | None = None

def validate_pipeline(path: str) -> ValidateResult:
    """Validate pipeline using glab ci lint."""
    result = subprocess.run(
        ["glab", "ci", "lint", path, "--include-jobs"],
        capture_output=True,
        text=True,
    )

    # Parse glab output...
    return ValidateResult(
        valid=result.returncode == 0,
        errors=parse_errors(result.stderr) if result.returncode != 0 else None,
    )
```

Note: `glab ci lint` requires:
- `glab` CLI installed
- Authentication to GitLab instance
- Access to the project (for includes resolution)

---

## Feature Matrix

| Feature | Phase | Status | Dependencies |
|---------|-------|--------|--------------|
| **Core Types** | | | |
| ├─ Pipeline dataclass | 1A | [ ] | — |
| ├─ Job dataclass | 1A | [ ] | — |
| ├─ Stage ordering | 1A | [ ] | — |
| ├─ Rules dataclass | 1A | [ ] | — |
| ├─ Pre-defined Rule variables (on_default_branch, on_tag, etc.) | 1A | [ ] | — |
| ├─ Triggers (push, mr, schedule, etc.) | 1A | [ ] | — |
| ├─ Artifacts dataclass | 1A | [ ] | — |
| ├─ Cache dataclass | 1A | [ ] | — |
| ├─ Include directives (all 6 types) | 1A | [ ] | — |
| ├─ Workflow dataclass | 1A | [ ] | — |
| ├─ Trigger dataclass (child/multi-project pipelines) | 1A | [ ] | — |
| ├─ Variables contexts (CI_, GITLAB_, MR_) | 1A | [ ] | — |
| ├─ Result types (Build/Lint/Validate/List) | 1A | [ ] | — |
| └─ DiscoveredPipeline/Job dataclasses | 1A | [ ] | — |
| **Contracts (contracts.py)** | | | |
| ├─ Resource protocol | 1A | [ ] | — |
| ├─ JobRef dataclass | 1A | [ ] | — |
| ├─ JobRef.to_dict() (custom serialization) | 1A | [ ] | — |
| ├─ JobRef.is_empty() | 1A | [ ] | — |
| └─ DiscoveredJob dataclass | 1A | [ ] | — |
| **Intrinsics Module** | | | |
| ├─ CI context class | 1A | [ ] | — |
| ├─ GitLab context class | 1A | [ ] | — |
| ├─ MR context class | 1A | [ ] | — |
| └─ Predefined constants (When, CachePolicy, etc.) | 1A | [ ] | — |
| **Serialization** | | | |
| ├─ Pipeline → YAML | 1B | [ ] | Core Types |
| ├─ Job → YAML | 1B | [ ] | Core Types |
| ├─ Rules → YAML | 1B | [ ] | Core Types |
| ├─ Artifacts → YAML | 1B | [ ] | Core Types |
| ├─ Cache → YAML | 1B | [ ] | Core Types |
| ├─ Include → YAML | 1B | [ ] | Core Types |
| ├─ Variables → YAML | 1B | [ ] | Core Types |
| ├─ Dataclass → dict via dataclasses.asdict | 1B | [ ] | Core Types |
| ├─ Field name case conversion (per schema spec) | 1B | [ ] | — |
| └─ None value omission | 1B | [ ] | — |
| **CLI Framework** | | | |
| ├─ main.py + typer setup | 1C | [ ] | — |
| ├─ `init` command | 1C | [ ] | — |
| ├─ `build` command (stub) | 1C | [ ] | — |
| ├─ `validate` command (stub) | 1C | [ ] | — |
| ├─ `list` command (stub) | 1C | [ ] | — |
| ├─ `lint` command (stub) | 1C | [ ] | — |
| ├─ `import` command (stub) | 1C | [ ] | — |
| ├─ `design` command (stub) | 1C | [ ] | — |
| ├─ `test` command (stub) | 1C | [ ] | — |
| ├─ `graph` command (stub) | 1C | [ ] | — |
| ├─ `version` command | 1C | [ ] | — |
| ├─ --type flag (pipeline/runner) | 1C | [ ] | — |
| └─ Exit code semantics (0/1/2) | 1C | [ ] | — |
| **Schema Fetching** | | | |
| ├─ HTTP fetcher with retry | 1D | [ ] | — |
| ├─ CI schema fetch (gitlab-org/gitlab) | 1D | [ ] | — |
| ├─ Component spec fetch (components/sast) | 1D | [ ] | — |
| ├─ Component spec fetch (components/secret-detection) | 1D | [ ] | — |
| ├─ Component spec fetch (components/dependency-scanning) | 1D | [ ] | — |
| ├─ Component spec fetch (components/container-scanning) | 1D | [ ] | — |
| ├─ Component spec fetch (components/dast) | 1D | [ ] | — |
| ├─ Component spec fetch (components/license-scanning) | 1D | [ ] | — |
| ├─ Component spec fetch (components/coverage-report) | 1D | [ ] | — |
| └─ specs/manifest.json | 1D | [ ] | — |
| **Schema Parsing** | | | |
| ├─ CI schema parser (ci.json) | 2A | [ ] | Schema Fetching |
| ├─ Component spec parser | 2A | [ ] | Schema Fetching |
| └─ Intermediate representation | 2A | [ ] | Schema Fetching |
| **Component Codegen** | | | |
| ├─ Generator templates (Jinja2) | 2B | [ ] | Schema Parsing |
| ├─ Code formatting (ruff) | 2B | [ ] | — |
| ├─ components/sast wrapper | 2B | [ ] | Schema Parsing |
| ├─ components/secret_detection wrapper | 2B | [ ] | Schema Parsing |
| ├─ components/dependency_scanning wrapper | 2B | [ ] | Schema Parsing |
| ├─ components/container_scanning wrapper | 2B | [ ] | Schema Parsing |
| ├─ components/dast wrapper | 2B | [ ] | Schema Parsing |
| ├─ components/license_scanning wrapper | 2B | [ ] | Schema Parsing |
| └─ components/coverage_report wrapper | 2B | [ ] | Schema Parsing |
| **AST Discovery** | | | |
| ├─ Package scanning (ast module) | 2C | [ ] | Core Types |
| ├─ Pipeline variable detection | 2C | [ ] | Core Types |
| ├─ Job variable detection | 2C | [ ] | Core Types |
| ├─ Dependency graph building | 2C | [ ] | Core Types |
| ├─ Reference validation | 2C | [ ] | Core Types |
| ├─ Recursive directory traversal | 2C | [ ] | — |
| └─ __pycache__/hidden directory exclusion | 2C | [ ] | — |
| **Runner (Value Extraction)** | | | |
| ├─ Dynamic module import | 2G | [ ] | AST Discovery |
| ├─ pyproject.toml parsing | 2G | [ ] | — |
| ├─ Module path resolution | 2G | [ ] | — |
| └─ Dict value extraction | 2G | [ ] | — |
| **Template Builder** | | | |
| ├─ Topological sort (Kahn's algorithm) | 2H | [ ] | AST Discovery |
| ├─ Cycle detection | 2H | [ ] | AST Discovery |
| └─ Dependency ordering | 2H | [ ] | AST Discovery |
| **Build Command (full)** | | | |
| ├─ Discovery integration | 3A | [ ] | AST Discovery |
| ├─ Runner integration | 3A | [ ] | Runner |
| ├─ Template builder integration | 3A | [ ] | Template Builder |
| ├─ Multi-pipeline support | 3A | [ ] | Serialization |
| ├─ Output to `.gitlab-ci.yml` | 3A | [ ] | Serialization |
| ├─ --format json/yaml | 3A | [ ] | — |
| └─ --output flag | 3A | [ ] | — |
| **Validation (glab ci lint)** | | | |
| ├─ glab subprocess integration | 2D | [ ] | — |
| ├─ ValidateResult types | 2D | [ ] | — |
| ├─ --include-jobs support | 2D | [ ] | — |
| ├─ --dry-run support | 2D | [ ] | — |
| └─ `validate` command (full) | 3B | [ ] | glab integration |
| **Linting Rules** | | | |
| ├─ Linter framework | 2E | [ ] | — |
| ├─ Rule protocol | 2E | [ ] | — |
| ├─ WGL001: typed component wrappers | 2E | [ ] | — |
| ├─ WGL002: rules dataclass | 2E | [ ] | — |
| ├─ WGL003: predefined variables | 2E | [ ] | — |
| ├─ WGL004: cache dataclass | 2E | [ ] | — |
| ├─ WGL005: artifacts dataclass | 2E | [ ] | — |
| ├─ WGL006: typed stage constants | 2E | [ ] | — |
| ├─ WGL007: duplicate job names | 2E | [ ] | — |
| ├─ WGL008: file too large (>N jobs) | 2E | [ ] | — |
| ├─ Recursive package scanning | 2E | [ ] | — |
| ├─ --fix flag support | 2E | [ ] | — |
| └─ `lint` command (full) | 3C | [ ] | Linter framework |
| **Import (YAML → Python)** | | | |
| ├─ YAML parser | 2F | [ ] | — |
| ├─ IR (intermediate representation) | 2F | [ ] | — |
| ├─ IRPipeline, IRJob, IRRules dataclasses | 2F | [ ] | — |
| ├─ Include resolution tracking | 2F | [ ] | — |
| ├─ Python code generator | 3D | [ ] | YAML parser, Core Types |
| ├─ Field name transformation | 3D | [ ] | — |
| ├─ Reserved name handling (if_, with_) | 3D | [ ] | — |
| ├─ Scaffold: pyproject.toml | 3D | [ ] | — |
| ├─ Scaffold: src/package/__init__.py | 3D | [ ] | — |
| ├─ Scaffold: README.md | 3D | [ ] | — |
| ├─ Scaffold: CLAUDE.md | 3D | [ ] | — |
| ├─ Scaffold: .gitignore | 3D | [ ] | — |
| ├─ --single-file flag | 3D | [ ] | — |
| ├─ --no-scaffold flag | 3D | [ ] | — |
| └─ `import` command (full) | 3D | [ ] | Python code generator |
| **List Command** | | | |
| ├─ Table output format | 3E | [ ] | AST Discovery |
| ├─ --format json | 3E | [ ] | — |
| └─ `list` command (full) | 3E | [ ] | AST Discovery |
| **Graph Command (DAG Visualization)** | | | |
| ├─ graphviz library integration | 3H | [ ] | AST Discovery |
| ├─ DOT format output | 3H | [ ] | — |
| ├─ Mermaid format output | 3H | [ ] | — |
| ├─ Job dependency edge extraction | 3H | [ ] | AST Discovery |
| └─ `graph` command (full) | 3H | [ ] | AST Discovery |
| **Auto DevOps Templates** | | | |
| ├─ AutoDevOps dataclass | 5A | [ ] | Core Types |
| ├─ Jobs/Build.gitlab-ci.yml wrapper | 5A | [ ] | Core Types |
| ├─ Jobs/Deploy.gitlab-ci.yml wrapper | 5A | [ ] | Core Types |
| ├─ Jobs/Test.gitlab-ci.yml wrapper | 5A | [ ] | Core Types |
| ├─ Jobs/SAST.gitlab-ci.yml wrapper | 5A | [ ] | Core Types |
| └─ Jobs/DAST.gitlab-ci.yml wrapper | 5A | [ ] | Core Types |
| **GitLab Runner Config** | | | |
| ├─ Config (config.toml) dataclass | 5B | [ ] | — |
| ├─ Runner dataclass | 5B | [ ] | — |
| ├─ Executor enum (shell, docker, kubernetes...) | 5B | [ ] | — |
| ├─ DockerConfig dataclass | 5B | [ ] | — |
| ├─ KubernetesConfig dataclass | 5B | [ ] | — |
| ├─ MachineConfig dataclass | 5B | [ ] | — |
| ├─ CacheConfig dataclass | 5B | [ ] | — |
| ├─ to_toml() serialization method | 5B | [ ] | — |
| └─ `build --type=runner` integration | 5B | [ ] | Build Command |
| **Design Command (AI-assisted)** | | | |
| ├─ wetwire-core orchestrator | 3F | [ ] | All CLI commands |
| ├─ Interactive session | 3F | [ ] | — |
| ├─ --stream flag | 3F | [ ] | — |
| ├─ --max-lint-cycles flag | 3F | [ ] | — |
| └─ `design` command (full) | 3F | [ ] | wetwire-core |
| **Test Command (Persona-based)** | | | |
| ├─ Persona selection | 3G | [ ] | wetwire-core |
| ├─ Scenario configuration | 3G | [ ] | — |
| ├─ Result writing | 3G | [ ] | — |
| ├─ Session tracking | 3G | [ ] | — |
| └─ `test` command (full) | 3G | [ ] | wetwire-core |
| **Reference Example Testing** | | | |
| ├─ Fetch gitlab-org/gitlab pipelines | 4A | [ ] | Schema Fetching |
| ├─ Import/rebuild cycle tests | 4A | [ ] | Import, Build |
| ├─ Round-trip validation | 4A | [ ] | Import, Build, Validate |
| └─ Success rate tracking | 4A | [ ] | — |
| **wetwire-core Integration** | | | |
| ├─ RunnerAgent tool definitions | 4B | [ ] | All CLI commands |
| ├─ Tool handlers implementation | 4B | [ ] | — |
| ├─ Stream handler support | 4B | [ ] | — |
| ├─ Session result writing | 4B | [ ] | — |
| ├─ Scoring integration | 4B | [ ] | — |
| └─ Agent testing with personas | 4B | [ ] | — |

---

## Phased Implementation

### Phase 1: Foundation (Parallel Streams)

All Phase 1 work streams can be developed **in parallel** with no dependencies on each other.

```
┌─────────────────────────────────────────────────────────────────────────┐
│ PHASE 1: Foundation                                                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │     1A       │  │     1B       │  │     1C       │  │     1D       │ │
│  │  Core Types  │  │ Serialization│  │     CLI      │  │Schema Fetch  │ │
│  │              │  │              │  │  Framework   │  │              │ │
│  │  pipeline/   │  │  serialize/  │  │    cli/      │  │  codegen/    │ │
│  │  intrinsics  │  │              │  │              │  │  fetch.py    │ │
│  │  contracts   │  │              │  │              │  │              │ │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘ │
│         │                 │                 │                 │         │
│         │                 │                 │                 │         │
│         ▼                 ▼                 ▼                 ▼         │
│    No deps           Needs 1A          No deps           No deps       │
│                      (can stub)                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Phase 2: Core Capabilities (Parallel Streams)

Phase 2 streams have dependencies on Phase 1 but are **parallel to each other**.

### Phase 3: Command Integration (Parallel Streams)

Phase 3 integrates Phase 2 capabilities into CLI commands.

### Phase 4: Polish & Integration

Reference example testing and wetwire-core integration.

### Phase 5: Extended Features

Auto DevOps templates and GitLab Runner configuration.

---

## Progress Tracking

### Phase 1 Progress
- [ ] 1A: Core Types + Contracts + Intrinsics (0/22)
- [ ] 1B: Serialization (0/10)
- [ ] 1C: CLI Framework (0/13)
- [ ] 1D: Schema Fetching (0/10)

### Phase 2 Progress
- [ ] 2A: Schema Parsing (0/3)
- [ ] 2B: Component Codegen (0/9)
- [ ] 2C: AST Discovery (0/7)
- [ ] 2D: glab Integration (0/4)
- [ ] 2E: Linter Rules (0/12)
- [ ] 2F: YAML Parser (0/4)
- [ ] 2G: Runner/Value Extraction (0/4)
- [ ] 2H: Template Builder (0/3)

### Phase 3 Progress
- [ ] 3A: Build Command (0/7)
- [ ] 3B: Validate Command (0/1)
- [ ] 3C: Lint Command (0/1)
- [ ] 3D: Import Command (0/15)
- [ ] 3E: List Command (0/3)
- [ ] 3F: Design Command (0/5)
- [ ] 3G: Test Command (0/5)
- [ ] 3H: Graph Command (0/5)

### Phase 4 Progress
- [ ] 4A: Reference Example Testing (0/4)
- [ ] 4B: wetwire-core Integration (0/6)

### Phase 5 Progress
- [ ] 5A: Auto DevOps Templates (0/6)
- [ ] 5B: GitLab Runner Config (0/9)

---

## Critical Path

The minimum sequence to reach a working `build` command:

```
1A (Core Types) → 1B (Serialization) ─┐
                                      ├→ 2C (AST Discovery) → 2G (Runner) ─┐
                                      │                      2H (Template) ┼→ 3A (build)
                                      └────────────────────────────────────┘
```

The minimum sequence to reach a working `import` command:

```
1A (Core Types) ─┐
                 ├→ 3D (import)
2F (YAML Parser) ┘
```

---

## Feature Count Summary

| Phase | Streams | Features |
|-------|---------|----------|
| Phase 1 | 4 | 55 |
| Phase 2 | 8 | 46 |
| Phase 3 | 8 | 42 |
| Phase 4 | 2 | 10 |
| Phase 5 | 2 | 15 |
| **Total** | **24** | **168** |

---

## Design Decisions

### Child Pipelines ✅

**Decision:** Yes, support `trigger:include` for multi-project and child pipeline orchestration.

```python
# Child pipeline trigger
deploy_trigger = Trigger(
    include="deploy/.gitlab-ci.yml",
    strategy="depend",
)

trigger_deploy = Job(
    name="trigger-deploy",
    stage="deploy",
    trigger=deploy_trigger,
)

# Multi-project trigger
downstream_trigger = Trigger(
    project="group/downstream-project",
    branch="main",
)
```

### DAG Visualization ✅

**Decision:** Yes, generate pipeline graphs using graphviz library.

Supports both DOT (Graphviz) and Mermaid output formats:

```bash
wetwire-gitlab graph ./my-pipeline --format mermaid
wetwire-gitlab graph ./my-pipeline --format dot
```

### Components: Scope ✅

**Decision:** Support **referencing** and **importing** components. Defer **authoring**.

| Capability | Description | Status |
|------------|-------------|--------|
| **Referencing** | Use typed wrappers in pipelines (`sast.SAST()`) | ✅ In scope |
| **Importing** | Convert `include: component:` → Python code | ✅ In scope |
| **Authoring** | Create component templates in Python | ⏸️ Deferred |

### Runner Config: CLI Integration ✅

**Decision:** Integrate via `--type=runner` flag. Default type is `pipeline`.

```bash
wetwire-gitlab build ./my-config                    # default: --type=pipeline → .gitlab-ci.yml
wetwire-gitlab build --type=pipeline ./my-config    # .gitlab-ci.yml
wetwire-gitlab build --type=runner ./my-config      # config.toml
```

---

## Research Sources

- [GitLab CI/CD YAML syntax reference](https://docs.gitlab.com/ci/yaml/)
- [Predefined CI/CD variables reference](https://docs.gitlab.com/ci/variables/predefined_variables/)
- [CI/CD Components](https://docs.gitlab.com/ci/components/)
- [glab ci lint](https://docs.gitlab.com/cli/ci/lint/)
- [GitLab Runner configuration](https://docs.gitlab.com/runner/configuration/advanced-configuration/)
- [Auto DevOps stages](https://docs.gitlab.com/topics/autodevops/stages/)
- [CI/CD Catalog](https://gitlab.com/explore/catalog)
