# Examples

This guide documents the 5 example projects included with wetwire-gitlab.

## Overview

| Example | Description | Key Concepts |
|---------|-------------|--------------|
| [python-app](#python-app) | Basic Python CI/CD | Multi-version testing, coverage reports, manual deploy |
| [docker-build](#docker-build) | Docker build & push | Docker-in-Docker, registry auth, artifact passing |
| [multi-stage](#multi-stage) | Complex pipeline | DAG dependencies, parallel jobs, environments |
| [kubernetes-deploy](#kubernetes-deploy) | Helm-based deployment | Multi-environment, namespace isolation, progressive deploy |
| [monorepo](#monorepo) | Dynamic child pipelines | Change detection, triggers, dotenv reports |

## Running Examples

Each example is a complete, buildable package:

```bash
# Build any example
cd examples/python-app
wetwire-gitlab build

# View the generated .gitlab-ci.yml
cat .gitlab-ci.yml
```

---

## python-app

**Location:** `examples/python-app/`

A basic Python CI/CD pipeline demonstrating test, lint, and deploy stages with multi-version testing.

### Structure

```
python-app/
├── ci/
│   ├── __init__.py
│   ├── jobs.py      # Test and deploy jobs
│   └── pipeline.py  # Pipeline stages
├── pyproject.toml
└── README.md
```

### Key Patterns

**Multi-version testing** - Separate jobs for Python 3.11, 3.12, and 3.13:

```python
test_py311 = Job(
    name="test:py311",
    stage="test",
    image=Image(name="python:3.11"),
    script=["pip install -e .", "pytest"],
)
```

**Cache management** - Shared pip cache across jobs:

```python
cache = Cache(
    key="${CI_JOB_NAME}",
    paths=[".cache/pip"],
)
```

**Coverage reports** - Using Cobertura format:

```python
artifacts=Artifacts(
    reports={"coverage_report": {"coverage_format": "cobertura", "path": "coverage.xml"}},
)
```

**Manual deployment** - Conditional manual trigger:

```python
deploy = Job(
    name="deploy",
    rules=[Rule(if_=f"{CI.COMMIT_BRANCH} == {CI.DEFAULT_BRANCH}", when=When.MANUAL)],
    needs=["test:py311", "test:py312", "test:py313"],
)
```

### Concepts Demonstrated

- Multi-image job variants
- Coverage report parsing
- Manual job gates
- Job dependencies (needs)
- Cache with custom keys

---

## docker-build

**Location:** `examples/docker-build/`

Docker build and push pipeline with GitLab Container Registry integration.

### Structure

```
docker-build/
├── ci/
│   ├── __init__.py
│   ├── jobs.py      # Build, test, push jobs
│   └── pipeline.py  # Pipeline stages
├── pyproject.toml
└── README.md
```

### Key Patterns

**Docker-in-Docker (DinD)** - Using DinD service:

```python
build = Job(
    name="build",
    image=Image(name="docker:24"),
    services=["docker:24-dind"],
    variables={"DOCKER_TLS_CERTDIR": "/certs"},
)
```

**Registry authentication** - Using CI variables:

```python
before_script=[
    f"docker login -u {CI.REGISTRY_USER} -p {CI.REGISTRY_PASSWORD} {CI.REGISTRY}",
]
```

**Image tagging** - Dynamic tags with commit SHA:

```python
script=[
    f"docker build -t {CI.REGISTRY_IMAGE}:{CI.COMMIT_SHORT_SHA} .",
]
```

**Predefined rules** - Using Rules constants:

```python
push = Job(
    name="push",
    rules=[Rules.ON_DEFAULT_BRANCH, Rules.ON_TAG],
)
```

**Artifact passing** - Image tarball between stages:

```python
artifacts=Artifacts(
    paths=["image.tar"],
    expire_in="1 hour",
)
```

### Concepts Demonstrated

- DinD service configuration
- Container Registry integration
- Image tagging strategies
- Artifact passing between stages
- Tag-based triggers

---

## multi-stage

**Location:** `examples/multi-stage/`

Complex pipeline with job dependencies, parallel execution, and environment-based deployments.

### Structure

```
multi-stage/
├── ci/
│   ├── __init__.py
│   ├── jobs.py      # 10+ jobs across 5 stages
│   └── pipeline.py  # Complex stage definitions
├── pyproject.toml
└── README.md
```

### Key Patterns

**Five-stage pipeline**:

```python
pipeline = Pipeline(stages=["prepare", "build", "test", "quality", "deploy"])
```

**Parallel builds** - Three jobs depending on prepare:

```python
build_frontend = Job(name="build:frontend", needs=["prepare"])
build_backend = Job(name="build:backend", needs=["prepare"])
build_docs = Job(name="build:docs", needs=["prepare"])
```

**Service dependencies** - Integration test with PostgreSQL/Redis:

```python
test_integration = Job(
    name="test:integration",
    services=["postgres:15", "redis:7"],
    variables={
        "POSTGRES_DB": "testdb",
        "POSTGRES_USER": "test",
        "POSTGRES_PASSWORD": "test",
        "REDIS_URL": "redis://redis:6379",
    },
)
```

**Failure-conditional artifacts** - E2E screenshots on failure:

```python
artifacts=Artifacts(
    paths=["cypress/screenshots/", "cypress/videos/"],
    when="on_failure",
)
```

**Environment configuration**:

```python
deploy_staging = Job(
    name="deploy:staging",
    environment={"name": "staging", "url": "https://staging.example.com"},
    rules=[Rules.ON_DEFAULT_BRANCH],
)

deploy_production = Job(
    name="deploy:production",
    needs=["deploy:staging"],
    environment={"name": "production", "url": "https://example.com"},
    rules=[Rule(if_=f"{CI.COMMIT_BRANCH} == {CI.DEFAULT_BRANCH}", when=When.MANUAL)],
)
```

### Concepts Demonstrated

- Complex DAG pipelines
- Service containers with custom variables
- Conditional artifact collection
- Environment tracking
- Multi-stage dependencies
- Parallel job optimization

---

## kubernetes-deploy

**Location:** `examples/kubernetes-deploy/`

Multi-environment Kubernetes deployment using Helm with environment-specific configurations.

### Structure

```
kubernetes-deploy/
├── ci/
│   ├── __init__.py
│   ├── jobs.py      # Build and deploy jobs
│   └── pipeline.py  # Pipeline stages
├── pyproject.toml
└── README.md
```

### Key Patterns

**Helm integration** - Using Alpine Helm image:

```python
deploy_dev = Job(
    name="deploy:dev",
    image=Image(name="alpine/helm:3.14"),
    variables={
        "KUBE_NAMESPACE": "development",
        "HELM_RELEASE_NAME": "myapp-dev",
    },
    script=[
        "helm upgrade --install $HELM_RELEASE_NAME ./helm-chart "
        f"--namespace $KUBE_NAMESPACE --set image.tag={CI.COMMIT_SHORT_SHA}",
    ],
)
```

**Multi-environment deployments**:

```python
# Development - all branches except default
deploy_dev = Job(
    rules=[Rule(if_=f"{CI.COMMIT_BRANCH} != {CI.DEFAULT_BRANCH}")],
)

# Staging - default branch only
deploy_staging = Job(
    rules=[Rules.ON_DEFAULT_BRANCH],
    needs=["build"],
)

# Production - manual approval after staging
deploy_production = Job(
    rules=[Rule(if_=f"{CI.COMMIT_BRANCH} == {CI.DEFAULT_BRANCH}", when=When.MANUAL)],
    needs=["deploy:staging"],
    script=["helm upgrade ... --set replicas=3"],  # Higher replica count
)
```

**Environment tracking**:

```python
environment={"name": "production", "url": "https://app.example.com"}
```

### Concepts Demonstrated

- Helm-based deployments
- Kubernetes namespace management
- Multi-environment promotion
- Environment-specific replicas
- Progressive deployment (dev -> staging -> production)

---

## monorepo

**Location:** `examples/monorepo/`

Monorepo with dynamic child pipelines triggered based on detected changes to specific packages.

### Structure

```
monorepo/
├── ci/
│   ├── __init__.py
│   ├── jobs.py      # Detect and trigger jobs
│   └── pipeline.py  # Pipeline stages
├── pyproject.toml
└── README.md
```

### Key Patterns

**Change detection** - Git diff to identify changed packages:

```python
detect_changes = Job(
    name="detect-changes",
    script=[
        'FRONTEND_CHANGED=$(git diff --name-only $CI_COMMIT_BEFORE_SHA $CI_COMMIT_SHA | grep -q "^packages/frontend/" && echo "true" || echo "false")',
        'BACKEND_CHANGED=$(git diff --name-only $CI_COMMIT_BEFORE_SHA $CI_COMMIT_SHA | grep -q "^packages/backend/" && echo "true" || echo "false")',
        'echo "FRONTEND_CHANGED=$FRONTEND_CHANGED" >> build.env',
        'echo "BACKEND_CHANGED=$BACKEND_CHANGED" >> build.env',
    ],
    artifacts=Artifacts(reports={"dotenv": "build.env"}),
)
```

**Dynamic triggers** - Child pipelines per package:

```python
trigger_frontend = Job(
    name="trigger:frontend",
    stage="trigger",
    needs=["detect-changes"],
    trigger=Trigger(
        include=[{"local": "packages/frontend/.gitlab-ci.yml"}],
        strategy="depend",
    ),
    rules=[Rule(if_='$FRONTEND_CHANGED == "true"')],
)
```

**Conditional triggering** - Only run when package changed:

```python
rules=[Rule(if_='$BACKEND_CHANGED == "true"')]
```

### Concepts Demonstrated

- Change detection for monorepos
- Child pipelines with local includes
- Dynamic job triggering
- Dotenv artifact reports
- Cross-package dependency management

---

## Pattern Reference

### Common Patterns Across Examples

| Pattern | Examples |
|---------|----------|
| Artifacts | All 5 |
| Rules/Conditions | All 5 |
| Job Dependencies (needs) | All 5 |
| CI Variables | docker-build, kubernetes-deploy, monorepo |
| Cache | python-app, multi-stage |
| Services | docker-build, multi-stage, kubernetes-deploy |
| Environment Tracking | multi-stage, kubernetes-deploy |
| Rules Constants | docker-build |
| Before/After Scripts | docker-build, kubernetes-deploy |
| Triggers | monorepo |

### Wetwire-Gitlab Features Demonstrated

1. **Typed Dataclasses** - `Job`, `Pipeline`, `Artifacts`, `Cache`, `Rule`, `Trigger`
2. **Intrinsics Package** - `CI.*`, `When`, `Rules` constants
3. **Variable Interpolation** - F-strings with CI variables
4. **Complex Dependencies** - DAG pipelines with multi-level dependencies
5. **Environment Variables** - Global and job-specific scoping
6. **Artifact Management** - Reports, expiration, conditional collection
7. **Service Integration** - Docker, PostgreSQL, Redis
8. **Helm Integration** - Kubernetes deployment patterns
9. **Monorepo Support** - Change detection and dynamic triggers
