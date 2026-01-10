# Feature Roadmap

This document tracks feature implementation status and planned enhancements for wetwire-gitlab.

---

## Feature Matrix

### Core Features

| Feature | Status | Version | Notes |
|---------|--------|---------|-------|
| **Core Types** | ✅ Complete | 0.1.0 | Job, Pipeline, Rule, Artifacts, Cache, Include, Workflow, Trigger, Variables, Image, Default |
| **Intrinsics** | ✅ Complete | 0.1.0 | CI, GitLab, MR contexts, When/CachePolicy constants |
| **Serialization** | ✅ Complete | 0.1.0 | YAML/JSON output, field name conversion |
| **AST Discovery** | ✅ Complete | 0.1.0 | Find Job/Pipeline in Python source |
| **Dependency Ordering** | ✅ Complete | 0.1.0 | Topological sort, cycle detection |
| **Runtime Extraction** | ✅ Complete | 0.1.0 | Dynamic module import, value extraction |

### CLI Commands

| Command | Status | Version | Notes |
|---------|--------|---------|-------|
| `build` | ✅ Complete | 0.1.0 | Generate .gitlab-ci.yml from Python |
| `validate` | ✅ Complete | 0.1.0 | glab CLI integration |
| `lint` | ✅ Complete | 0.1.0 | 19 lint rules (WGL001-WGL019) |
| `list` | ✅ Complete | 0.1.0 | Display discovered jobs/pipelines |
| `import` | ✅ Complete | 0.1.0 | Convert YAML to Python |
| `init` | ✅ Complete | 0.1.0 | Package scaffolding |
| `graph` | ✅ Complete | 0.1.0 | DAG visualization (Mermaid/DOT) |
| `design` | ✅ Complete | 0.1.0 | AI-assisted pipeline design |
| `test` | ✅ Complete | 0.1.0 | Persona-based evaluation |
| `version` | ✅ Complete | 0.1.0 | Display version information |

### Lint Rules

| Rule | Description | Auto-Fix | Status |
|------|-------------|----------|--------|
| WGL001 | Use typed component wrappers | ❌ | ✅ Complete |
| WGL002 | Use Rule dataclass | ❌ | ✅ Complete |
| WGL003 | Use predefined variables | ✅ | ✅ Complete |
| WGL004 | Use Cache dataclass | ❌ | ✅ Complete |
| WGL005 | Use Artifacts dataclass | ❌ | ✅ Complete |
| WGL006 | Use typed stage constants | ❌ | ✅ Complete |
| WGL007 | Duplicate job names | ❌ | ✅ Complete |
| WGL008 | File too large | ❌ | ✅ Complete |
| WGL009 | Use predefined Rules | ✅ | ✅ Complete |
| WGL010 | Use typed When constants | ✅ | ✅ Complete |
| WGL011 | Missing stage in Job | ❌ | ✅ Complete |
| WGL012 | Use CachePolicy constants | ✅ | ✅ Complete |
| WGL013 | Use ArtifactsWhen constants | ✅ | ✅ Complete |
| WGL014 | Missing script in Job | ❌ | ✅ Complete |
| WGL015 | Missing name in Job | ❌ | ✅ Complete |
| WGL016 | Use Image dataclass | ❌ | ✅ Complete |
| WGL017 | Empty rules list | ❌ | ✅ Complete |
| WGL018 | Needs without stage | ❌ | ✅ Complete |
| WGL019 | Manual without allow_failure | ❌ | ✅ Complete |

### Templates and Components

| Feature | Status | Version | Notes |
|---------|--------|---------|-------|
| **Auto DevOps** | ✅ Complete | 0.1.0 | AutoDevOps, AutoDevOpsConfig wrappers |
| **Job Templates** | ✅ Complete | 0.1.0 | Build, Test, Deploy, SAST, DAST |
| **Component Catalog** | ✅ Complete | 0.1.0 | 9 security/quality components |
| **Runner Config** | ✅ Complete | 0.1.0 | config.toml generation |

### AI Integration

| Feature | Status | Version | Provider | Notes |
|---------|--------|---------|----------|-------|
| **Design Command** | ✅ Complete | 0.1.0 | Anthropic | Interactive pipeline design |
| **Design Command** | ✅ Complete | 0.1.0 | Kiro | Alternative CLI provider |
| **Test Command** | ✅ Complete | 0.1.0 | Anthropic | Persona-based evaluation |
| **Test Command** | ✅ Complete | 0.1.0 | Kiro | Alternative CLI provider |
| **MCP Server** | ✅ Complete | 0.1.0 | - | Model Context Protocol tools |
| **GitLabRunnerAgent** | ✅ Complete | 0.1.0 | - | 6 agent tools |

### Documentation

| Document | Status | Version | Notes |
|----------|--------|---------|-------|
| README.md | ✅ Complete | 0.1.0 | Project overview |
| CLAUDE.md | ✅ Complete | 0.1.0 | AI assistant context |
| CHANGELOG.md | ✅ Complete | 0.1.0 | Release history |
| QUICK_START.md | ✅ Complete | 0.1.0 | Getting started guide |
| CLI.md | ✅ Complete | 0.1.0 | Comprehensive CLI reference |
| LINT_RULES.md | ✅ Complete | 0.1.0 | Detailed rule documentation |
| IMPORT_WORKFLOW.md | ✅ Complete | 0.1.0 | YAML conversion guide |
| INTERNALS.md | ✅ Complete | 0.1.0 | Architecture documentation |
| DEVELOPERS.md | ✅ Complete | 0.1.0 | Development workflow |
| FAQ.md | ✅ Complete | 0.1.0 | Frequently asked questions |
| ADOPTION.md | ✅ Complete | 0.1.0 | Migration strategies |
| VERSIONING.md | ✅ Complete | 0.1.0 | Version management |
| EXAMPLES.md | ✅ Complete | 0.1.0 | Example projects documentation |
| GITLAB_COMPONENTS.md | ✅ Complete | 0.1.0 | Security scanning components |
| RUNNER_CONFIG.md | ✅ Complete | 0.1.0 | Runner configuration |
| AUTO_DEVOPS.md | ✅ Complete | 0.1.0 | Auto DevOps templates |
| MCP_SERVER.md | ✅ Complete | 0.1.0 | MCP server integration |
| PLAN.md | ✅ Complete | 0.1.0 | Development plan |
| ROADMAP.md | ✅ Complete | 0.1.0 | This document |

### Examples

| Example | Status | Version | Description |
|---------|--------|---------|-------------|
| python-app | ✅ Complete | 0.1.0 | Basic Python CI/CD with multi-version testing |
| docker-build | ✅ Complete | 0.1.0 | Docker build & push with registry integration |
| multi-stage | ✅ Complete | 0.1.0 | Complex DAG pipeline with environments |
| kubernetes-deploy | ✅ Complete | 0.1.0 | Helm-based multi-environment deployment |
| monorepo | ✅ Complete | 0.1.0 | Dynamic child pipelines with change detection |

### Testing

| Feature | Status | Version | Coverage | Notes |
|---------|--------|---------|----------|-------|
| **Unit Tests** | ✅ Complete | 0.1.0 | 78% | 814 tests total |
| **CLI Tests** | ✅ Complete | 0.1.0 | High | 12 test files |
| **Linter Tests** | ✅ Complete | 0.1.0 | 93% | All rules covered |
| **Pipeline Tests** | ✅ Complete | 0.1.0 | High | Core type tests |
| **Integration Tests** | ✅ Complete | 0.1.0 | High | 7 test files |
| **Component Tests** | ✅ Complete | 0.1.0 | 100% | Wrapper validation |
| **Runner Tests** | ✅ Complete | 0.1.0 | 91% | Loader coverage |
| **Codegen Tests** | ✅ Complete | 0.1.0 | 100% | Full coverage |

---

## Completed Phases

### Phase 11: Quality Improvements (Complete)

| Feature | Status | Issue | Priority |
|---------|--------|-------|----------|
| CLI Refactoring | ✅ Complete | #94 | High |
| Planning Documents | ✅ Complete | #95 | High |
| QUICK_START Expansion | ✅ Complete | #96 | Medium |
| Lint Auto-Fix Expansion | ✅ Complete | #97 | Medium |
| Template Reference Testing | ✅ Complete | #98 | Medium |
| Wetwire Spec Links | ✅ Complete | #99 | Low |

### Phase 12: Feature Expansion (Complete)

| Feature | Status | Issue | Priority |
|---------|--------|-------|----------|
| Development Scripts | ✅ Complete | #100 | High |
| Auto-Fix Expansion | ✅ Complete | #101 | Medium |
| Semantic Equivalence Testing | ✅ Complete | #102 | Medium |
| Diff Command | ✅ Complete | #106 | Medium |
| Watch Mode | ✅ Complete | #107 | Medium |

---

## Future Enhancements (Under Consideration)

These features are not yet scheduled but may be added based on community feedback:

| Feature | Priority | Notes |
|---------|----------|-------|
| **Schema Validation** | Medium | Validate against GitLab CI JSON schema |
| **VS Code Extension** | Low | IDE support for syntax highlighting |
| **Interactive Mode** | Low | CLI wizard for job creation |
| **GitLab 17.x Features** | Medium | Support latest GitLab features |
| **Additional Lint Rules** | Medium | Expand beyond WGL001-WGL019 |
| **Performance Optimization** | Low | Faster discovery for large codebases |

---

## Breaking Changes Policy

wetwire-gitlab follows [Semantic Versioning](https://semver.org/):

- **MAJOR** (X.0.0): Breaking API changes
- **MINOR** (0.Y.0): New features, backwards compatible
- **PATCH** (0.0.Z): Bug fixes, backwards compatible

### What Constitutes a Breaking Change

- Removing public API functions or classes
- Changing function signatures
- Changing generated YAML structure
- Removing lint rules
- Changing default behavior

### Deprecation Process

1. **Deprecation warning** in previous minor release
2. **Migration guide** in release notes
3. **Major version bump** when removing deprecated features

### Non-Breaking Changes

- Adding new features (minor version bump)
- Adding new lint rules (minor version bump)
- Adding new intrinsics (minor version bump)
- Bug fixes (patch version bump)
- Documentation updates (no version bump)

---

## Version Timeline

| Version | Status | Release Date | Highlights |
|---------|--------|--------------|------------|
| 0.1.0 | 🔄 In Development | TBD | Initial release with all Phase 1-11 features |
| 0.2.0 | 📋 Planned | TBD | TBD based on community feedback |

---

## Component Support Matrix

### GitLab CI/CD Components

| Component | Type | Status | Version |
|-----------|------|--------|---------|
| SAST | Security | ✅ Complete | 0.1.0 |
| Secret Detection | Security | ✅ Complete | 0.1.0 |
| Dependency Scanning | Security | ✅ Complete | 0.1.0 |
| Container Scanning | Security | ✅ Complete | 0.1.0 |
| DAST | Security | ✅ Complete | 0.1.0 |
| License Scanning | Compliance | ✅ Complete | 0.1.0 |
| Code Quality | Quality | ✅ Complete | 0.1.0 |
| Coverage | Quality | ✅ Complete | 0.1.0 |
| Terraform | Infrastructure | ✅ Complete | 0.1.0 |

### GitLab Runner Executors

| Executor | Status | Version | Notes |
|----------|--------|---------|-------|
| Docker | ✅ Complete | 0.1.0 | Full DockerConfig support |
| Kubernetes | ✅ Complete | 0.1.0 | Full KubernetesConfig support |
| Shell | ✅ Complete | 0.1.0 | Basic executor config |
| SSH | ✅ Complete | 0.1.0 | Basic executor config |
| VirtualBox | ✅ Complete | 0.1.0 | Basic executor config |
| Parallels | ✅ Complete | 0.1.0 | Basic executor config |
| Custom | ✅ Complete | 0.1.0 | Basic executor config |

### Cache Backends

| Backend | Status | Version | Notes |
|---------|--------|---------|-------|
| S3 | ✅ Complete | 0.1.0 | AWS S3-compatible storage |
| GCS | ✅ Complete | 0.1.0 | Google Cloud Storage |
| Azure | ✅ Complete | 0.1.0 | Azure Blob Storage |
| Local | ✅ Complete | 0.1.0 | Local filesystem cache |

---

## GitLab Version Compatibility

wetwire-gitlab generates YAML compatible with:

| GitLab Version | Status | Notes |
|----------------|--------|-------|
| 13.x | ✅ Supported | Rules keyword, needs |
| 14.x | ✅ Supported | Resource groups, release |
| 15.x | ✅ Supported | Workflow rules, inputs |
| 16.x | ✅ Supported | Component catalog |
| 17.x | ✅ Supported | Latest CI/CD enhancements |

---

## Python Version Support

| Python Version | Status | Notes |
|----------------|--------|-------|
| 3.11 | ✅ Supported | Minimum version |
| 3.12 | ✅ Supported | Tested in CI |
| 3.13 | ✅ Supported | Tested in CI |
| 3.14+ | 🔄 Planned | Will support when available |

---

## Dependencies

### Required

| Package | Version | Purpose |
|---------|---------|---------|
| pyyaml | >=6.0 | YAML parsing and serialization |
| jinja2 | >=3.0 | Template-based code generation |

### Optional

| Package | Version | Purpose |
|---------|---------|---------|
| wetwire-core | Latest | AI-assisted design/test (anthropic) |
| kiro-cli | Latest | Alternative AI provider |
| glab | Latest | GitLab CLI for validation |

---

## Contributing

To propose new features or enhancements:

1. Check existing [GitHub Issues](https://github.com/lex00/wetwire-gitlab-python/issues)
2. Open a discussion or issue describing the feature
3. Wait for maintainer feedback before starting work
4. Follow the [Developer Guide](DEVELOPERS.md)

---

## See Also

- [PLAN.md](PLAN.md) - Current development phase and priorities
- [CHANGELOG.md](../CHANGELOG.md) - Detailed release history
- [VERSIONING.md](VERSIONING.md) - Version management policy
- [ADOPTION.md](ADOPTION.md) - Migration strategies
