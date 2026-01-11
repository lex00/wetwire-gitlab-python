# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

#### Kiro Module Refactoring

- **Kiro Module** (`kiro/`) - Refactored to use wetwire-core's centralized Kiro integration (#143)
  - Removed `agent_config.json` (unused - config was embedded in Python)
  - Removed `installer.py` (624 lines) that duplicated wetwire-core functionality
  - Added `config.py` with `GITLAB_KIRO_CONFIG` using `KiroConfig` from wetwire-core
  - Updated `__init__.py` to re-export core functions (`KiroConfig`, `launch_kiro`, etc.)
  - Maintained backwards compatibility with `install_kiro_configs()` wrapper
  - Net code reduction: ~400 lines

### Added

#### README Badges

- **README.md** - Add standard README badges per spec 12.4 (#146)
  - CI status badge linking to GitHub Actions workflow
  - PyPI version badge linking to package
  - Python 3.11+ version badge
  - MIT license badge
  - Codecov coverage badge

#### Coverage Reporting in CI

- **CI workflow** (`.github/workflows/ci.yml`) - Add coverage reporting per spec 11.7 (#136)
  - Run tests with coverage reporting (XML and terminal output)
  - Upload coverage to Codecov for Python 3.12 builds
  - Coverage metrics visible in CI output

#### CODEGEN.md Documentation

- **CODEGEN.md** (`docs/CODEGEN.md`) - Document code generation pipeline (#135)
  - Explains all six pipeline stages (Discover, Validate, Extract, Order, Serialize, Emit)
  - Details AST-based discovery process
  - Documents serialization rules and field mappings
  - Includes error handling and performance considerations

#### Imported GitLab CI Examples

- **examples/imported/** (`examples/imported/`) - Import official GitLab CI templates (#134)
  - Python, Node.js, and Rust official GitLab CI templates
  - Round-trip testing verifies import and build work correctly
  - README with proper attribution to gitlab-org/gitlab

#### Kiro Agent Configuration

- **agent_config.json** (`kiro/agent_config.json`) - Add standalone agent config for Kiro CLI (#133)
  - Includes GitLab CI syntax patterns and examples
  - Documents lint rules WGL001-WGL025
  - Defines design workflow for AI-assisted pipeline creation
  - Compatible with Kiro CLI agent discovery

#### Secret Pattern Detection (WGL025)

- **WGL025** (`linter/rules/job_rules.py`) - Detect hardcoded secrets in job definitions (#132)
  - Scans script commands and variable values for common secret patterns
  - Detects AWS keys (AKIA...), private key headers, GitLab/GitHub tokens
  - Detects Stripe API keys, Slack webhooks, generic API keys and passwords
  - 10+ pattern matchers for comprehensive coverage

#### Circular Dependency Detection (WGL024)

- **WGL024** (`linter/rules/job_rules.py`) - Detect circular dependencies in job needs (#131)
  - Uses DFS with recursion stack for cycle detection
  - Supports both string and Job variable references in needs
  - Reports normalized cycles with job names and file locations
  - Handles self-references (A -> A) and multi-job cycles (A -> B -> C -> A)

#### Build Manifest Tracking

- **Build Manifest** (`cli/commands/build.py`) - Track build pipeline stages per WETWIRE_SPEC.md section 8.4 (#129)
  - New `--manifest` flag for build command
  - Generates `manifest.json` alongside `.gitlab-ci.yml` output
  - Tracks: version, timestamp, source files with SHA256 hashes, discovered jobs, dependencies
  - New `BuildManifest` dataclass in contracts module
  - `create_manifest()` utility function for programmatic use
  - Supports incremental builds via source file hash tracking

#### Phase 14: Developer Tooling

- **Optional wetwire-core** (`pyproject.toml`) - Core CLI commands work without wetwire-core (#122)
  - Moved wetwire-core to `[agent]` optional dependency
  - Only `design` and `test` commands require it
  - Try/except imports with helpful error messages
  - New test file for optional dependency verification

- **Pre-commit Hooks** (`.pre-commit-config.yaml`) - Automated code quality checks (#123)
  - Ruff linter with auto-fix
  - Ruff formatter
  - YAML validation
  - Trailing whitespace and EOF fixes
  - Large file detection (1MB limit)

- **Type Checking** (`pyrightconfig.json`) - Static type analysis (#124)
  - Pyright configuration for Python 3.11+
  - types-PyYAML type stubs added to dev dependencies
  - Standard type checking mode

- **Pytest Slow Marker** (`pyproject.toml`) - Fast test iteration (#125)
  - New `@pytest.mark.slow` for integration tests
  - 749 fast tests, 281 slow tests (1030 total)
  - Run fast tests: `pytest -m "not slow"`
  - Updated docs/DEVELOPERS.md with usage

- **Graphviz Optional** (`pyproject.toml`) - Optional DOT output (#126)
  - New `[graph]` optional dependency
  - graphviz>=0.20 for DOT format output

#### Phase 12E: Watch Mode

- **Watch Mode** (`cli/commands/build.py`) - Auto-rebuild on file changes (#107)
  - New `--watch` flag for build command
  - Uses watchdog library for file monitoring
  - Debounces rapid changes (0.5s delay)
  - Shows timestamps and clear separators
  - Handles errors gracefully without crashing
  - Optional dependency: `pip install wetwire-gitlab[watch]`
  - 5 new tests (814 total tests)

#### Phase 12D: Diff Command

- **Diff Command** (`cli/commands/diff.py`) - Compare generated YAML with existing (#106)
  - New `wetwire-gitlab diff` command
  - Unified and context diff formats
  - Semantic comparison option (--semantic)
  - Color-coded output for additions/deletions
  - Exit codes: 0=identical, 1=different, 2=error
  - 16 new tests (809 total tests)

#### Phase 12C: Semantic Equivalence Testing

- **Semantic Equivalence Testing** (`testing/`) - Added round-trip validation (#102)
  - New `compare_yaml_semantic()` function for YAML comparison
  - Compares YAML structure ignoring whitespace, ordering, quote style
  - Added `to_pipeline()` and `to_job()` methods to IR classes
  - Extended Pipeline to support top-level cache and services
  - 27 new tests for semantic equivalence (793 total tests)
  - Per WETWIRE_SPEC.md Section 11.1 requirement

#### Phase 12B: Auto-Fix Expansion

- **Auto-Fix Expansion** (`linter/rules/`) - Added auto-fix support for more rules (#101)
  - WGL003: Auto-fix raw CI variable strings → intrinsic constants
  - WGL009: Auto-fix common rule patterns → Rules constants
  - Now 5 rules support auto-fix (WGL003, WGL009, WGL010, WGL012, WGL013)
  - Added 8 new auto-fix tests (766 total tests)
  - Updated LINT_RULES.md with auto-fix indicators

#### Phase 12A: Development Scripts

- **Development Scripts** (`scripts/`) - Added automation scripts for development (#100)
  - dev-setup.sh: Automated environment setup (venv + dependencies)
  - ci.sh: Run full CI workflow locally (lint + tests + coverage)
  - check-types.sh: Run type checker on source code
  - Updated DEVELOPERS.md with script documentation and quick start

#### Phase 10C: Loader and Codegen Coverage

- **Loader and Codegen Coverage** (`tests/`) - Improved test coverage (#90)
  - runner/loader.py: 76% → 91% (+15%)
  - importer/codegen.py: 75% → 100% (+25%)
  - Added 52 new tests (719 total)
  - Overall project coverage: 76% → 77%
  - Test module extraction, path resolution, TOML parsing
  - Test all code generation edge cases

#### Phase 10B: Runner Config Coverage

- **Runner Config Module Coverage** (`tests/components/`) - Improved test coverage (#90)
  - runner_config/config.py: 80% → 94% (+14%)
  - All other runner_config modules: 100%
  - Added 12 new tests (667 total)
  - Overall project coverage: 74% → 76%
  - Test GCS cache serialization and TOML parsing

#### Phase 10A: Test Coverage Improvements

- **Core Module Coverage** (`tests/`) - Improved test coverage for core modules (#90)
  - linter/linter.py: 79% → 93% (+14%)
  - discover/scanner.py: 84% → 99% (+15%)
  - Added 31 new tests (655 total)
  - Test edge cases: syntax errors, unknown rules, directory skipping
  - Test helper functions and module-prefixed calls

#### Phase 9E: CLI Documentation

- **CLI.md Expansion** (`docs/CLI.md`) - Comprehensive CLI reference (#83)
  - Quick reference table for all 9 commands
  - Detailed command documentation with examples
  - Provider documentation (anthropic/kiro)
  - Typical workflow section (dev, CI/CD, migration, team)
  - Dependencies and troubleshooting sections
  - Expanded from ~253 to ~950 lines

#### Phase 9D: Test Reorganization

- **Test Directory Structure** (`tests/`) - Reorganized tests into subdirectories (#82)
  - cli/: Command-line interface tests (11 files)
  - linter/: Linter rule tests (3 files)
  - importer/: YAML import tests (1 file)
  - codegen/: Code generation tests (3 files)
  - pipeline/: Core type tests (5 files)
  - discover/: AST discovery tests (1 file)
  - components/: Component wrapper tests (3 files)
  - runner/: Runner loader tests (1 file)
  - integration/: Integration and example tests (7 files)

#### Phase 9C: Domain-Specific Documentation

- **Domain Documentation** (`docs/`) - GitLab-specific feature guides (#81)
  - GITLAB_COMPONENTS.md: Security scanning components (SAST, DAST, etc.)
  - RUNNER_CONFIG.md: GitLab Runner config.toml generation
  - AUTO_DEVOPS.md: Auto DevOps template configuration
  - MCP_SERVER.md: MCP server tools and integration

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
