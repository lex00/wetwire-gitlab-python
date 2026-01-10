# Adoption Guide

Practical guidance for teams adopting wetwire-gitlab alongside existing CI/CD infrastructure.

---

## Migration Strategies

### Side-by-Side Adoption

You don't need to migrate everything at once. wetwire-gitlab generates standard `.gitlab-ci.yml` files that work with the same GitLab runner infrastructure you already use.

**Coexistence patterns:**

| Existing Setup | Integration Approach |
|----------------|---------------------|
| Raw YAML | Keep existing `.gitlab-ci.yml` as-is; gradually add Python-defined jobs |
| Include templates | Python-generated YAML can include existing templates |
| Dynamic pipelines | Use Python for child pipeline generation |

### Incremental Migration Path

**Week 1: Proof of concept**
- Pick a simple job (linting, unit tests)
- Write it in Python using wetwire-gitlab
- Verify the generated YAML output
- Deploy to a test branch

**Week 2-4: Build confidence**
- Convert 2-3 more jobs
- Establish team patterns (file organization, naming conventions)
- Set up CI/CD that builds from Python

**Ongoing: New jobs in Python**
- All new CI/CD logic uses wetwire-gitlab
- Migrate legacy jobs opportunistically (when you're touching them anyway)

### What NOT to Migrate

Some configurations are better left alone:
- **Stable, rarely-changed pipelines** that work fine as-is
- **Pipelines managed by other teams** (coordinate first)
- **Auto DevOps configurations** (GitLab manages these)

Migration should reduce maintenance burden, not create it.

---

## Escape Hatches

When you hit an edge case the library doesn't handle cleanly.

### Raw Dictionary Passthrough

For properties not yet typed, pass raw dictionaries:

```python
job = Job(
    name="custom",
    stage="build",
    script=["make build"],
    # Raw passthrough for custom properties
    services=[{"name": "docker:dind", "alias": "docker"}],
)
```

The serializer passes dictionaries through unchanged.

### String Values

For edge cases where you need raw GitLab CI syntax:

```python
job = Job(
    name="deploy",
    stage="deploy",
    script=["deploy.sh"],
    # Raw string for complex expressions
    environment={"name": "production", "url": "$DEPLOY_URL"},
)
```

### Include External Templates

Mix Python-generated jobs with external templates:

```python
pipeline = Pipeline(
    stages=["build", "test", "deploy"],
    include=[
        Include(template="Jobs/SAST.gitlab-ci.yml"),
        Include(local="common/shared.yml"),
    ],
)
```

### When to Use Escape Hatches

| Situation | Approach |
|-----------|----------|
| New GitLab CI feature | Raw dict passthrough |
| Complex expressions | String values |
| Existing templates | Include directive |
| One-off requirement | Whatever works, with a comment |

### When to File an Issue

If you're using escape hatches for:
- Common job configurations
- Standard GitLab CI features
- Patterns other teams would need

...file an issue. The library should handle it.

---

## Team Onboarding

A playbook for getting your team productive in the first week.

### Day 1: Environment Setup

```bash
# Clone your repo
git clone <repo>
cd <repo>

# Install dependencies
uv sync

# Verify it works
uv run wetwire-gitlab list && echo "OK"
```

**What to check:**
- Python 3.11+ installed
- uv or pip available
- GitLab CI/CD pipeline permissions (for deployment)

### Day 1-2: Read the Code

Start with a simple job file:
```python
from wetwire_gitlab.pipeline import *

build = Job(
    name="build",
    stage="build",
    script=["make build"],
)
```

That's the pattern. Every job looks like this.

### Day 2-3: Make a Small Change

Find something low-risk:
- Change a script command
- Add a variable
- Modify a rule condition

```python
# Before
build = Job(
    name="build",
    stage="build",
    script=["make build"],
)

# After
build = Job(
    name="build",
    stage="build",
    script=["make build"],
    variables={"DEBUG": "true"},
)
```

Run `wetwire-gitlab build`, diff the output, push to a test branch.

### Day 3-4: Add a New Job

Create a new job:

```python
from wetwire_gitlab.pipeline import *, Artifacts

test = Job(
    name="unit-tests",
    stage="test",
    script=["pytest tests/"],
    artifacts=Artifacts(
        paths=["coverage.xml"],
        reports={"coverage_report": {"coverage_format": "cobertura", "path": "coverage.xml"}},
    ),
)
```

Jobs auto-register when discovered by the scanner.

### Day 5: Review the Patterns

By now you've seen:
- Jobs defined as `Job(...)` instances
- Artifacts, Cache, Rules as typed dataclasses
- Intrinsics like `CI.COMMIT_BRANCH`, `When.MANUAL`
- Variables defined with `Variables` dataclass or dict

That's 90% of what you need.

### Common Gotchas

| Problem | Solution |
|---------|----------|
| "Job not in output" | Ensure file is in the package path being scanned |
| "Wrong YAML format" | Check the serializer output with `wetwire-gitlab build --format yaml` |
| "Variable not expanding" | Use f-strings with CI intrinsics |

### Team Conventions to Establish

Decide these early:
- **File organization**: By stage (build.py, test.py, deploy.py) or by feature?
- **Naming**: snake_case for jobs? kebab-case?
- **Rules**: Use predefined `Rules.ON_DEFAULT_BRANCH` or custom?

Document in your repo's README.

### Resources

- [Quick Start](QUICK_START.md) - 5-minute intro
- [CLI Reference](CLI.md) - Build, lint, and validate commands
- [Lint Rules](LINT_RULES.md) - Code quality rules

---

## Import Existing YAML

Use the import command to convert existing `.gitlab-ci.yml` to Python:

```bash
wetwire-gitlab import .gitlab-ci.yml --output ci/
```

This generates:
- Python files for each job
- Pipeline configuration
- Shared variables and stages

See [Import Workflow](IMPORT_WORKFLOW.md) for details.

---

## See Also

- [Quick Start](QUICK_START.md) - Getting started guide
- [CLI Reference](CLI.md) - All commands
- [Import Workflow](IMPORT_WORKFLOW.md) - Converting YAML to Python
