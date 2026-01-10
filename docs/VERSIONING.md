# Versioning

This document explains the versioning system for wetwire-gitlab.

## Version Types

The project maintains **two independent version streams**:

| Version | Format | Purpose |
|---------|--------|---------|
| **Package Version** | Semantic (X.Y.Z) | PyPI releases, API changes |
| **GitLab CI Schema** | GitLab version | Track GitLab CI/CD feature support |

### Package Version

The main version for PyPI releases. Follows [Semantic Versioning](https://semver.org/):

- **MAJOR** (X): Breaking API changes
- **MINOR** (Y): New features, backwards compatible
- **PATCH** (Z): Bug fixes, backwards compatible

**Location:** `pyproject.toml`

### GitLab CI Schema Version

Tracks which GitLab CI/CD features are supported.

**Source:** Based on GitLab release documentation and JSON schema.

**Format:** GitLab version (e.g., `17.0`)

---

## Bumping the Package Version

When releasing a new version:

1. Update `pyproject.toml`:
   ```toml
   [project]
   version = "0.2.0"
   ```

2. Update version in `src/wetwire_gitlab/__init__.py`:
   ```python
   __version__ = "0.2.0"
   ```

3. Update CHANGELOG.md with release notes

4. Run tests:
   ```bash
   uv run pytest tests/
   ```

5. Commit and tag:
   ```bash
   git commit -am "Bump version to 0.2.0"
   git tag v0.2.0
   git push && git push --tags
   ```

---

## Viewing Current Versions

### From Python

```python
from wetwire_gitlab import __version__
print(__version__)  # "0.1.0"
```

### From CLI

```bash
wetwire-gitlab version
```

---

## GitLab CI Feature Support

wetwire-gitlab tracks GitLab CI/CD features by version:

| GitLab Version | Features Added |
|----------------|----------------|
| 13.0+ | Rules keyword, needs |
| 14.0+ | Resource groups, release |
| 15.0+ | Workflow rules, inputs |
| 16.0+ | Component catalog |
| 17.0+ | CI/CD catalog enhancements |

### Checking Feature Support

The library validates configurations against supported features. If you use a feature from a newer GitLab version:

```python
# Component catalog requires GitLab 16.0+
include = Include(component="gitlab.com/my-org/component@1.0")
```

The linter will warn if features require specific GitLab versions.

---

## Release Workflow

### Pre-release Checklist

1. All tests pass: `uv run pytest`
2. Linter passes: `uv run ruff check src/ tests/`
3. Type checker passes: `uv run ty check src/`
4. Documentation is updated
5. CHANGELOG.md has release notes

### Creating a Release

1. Update version numbers (see above)
2. Create PR with version bump
3. Merge PR
4. Tag the release
5. GitHub Actions publishes to PyPI

### Hotfix Process

For urgent fixes:

1. Create hotfix branch from tag: `git checkout -b hotfix/0.1.1 v0.1.0`
2. Apply fix
3. Bump patch version
4. Merge and tag

---

## Dependency Versioning

### Runtime Dependencies

```toml
[project]
dependencies = [
    "pyyaml>=6.0",
    "jinja2>=3.0",
]
```

Dependencies use minimum version constraints for compatibility.

### Development Dependencies

```toml
[project.optional-dependencies]
dev = [
    "pytest>=9.0",
    "ruff>=0.11",
]
```

Development dependencies pin to known-working versions.

---

## Breaking Changes Policy

### What Constitutes a Breaking Change

- Removing public API functions or classes
- Changing function signatures
- Changing generated YAML structure
- Removing lint rules

### Handling Breaking Changes

1. Deprecation warning in previous minor release
2. Migration guide in release notes
3. Major version bump

### Non-Breaking Changes

- Adding new features
- Adding new lint rules
- Adding new intrinsics
- Bug fixes

---

## See Also

- [Developer Guide](DEVELOPERS.md) - Full development guide
- [Internals](INTERNALS.md) - Architecture details
