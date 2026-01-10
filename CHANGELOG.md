# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

#### Phase 9B: Documentation Improvements

- **EXAMPLES.md** (`docs/EXAMPLES.md`) - Comprehensive examples documentation (#80)
  - Documented all 5 example projects with key patterns
  - Added pattern reference table
  - Added README.md examples section with link

#### Phase 9A: Job Reference Support

- **Job Reference Support** (`serialize/converter.py`) - Direct Job references in needs/dependencies (#79)
  - Support Job instances in `needs` and `dependencies` fields
  - Extract job name automatically from Job.name field
  - Backwards compatible with string references
  - Updated CLAUDE.md with Job reference examples
  - Type-safe: IDE can verify Job references exist

#### Phase 7D: Kiro Provider Support

- **Kiro Provider** (`kiro/`) - Alternative AI provider for design and test commands (#67)
  - `check_kiro_installed()`: Check if kiro-cli is available
  - `install_kiro_configs()`: Install agent and MCP configurations
  - `launch_kiro()`: Launch interactive Kiro session with wetwire-runner agent
  - `run_kiro_scenario()`: Run non-interactive Kiro scenario for testing
  - Agent config with GitLab-specific prompt and MCP server integration
  - `--provider` flag for design/test commands (anthropic/kiro, default: anthropic)
  - `--timeout` flag for test command with Kiro provider
  - Optional `kiro` dependency in pyproject.toml

#### Phase 8: Advanced Features

- **Linter Auto-Fix** (`linter/`) - Automatic fixing of lint issues (#73)
  - `fix_code()`: Fix lint issues in source code strings
  - `fix_file()`: Fix lint issues in files with optional write mode
  - `--fix` CLI flag: Apply fixes via `wetwire-gitlab lint --fix`
  - WGL010 auto-fix: Converts `when="manual"` to `when=When.MANUAL` with import
  - LintIssue fields: `original`, `suggestion`, `fix_imports`, `insert_after_line`
- **Additional Lint Rules** (`linter/rules.py`) - 8 new lint rules for GitLab patterns (#73)
  - WGL012: Use CachePolicy constants instead of string literals
  - WGL013: Use ArtifactsWhen constants instead of string literals
  - WGL014: Jobs should have script, trigger, or extends
  - WGL015: Jobs should have explicit name
  - WGL016: Use Image dataclass instead of string literal
  - WGL017: Empty rules list means job never runs
  - WGL018: Jobs with needs should specify stage
  - WGL019: Manual jobs should consider allow_failure
- **Documentation** (`docs/`) - Added adoption and versioning guides (#73)
  - ADOPTION.md: Migration strategies, escape hatches, team onboarding
  - VERSIONING.md: Version types, release workflow, breaking changes policy
- **Linter Refactoring** (`linter/rules/`) - Split rules into categorical modules (#73)
  - type_rules.py: WGL001-WGL006, WGL012, WGL013, WGL016 (typed constants)
  - pattern_rules.py: WGL009, WGL010 (predefined patterns)
  - file_rules.py: WGL007, WGL008 (file-level checks)
  - job_rules.py: WGL011, WGL014-WGL019 (job validation)

#### Phase 3: Command Integration

- **Build Command** (`cli/`) - Full build command implementation: discovers jobs/pipelines, extracts values via runner, generates YAML/JSON output with --format and --output flags (#43)
- **Validate Command** (`cli/`) - Pipeline validation using glab CLI integration with --include-jobs support (#44)
- **Lint Command** (`cli/`) - Python code quality rules with text/JSON output and exit codes (#45)
- **Import Command** (`cli/`) - Convert .gitlab-ci.yml to Python code with code generation, scaffold support, and --single-file/--no-scaffold flags (#46)
- **List Command** (`cli/`) - Display discovered jobs and pipelines with table/JSON output formats (#47)
- **Design Command** (`cli/`) - Stub for AI-assisted design requiring wetwire-core integration (#48)
- **Test Command** (`cli/`) - Stub for persona-based evaluation requiring wetwire-core integration (#48)
- **Graph Command** (`cli/`) - DAG visualization with Mermaid and DOT format output (#48)

#### Phase 7: Feature Completeness

- **CLI Utilities Module** (`cli/cli_utils.py`) - Reusable CLI helper functions (#68)
  - `error_exit()`: Print error with optional hint and return exit code
  - `validate_package_path()`: Validate and resolve package paths
  - `require_optional_dependency()`: Check for optional dependencies
  - `resolve_output_dir()`: Resolve output directory with optional creation
  - `add_common_args()`: Add shared arguments to parsers
  - `print_success()`, `print_warning()`: Formatted output helpers
- **Graph Command Enhancements** (`cli/main.py`, `discover/scanner.py`) - Enhanced DAG visualization (#66)
  - `--params/-p` flag: Include pipeline variables as nodes with different shapes
  - `--cluster/-c` flag: Group jobs by stage in subgraphs
  - Node annotations: Show when condition (manual, always, etc.)
  - Enhanced scanner: Extract stage, variables, and when from Job declarations
- **Additional Linter Rules** (`linter/rules.py`) - 3 new lint rules for GitLab patterns (#65)
  - WGL009: Use predefined Rules constants (Rules.ON_DEFAULT_BRANCH, etc.)
  - WGL010: Use typed When constants (When.MANUAL, etc.)
  - WGL011: Missing stage in Job definitions
- **Init Command** (`cli/init.py`) - Full implementation with package scaffolding (#64)
  - Creates package structure (\_\_init\_\_.py, jobs.py, pipeline.py)
  - Generates README.md, CLAUDE.md, .gitignore by default
  - Supports --force, --verbose, --no-scaffold, --description flags
  - Created packages are immediately buildable

#### Phase 6: Production Readiness

- **wetwire-core Integration** (`agent.py`, `cli/main.py`) - Full integration with wetwire-core for AI-assisted pipeline design and persona-based testing (#54)
  - GitLabRunnerAgent: AI agent with 6 tools (init_package, write_file, read_file, run_lint, run_build, ask_developer)
  - Design command: Interactive pipeline design session with AI assistance
  - Test command: Persona-based evaluation with 5 personas (beginner, intermediate, expert, terse, verbose)
  - Scoring system: 5-dimension evaluation (completeness, lint quality, code quality, output validity, question efficiency)
  - Session results: RESULTS.md output with scoring breakdown
- **Examples Directory** (`examples/`) - 5 complete example projects demonstrating wetwire-gitlab usage: python-app, docker-build, multi-stage, kubernetes-deploy, monorepo (#52)
- **Intrinsics Enhancement** (`intrinsics.py`) - Added PascalCase aliases for CI variables (CI.COMMIT_BRANCH, etc.) and Rules class for predefined rules (#52)
- **Documentation** (`docs/`) - Added QUICK_START.md, CLI.md, LINT_RULES.md, IMPORT_WORKFLOW.md, INTERNALS.md, DEVELOPERS.md and expanded FAQ.md (#53)
- **MCP Server** (`mcp_server.py`) - Model Context Protocol server for AI tool integration with init, lint, build, validate, and import tools (#55)
- **Component Catalog Wrappers** (`components/`) - Typed wrappers for GitLab CI/CD Components: SAST, Secret Detection, Dependency Scanning, Container Scanning, Code Quality, License Scanning, Coverage, Terraform, DAST (#56)

#### Phase 5: Extended Features

- **Auto DevOps Templates** (`templates/`) - Typed wrappers for GitLab Auto DevOps: AutoDevOps, AutoDevOpsConfig dataclasses with to_include() and to_variables() methods (#50)
- **Job Templates** (`templates/`) - Build, Test, Deploy, SAST, DAST template wrappers for Jobs/*.gitlab-ci.yml and Security/*.gitlab-ci.yml includes (#50)
- **Runner Config** (`runner_config/`) - Typed dataclasses for GitLab Runner config.toml: Config, Runner, Executor, DockerConfig, KubernetesConfig, CacheConfig with TOML serialization (#51)

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
