# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

#### Phase 3: Command Integration

- **Build Command** (`cli/`) - Full build command implementation: discovers jobs/pipelines, extracts values via runner, generates YAML/JSON output with --format and --output flags (#43)
- **Validate Command** (`cli/`) - Pipeline validation using glab CLI integration with --include-jobs support (#44)
- **Lint Command** (`cli/`) - Python code quality rules with text/JSON output and exit codes (#45)
- **Import Command** (`cli/`) - Convert .gitlab-ci.yml to Python code with code generation, scaffold support, and --single-file/--no-scaffold flags (#46)
- **List Command** (`cli/`) - Display discovered jobs and pipelines with table/JSON output formats (#47)
- **Design Command** (`cli/`) - Stub for AI-assisted design requiring wetwire-core integration (#48)
- **Test Command** (`cli/`) - Stub for persona-based evaluation requiring wetwire-core integration (#48)
- **Graph Command** (`cli/`) - DAG visualization with Mermaid and DOT format output (#48)

#### Phase 5: Extended Features

- **Auto DevOps Templates** (`templates/`) - Typed wrappers for GitLab Auto DevOps: AutoDevOps, AutoDevOpsConfig dataclasses with to_include() and to_variables() methods (#50)
- **Job Templates** (`templates/`) - Build, Test, Deploy, SAST, DAST template wrappers for Jobs/*.gitlab-ci.yml and Security/*.gitlab-ci.yml includes (#50)

#### Phase 4: Polish & Integration

- **Reference Example Testing** (`tests/`) - Comprehensive tests for YAML parsing, code generation quality, round-trip conversion, and real-world patterns (#49)

#### Phase 2: Core Capabilities

- **Template Builder** (`template/`) - Topological sort using Kahn's algorithm, cycle detection, and dependency ordering for YAML generation (#42)
- **Runner/Value Extraction** (`runner/`) - Dynamic module import using importlib, pyproject.toml parsing, and value extraction from Python modules (#41)
- **YAML Parser** (`importer/`) - Parse existing `.gitlab-ci.yml` files into intermediate representation with IRPipeline, IRJob, IRRule, IRInclude types (#40)
- **Linter Rules** (`linter/`) - 8 lint rules (WGL001-WGL008) for pipeline code quality checking with rule filtering and directory scanning (#39)
- **glab Integration** (`validation/`) - GitLab CLI integration for pipeline validation with `--include-jobs` and `--dry-run` support (#38)
- **AST Discovery** (`discover/`) - AST-based discovery of Job and Pipeline declarations in Python source files with dependency graph building (#37)
- **Component Codegen** (`codegen/generate.py`) - Jinja2-based code generation for typed component wrappers with acronym handling (#36)
- **Schema Parsing** (`codegen/parse.py`) - Parse GitLab CI JSON schema and component YAML specs into intermediate representation (#35)

#### Phase 1: Foundation

- **Schema Fetching** (`codegen/fetch.py`) - HTTP fetching with retry logic for CI schema and component specifications (#34)
- **CLI Framework** (`cli/`) - argparse-based CLI with subcommands: build, validate, list, lint, import, init, design, test, graph, version (#33)
- **Serialization** (`serialize/`) - Convert typed dataclasses to YAML with field name conversion and nested object support (#32)
- **Core Types** (`pipeline/`) - Typed dataclasses for GitLab CI configuration: Job, Pipeline, Rule, Artifacts, Cache, Include, Workflow, Trigger, Variables, Image, Default (#31)
- **Contracts** (`contracts.py`) - JobRef, DiscoveredJob, DiscoveredPipeline, BuildResult, LintResult, ValidateResult types (#31)
- **Intrinsics** (`intrinsics.py`) - CI/CD variable references (CI, GitLab, MR contexts), When/CachePolicy constants, predefined rules (#31)

### Dependencies

- Added `jinja2>=3.0` for template-based code generation
- Added `pyyaml>=6.0` for YAML parsing and serialization

## [0.1.0] - Unreleased

Initial development release.

### Added

- Project structure with `src/wetwire_gitlab` package
- Development tooling: ruff, pytest, ty
- GitHub Actions CI for Python 3.11, 3.12, 3.13

[Unreleased]: https://github.com/lex00/wetwire-gitlab-python/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/lex00/wetwire-gitlab-python/releases/tag/v0.1.0
