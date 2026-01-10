# Quick Start

This guide will help you get started with wetwire-gitlab in minutes.

## Installation

```bash
pip install wetwire-gitlab
# or with uv
uv add wetwire-gitlab
```

## Create Your First Pipeline

### 1. Initialize a Project

Create a new directory with the following structure:

```
my-project/
├── ci/
│   ├── __init__.py
│   ├── jobs.py
│   └── pipeline.py
└── pyproject.toml
```

### 2. Configure pyproject.toml

```toml
[project]
name = "my-project"
version = "0.1.0"

[tool.wetwire-gitlab]
package = "ci"
```

### 3. Define Your Pipeline

**ci/pipeline.py:**

```python
from wetwire_gitlab.pipeline import *

pipeline = Pipeline(stages=["test", "deploy"])
```

**ci/jobs.py:**

```python
from wetwire_gitlab.intrinsics import *
from wetwire_gitlab.pipeline import *

test = Job(
    name="test",
    stage="test",
    image="python:3.11",
    script=[
        "pip install -e .[dev]",
        "pytest",
    ],
)

deploy = Job(
    name="deploy",
    stage="deploy",
    image="python:3.11",
    script=[
        "echo 'Deploying...'",
    ],
    rules=[
        Rule(if_=f"{CI.COMMIT_BRANCH} == {CI.DEFAULT_BRANCH}", when=When.MANUAL),
    ],
)
```

**ci/__init__.py:**

```python
from .jobs import deploy, test
from .pipeline import pipeline

__all__ = ["deploy", "pipeline", "test"]
```

### 4. Generate .gitlab-ci.yml

```bash
wetwire-gitlab build
```

This generates:

```yaml
stages:
  - test
  - deploy

test:
  stage: test
  image: python:3.11
  script:
    - pip install -e .[dev]
    - pytest

deploy:
  stage: deploy
  image: python:3.11
  script:
    - echo 'Deploying...'
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
      when: manual
```

## Common Commands

```bash
# Generate .gitlab-ci.yml
wetwire-gitlab build

# Validate the pipeline
wetwire-gitlab validate

# List discovered jobs
wetwire-gitlab list

# Lint your pipeline code
wetwire-gitlab lint

# Import existing .gitlab-ci.yml
wetwire-gitlab import .gitlab-ci.yml
```

## Multi-File Organization

As your pipeline grows, organize jobs into logical modules.

### Organizing by Stage

**ci/jobs/build.py:**

```python
from wetwire_gitlab.intrinsics import *
from wetwire_gitlab.pipeline import *

build_frontend = Job(
    name="build-frontend",
    stage="build",
    image="node:20",
    script=["npm run build:frontend"],
    artifacts=Artifacts(paths=["dist/frontend/"], expire_in="1 week"),
)

build_backend = Job(
    name="build-backend",
    stage="build",
    image="node:20",
    script=["npm run build:backend"],
    artifacts=Artifacts(paths=["dist/backend/"], expire_in="1 week"),
)
```

**ci/jobs/test.py:**

```python
from wetwire_gitlab.pipeline import *

test_unit = Job(
    name="test-unit",
    stage="test",
    image="node:20",
    script=["npm run test:unit"],
    needs=["build-frontend", "build-backend"],
)

test_integration = Job(
    name="test-integration",
    stage="test",
    image="node:20",
    services=["postgres:15"],
    script=["npm run test:integration"],
    needs=["build-backend"],
)
```

**ci/jobs/__init__.py:**

```python
from .build import build_backend, build_frontend
from .test import test_integration, test_unit

__all__ = ["build_backend", "build_frontend", "test_integration", "test_unit"]
```

### Shared Configurations

Extract reusable components to avoid repetition.

**ci/shared.py:**

```python
from wetwire_gitlab.pipeline import *

# Shared cache for all Python jobs
python_cache = Cache(
    key="${CI_JOB_NAME}",
    paths=[".cache/pip"],
)

# Shared cache for Node jobs
node_cache = Cache(
    key="${CI_COMMIT_REF_SLUG}",
    paths=["node_modules/", ".npm/"],
)

# Common Docker variables
DOCKER_VARS = {
    "DOCKER_TLS_CERTDIR": "/certs",
}
```

**ci/jobs.py:**

```python
from wetwire_gitlab.pipeline import *

from .shared import DOCKER_VARS, python_cache

test = Job(
    name="test",
    stage="test",
    image="python:3.11",
    cache=python_cache,
    script=["pip install -e .[dev]", "pytest"],
)

build_docker = Job(
    name="build-docker",
    stage="build",
    image="docker:24",
    services=["docker:24-dind"],
    variables=DOCKER_VARS,
    script=["docker build -t myimage ."],
)
```

## Common Patterns

### Docker Build and Push

```python
from wetwire_gitlab.intrinsics import *
from wetwire_gitlab.pipeline import *

build = Job(
    name="build",
    stage="build",
    image="docker:24",
    services=["docker:24-dind"],
    variables={
        "DOCKER_TLS_CERTDIR": "/certs",
        "IMAGE_TAG": f"{CI.REGISTRY_IMAGE}:{CI.COMMIT_SHORT_SHA}",
    },
    before_script=[
        f"docker login -u {CI.REGISTRY_USER} -p {CI.REGISTRY_PASSWORD} {CI.REGISTRY}",
    ],
    script=[
        "docker build -t $IMAGE_TAG .",
        "docker push $IMAGE_TAG",
    ],
    rules=[Rules.ON_DEFAULT_BRANCH, Rules.ON_TAG],
)
```

### Multi-Stage Pipeline with Dependencies

```python
from wetwire_gitlab.pipeline import *

# Define pipeline stages
pipeline = Pipeline(stages=["prepare", "build", "test", "deploy"])

# Prepare dependencies
prepare = Job(
    name="prepare",
    stage="prepare",
    image="node:20",
    script=["npm ci"],
    artifacts=Artifacts(paths=["node_modules/"], expire_in="1 day"),
)

# Build depends on prepare
build = Job(
    name="build",
    stage="build",
    image="node:20",
    script=["npm run build"],
    artifacts=Artifacts(paths=["dist/"], expire_in="1 week"),
    needs=["prepare"],
)

# Tests run in parallel after build
test_unit = Job(
    name="test-unit",
    stage="test",
    image="node:20",
    script=["npm run test:unit"],
    needs=["build"],
)

test_e2e = Job(
    name="test-e2e",
    stage="test",
    image="cypress/browsers:latest",
    script=["npm run test:e2e"],
    needs=["build"],
)

# Deploy only after all tests pass
deploy = Job(
    name="deploy",
    stage="deploy",
    script=["echo 'Deploying...'"],
    needs=["test-unit", "test-e2e"],
)
```

### Conditional Deployments

```python
from wetwire_gitlab.intrinsics import *
from wetwire_gitlab.pipeline import *

# Auto-deploy to staging on main branch
deploy_staging = Job(
    name="deploy-staging",
    stage="deploy",
    environment={"name": "staging", "url": "https://staging.example.com"},
    script=["./deploy.sh staging"],
    rules=[
        Rule(if_=f"{CI.COMMIT_BRANCH} == {CI.DEFAULT_BRANCH}"),
    ],
)

# Manual deployment to production
deploy_production = Job(
    name="deploy-production",
    stage="deploy",
    environment={"name": "production", "url": "https://example.com"},
    script=["./deploy.sh production"],
    rules=[
        Rule(if_=f"{CI.COMMIT_BRANCH} == {CI.DEFAULT_BRANCH}", when=When.MANUAL),
    ],
    needs=["deploy-staging"],
)

# Deploy to dev on feature branches
deploy_dev = Job(
    name="deploy-dev",
    stage="deploy",
    environment={"name": "development", "url": "https://dev.example.com"},
    script=["./deploy.sh dev"],
    rules=[
        Rule(if_=f'{CI.COMMIT_BRANCH} != "{CI.DEFAULT_BRANCH}"'),
    ],
)
```

### Matrix Testing

```python
from wetwire_gitlab.pipeline import *

# Shared cache configuration
pip_cache = Cache(
    key="${CI_JOB_NAME}",
    paths=[".cache/pip"],
)

# Test multiple Python versions
test_py311 = Job(
    name="test-py311",
    stage="test",
    image="python:3.11",
    cache=pip_cache,
    script=["pip install -e .[dev]", "pytest"],
)

test_py312 = Job(
    name="test-py312",
    stage="test",
    image="python:3.12",
    cache=pip_cache,
    script=["pip install -e .[dev]", "pytest"],
)

test_py313 = Job(
    name="test-py313",
    stage="test",
    image="python:3.13",
    cache=pip_cache,
    script=["pip install -e .[dev]", "pytest"],
)
```

### Monorepo with Change Detection

```python
from wetwire_gitlab.intrinsics import *
from wetwire_gitlab.pipeline import *

# Detect which packages changed
detect_changes = Job(
    name="detect-changes",
    stage="detect",
    image="alpine:latest",
    before_script=["apk add --no-cache git"],
    script=[
        f"git diff --name-only {CI.COMMIT_BEFORE_SHA}...{CI.COMMIT_SHA} > changes.txt",
        "grep -q '^packages/frontend/' changes.txt && echo 'FRONTEND_CHANGED=true' >> build.env || echo 'FRONTEND_CHANGED=false' >> build.env",
        "grep -q '^packages/backend/' changes.txt && echo 'BACKEND_CHANGED=true' >> build.env || echo 'BACKEND_CHANGED=false' >> build.env",
    ],
    artifacts=Artifacts(
        paths=["changes.txt"],
        reports={"dotenv": "build.env"},
    ),
)

# Trigger child pipelines only for changed packages
trigger_frontend = Job(
    name="trigger-frontend",
    stage="trigger",
    trigger=Trigger(
        include=[{"local": "packages/frontend/.gitlab-ci.yml"}],
        strategy="depend",
    ),
    needs=["detect-changes"],
    rules=[Rule(if_='$FRONTEND_CHANGED == "true"')],
)
```

## Type-Safe Constants

### CI Variables

Use typed variable references instead of raw strings:

```python
from wetwire_gitlab.intrinsics import *

# Commit information
CI.COMMIT_SHA           # $CI_COMMIT_SHA
CI.COMMIT_SHORT_SHA     # $CI_COMMIT_SHORT_SHA
CI.COMMIT_BRANCH        # $CI_COMMIT_BRANCH
CI.COMMIT_TAG           # $CI_COMMIT_TAG
CI.DEFAULT_BRANCH       # $CI_DEFAULT_BRANCH

# Pipeline context
CI.PIPELINE_ID          # $CI_PIPELINE_ID
CI.PIPELINE_SOURCE      # $CI_PIPELINE_SOURCE
CI.PIPELINE_URL         # $CI_PIPELINE_URL

# Job context
CI.JOB_NAME             # $CI_JOB_NAME
CI.JOB_STAGE            # $CI_JOB_STAGE
CI.JOB_TOKEN            # $CI_JOB_TOKEN

# Registry
CI.REGISTRY             # $CI_REGISTRY
CI.REGISTRY_IMAGE       # $CI_REGISTRY_IMAGE
CI.REGISTRY_USER        # $CI_REGISTRY_USER
CI.REGISTRY_PASSWORD    # $CI_REGISTRY_PASSWORD

# User context
GitLab.USER_LOGIN       # $GITLAB_USER_LOGIN
GitLab.USER_EMAIL       # $GITLAB_USER_EMAIL

# Merge request context
MR.SOURCE_BRANCH        # $CI_MERGE_REQUEST_SOURCE_BRANCH_NAME
MR.TARGET_BRANCH        # $CI_MERGE_REQUEST_TARGET_BRANCH_NAME
MR.IID                  # $CI_MERGE_REQUEST_IID
```

### Predefined Rules

```python
from wetwire_gitlab.intrinsics import *

# Common rule patterns
Rules.ON_DEFAULT_BRANCH    # Run on default branch (main/master)
Rules.ON_TAG               # Run on git tags
Rules.ON_MERGE_REQUEST     # Run on merge requests
```

### When Constants

```python
from wetwire_gitlab.intrinsics import *

job = Job(
    name="manual-deploy",
    when=When.MANUAL,      # manual, on_success, on_failure, always, never, delayed
)
```

### Cache Policy

```python
from wetwire_gitlab.intrinsics import *
from wetwire_gitlab.pipeline import *

cache = Cache(
    key="my-cache",
    paths=["node_modules/"],
    policy=CachePolicy.PULL_PUSH,  # pull, push, pull-push
)
```

### Artifacts When

```python
from wetwire_gitlab.intrinsics import *
from wetwire_gitlab.pipeline import *

artifacts = Artifacts(
    paths=["test-results/"],
    when=ArtifactsWhen.ON_FAILURE,  # on_success, on_failure, always
)
```

## Troubleshooting

### Common Errors

#### Missing Package Configuration

```
Error: No package specified in pyproject.toml
```

**Solution:** Add tool configuration to `pyproject.toml`:

```toml
[tool.wetwire-gitlab]
package = "ci"
```

#### Job Not Discovered

```
Warning: No jobs found in package 'ci'
```

**Solution:** Ensure jobs are exported in `ci/__init__.py`:

```python
from .jobs import build, deploy, test

__all__ = ["build", "deploy", "test"]
```

#### Invalid YAML Output

```
Error: Invalid GitLab CI configuration
```

**Solution:** Run validation to see specific errors:

```bash
wetwire-gitlab validate
```

Common causes:
- Missing required fields (name, stage, script)
- Invalid rule syntax
- Circular dependencies in needs

#### Lint Errors

```
WGL003: Use predefined variables from intrinsics
```

**Solution:** Replace string variables with typed references:

```python
# Before
rules=[Rule(if_="$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH")]

# After
from wetwire_gitlab.intrinsics import *
rules=[Rule(if_=f"{CI.COMMIT_BRANCH} == {CI.DEFAULT_BRANCH}")]
```

### Debugging Workflow

1. **List discovered jobs:**
   ```bash
   wetwire-gitlab list
   ```

2. **Check for lint issues:**
   ```bash
   wetwire-gitlab lint
   ```

3. **Auto-fix common issues:**
   ```bash
   wetwire-gitlab lint --fix
   ```

4. **Generate YAML:**
   ```bash
   wetwire-gitlab build
   ```

5. **Validate with GitLab:**
   ```bash
   wetwire-gitlab validate
   ```

### Validation Issues

If validation fails, check:

- **GitLab CLI installed:** `glab --version`
- **Authenticated:** `glab auth status`
- **In git repository:** Validation requires a GitLab project

To validate without GitLab:

```bash
# Just generate YAML
wetwire-gitlab build

# Manually validate with GitLab API
curl --header "Content-Type: application/json" \
     --data @.gitlab-ci.yml \
     "https://gitlab.com/api/v4/ci/lint"
```

### Import Existing Pipeline

Convert existing `.gitlab-ci.yml` to typed Python:

```bash
wetwire-gitlab import .gitlab-ci.yml > ci/imported.py
```

This generates Python code you can refactor into your project structure.

## Best Practices

1. **Use typed dataclasses** - Prefer `Job()`, `Rule()`, `Cache()` over raw dicts
2. **Extract shared configs** - Define caches, variables once and reuse
3. **Organize by stage** - Split large pipelines into `ci/jobs/build.py`, `ci/jobs/test.py`, etc.
4. **Use intrinsics** - Import `CI`, `GitLab`, `MR` for type-safe variables
5. **Leverage predefined rules** - Use `Rules.ON_DEFAULT_BRANCH` instead of manual if conditions
6. **Run lint regularly** - Catch issues early with `wetwire-gitlab lint --fix`
7. **Validate before commit** - Always run `wetwire-gitlab validate` before pushing

## Next Steps

- See [Examples](../examples/) for complete pipeline examples
- Read [CLI Reference](CLI.md) for all commands
- Check [Lint Rules](LINT_RULES.md) for code quality guidelines
