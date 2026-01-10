# Development Plan

This document outlines the current development phase, recently completed work, and upcoming priorities for wetwire-gitlab.

---

## Current Phase

**Phase 11: Quality Improvements** (In Progress)

Focus on code quality, documentation completeness, and developer experience improvements. This phase emphasizes polish, maintainability, and making the project more accessible to new contributors.

---

## Recently Completed

### Phase 10: Test Coverage Improvements (Complete)

Comprehensive test coverage improvements across core modules:

- **Phase 10C**: Loader and Codegen Coverage (#90)
  - runner/loader.py: 76% → 91% coverage
  - importer/codegen.py: 75% → 100% coverage
  - Added 52 new tests (719 total)
  - Overall project coverage: 76% → 77%

- **Phase 10B**: Runner Config Coverage (#90)
  - runner_config/config.py: 80% → 94% coverage
  - All other runner_config modules: 100%
  - Added 12 new tests (667 total)

- **Phase 10A**: Core Module Coverage (#90)
  - linter/linter.py: 79% → 93% coverage
  - discover/scanner.py: 84% → 99% coverage
  - Added 31 new tests (655 total)

### Phase 9: Documentation and Organization (Complete)

Comprehensive documentation expansion and test reorganization:

- **Phase 9E**: CLI Documentation (#83)
  - Expanded CLI.md from ~253 to ~950 lines
  - Quick reference table for all 9 commands
  - Detailed examples and troubleshooting

- **Phase 9D**: Test Reorganization (#82)
  - Organized tests into 8 subdirectories
  - Improved test discoverability and maintenance

- **Phase 9C**: Domain-Specific Documentation (#81)
  - GITLAB_COMPONENTS.md: Security scanning components
  - RUNNER_CONFIG.md: Runner config.toml generation
  - AUTO_DEVOPS.md: Auto DevOps templates
  - MCP_SERVER.md: MCP server tools

- **Phase 9B**: Examples Documentation (#80)
  - Documented all 5 example projects
  - Added pattern reference table

- **Phase 9A**: Job Reference Support (#79)
  - Support Job instances in needs/dependencies
  - Type-safe job references

### Phase 8: Advanced Features (Complete)

Linter enhancements and organizational improvements:

- **Linter Auto-Fix** (#73)
  - `--fix` CLI flag for automatic issue resolution
  - WGL010 auto-fix: String literals → typed When constants
  - Fix infrastructure for future rules

- **Additional Lint Rules** (#73)
  - WGL012-WGL019: 8 new lint rules
  - Coverage for cache policies, artifacts, job validation

- **Documentation** (#73)
  - ADOPTION.md: Migration strategies and team onboarding
  - VERSIONING.md: Version management and release workflow

- **Linter Refactoring** (#73)
  - Split rules into categorical modules
  - type_rules.py, pattern_rules.py, file_rules.py, job_rules.py

### Phase 7: Feature Completeness (Complete)

CLI utilities and advanced graph features:

- **CLI Utilities Module** (#68)
  - Reusable helper functions for all commands
  - Error handling, validation, output formatting

- **Graph Command Enhancements** (#66)
  - Pipeline variable visualization
  - Stage clustering
  - Node annotations for manual/conditional jobs

- **Additional Linter Rules** (#65)
  - WGL009-WGL011: Predefined Rules, When constants, missing stage

- **Init Command** (#64)
  - Full package scaffolding
  - Immediate buildability

### Phase 6: Production Readiness (Complete)

AI integration and comprehensive documentation:

- **wetwire-core Integration** (#54)
  - GitLabRunnerAgent with 6 tools
  - Design and test commands
  - Persona-based evaluation

- **Examples Directory** (#52)
  - 5 complete example projects
  - Real-world patterns

- **Intrinsics Enhancement** (#52)
  - PascalCase aliases for CI variables
  - Rules class for predefined rules

- **Documentation** (#53)
  - QUICK_START.md, CLI.md, LINT_RULES.md
  - IMPORT_WORKFLOW.md, INTERNALS.md, DEVELOPERS.md
  - Expanded FAQ.md

- **MCP Server** (#55)
  - Model Context Protocol server
  - AI tool integration

- **Component Catalog Wrappers** (#56)
  - Typed wrappers for 9 GitLab components
  - SAST, Secret Detection, etc.

### Phase 5: Extended Features (Complete)

Templates and runner configuration:

- **Auto DevOps Templates** (#50)
  - Typed wrappers for Auto DevOps
  - to_include() and to_variables() methods

- **Job Templates** (#50)
  - Build, Test, Deploy, SAST, DAST wrappers

- **Runner Config** (#51)
  - Typed dataclasses for config.toml
  - TOML serialization

### Phases 1-4: Foundation (Complete)

Core architecture and implementation:

- **Phase 4**: Reference example testing (#49)
- **Phase 3**: All 9 CLI commands (#43-#48)
- **Phase 2**: Template builder, runner, parser, linter, validation, discovery (#37-#42)
- **Phase 1**: Foundation - schema fetching, CLI framework, serialization, core types (#31-#34)

### Phase 11: Quality Improvements (Complete)

All Phase 11 issues (#94-#99) completed:
- **Phase 11A**: CLI modular refactoring (#94)
- **Phase 11B**: Planning documents (#95)
- **Phase 11C**: Documentation expansion (#96)
- **Phase 11D**: Lint auto-fix expansion (#97)
- **Phase 11E**: GitLab template reference testing (#98)
- **Phase 11F**: Wetwire spec links (#99)

---

## Current Phase

**Phase 12: Feature Expansion** (In Progress)

Focus on adding new capabilities and improving developer experience.

### Phase 12 Completed

**Phase 12A: Development Scripts** (#100)
- scripts/dev-setup.sh, ci.sh, check-types.sh
- Developer automation for setup and CI

**Phase 12B: Auto-Fix Expansion** (#101)
- WGL003, WGL009 auto-fix support
- Now 5 rules support auto-fix

**Phase 12C: Semantic Equivalence Testing** (#102)
- compare_yaml_semantic() function
- Round-trip validation per WETWIRE_SPEC.md

**Phase 12D: Diff Command** (#106)
- New `wetwire-gitlab diff` command
- Compare generated YAML with existing

### Phase 12 In Progress

**Phase 12E: Watch Mode** (#107)
- Auto-rebuild on file changes
- --watch flag for build command

---

## Known Limitations

### Coverage Gaps

While overall coverage is 78%, some modules have lower coverage:
- Certain edge cases in serialization
- Complex graph scenarios
- Error handling paths

**Strategy**: Address opportunistically when working in these areas.

### Auto-Fix Support

Currently only WGL010 supports auto-fix. Many rules could benefit from automatic fixes:
- WGL001: Component wrapper conversion
- WGL002: Rule dataclass conversion
- WGL003: Variable intrinsic conversion

**Strategy**: Expand incrementally through Phase 11D.

### GitLab Feature Coverage

Some newer GitLab CI/CD features may not have typed wrappers:
- New component catalog features (GitLab 17.x)
- Advanced workflow syntax
- Emerging security scanning options

**Strategy**: Use escape hatches (raw dicts) until typed support is added. File issues for commonly-needed features.

### Platform Limitations

- Kiro provider is optional and requires CLI installation
- glab CLI required for validate command
- wetwire-core required for anthropic provider

**Strategy**: Clear error messages with installation hints. All dependencies are optional except pyyaml/jinja2.

---

## Design Principles

These principles guide all development decisions:

1. **Typed over Dynamic**: Use dataclasses and type hints, not raw dictionaries
2. **Discoverable**: Jobs and pipelines found via AST scanning, not imports
3. **Composable**: Small, focused components that combine naturally
4. **Escape Hatches**: When typing doesn't fit, allow raw passthrough
5. **GitLab Native**: Generated YAML works with standard GitLab runners
6. **Incremental Adoption**: New features don't break existing code

---

## Contributing

To contribute to upcoming Phase 11 work:

1. Check the [GitHub Issues](https://github.com/lex00/wetwire-gitlab-python/issues)
2. Comment on the issue you'd like to work on
3. Follow the [Developer Guide](DEVELOPERS.md)
4. Submit a PR with tests and documentation

---

## See Also

- [ROADMAP.md](ROADMAP.md) - Feature implementation status
- [CHANGELOG.md](../CHANGELOG.md) - Detailed release history
- [VERSIONING.md](VERSIONING.md) - Version management policy
- [DEVELOPERS.md](DEVELOPERS.md) - Development workflow
