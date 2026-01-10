"""Job definitions for multi-stage pipeline."""

from wetwire_gitlab.intrinsics import CI, When
from wetwire_gitlab.pipeline import Artifacts, Cache, Job, Rule

# Shared cache for node_modules
node_cache = Cache(
    key="${CI_COMMIT_REF_SLUG}",
    paths=["node_modules/", ".npm/"],
)

# Prepare stage - install dependencies
prepare = Job(
    name="prepare",
    stage="prepare",
    image="node:20",
    script=[
        "npm ci --cache .npm",
    ],
    cache=node_cache,
    artifacts=Artifacts(
        paths=["node_modules/"],
        expire_in="1 day",
    ),
)

# Build stage - parallel builds
build_frontend = Job(
    name="build-frontend",
    stage="build",
    image="node:20",
    script=[
        "npm run build:frontend",
    ],
    artifacts=Artifacts(
        paths=["dist/frontend/"],
        expire_in="1 week",
    ),
    needs=["prepare"],
)

build_backend = Job(
    name="build-backend",
    stage="build",
    image="node:20",
    script=[
        "npm run build:backend",
    ],
    artifacts=Artifacts(
        paths=["dist/backend/"],
        expire_in="1 week",
    ),
    needs=["prepare"],
)

build_docs = Job(
    name="build-docs",
    stage="build",
    image="node:20",
    script=[
        "npm run build:docs",
    ],
    artifacts=Artifacts(
        paths=["dist/docs/"],
        expire_in="1 week",
    ),
    needs=["prepare"],
)

# Test stage - parallel tests
test_unit = Job(
    name="test-unit",
    stage="test",
    image="node:20",
    script=[
        "npm run test:unit -- --coverage",
    ],
    artifacts=Artifacts(
        paths=["coverage/"],
        reports={"coverage_report": {"coverage_format": "cobertura", "path": "coverage/cobertura.xml"}},
    ),
    needs=["build-frontend", "build-backend"],
)

test_integration = Job(
    name="test-integration",
    stage="test",
    image="node:20",
    services=["postgres:15", "redis:7"],
    variables={
        "POSTGRES_DB": "test",
        "POSTGRES_USER": "test",
        "POSTGRES_PASSWORD": "test",
    },
    script=[
        "npm run test:integration",
    ],
    needs=["build-backend"],
)

test_e2e = Job(
    name="test-e2e",
    stage="test",
    image="cypress/browsers:latest",
    script=[
        "npm run test:e2e",
    ],
    artifacts=Artifacts(
        paths=["cypress/screenshots/", "cypress/videos/"],
        when="on_failure",
        expire_in="1 week",
    ),
    needs=["build-frontend", "build-backend"],
)

# Quality stage - code quality checks
lint = Job(
    name="lint",
    stage="quality",
    image="node:20",
    script=[
        "npm run lint",
    ],
    needs=["prepare"],
)

security_scan = Job(
    name="security-scan",
    stage="quality",
    image="node:20",
    script=[
        "npm audit --audit-level=high",
    ],
    allow_failure=True,
    needs=["prepare"],
)

# Deploy stage
deploy_staging = Job(
    name="deploy-staging",
    stage="deploy",
    image="alpine:latest",
    environment={"name": "staging", "url": "https://staging.example.com"},
    script=[
        "echo 'Deploying to staging...'",
    ],
    rules=[
        Rule(if_=f"{CI.COMMIT_BRANCH} == {CI.DEFAULT_BRANCH}"),
    ],
    needs=["test-unit", "test-integration", "test-e2e"],
)

deploy_production = Job(
    name="deploy-production",
    stage="deploy",
    image="alpine:latest",
    environment={"name": "production", "url": "https://example.com"},
    script=[
        "echo 'Deploying to production...'",
    ],
    rules=[
        Rule(if_=f"{CI.COMMIT_BRANCH} == {CI.DEFAULT_BRANCH}", when=When.MANUAL),
    ],
    needs=["deploy-staging"],
)
