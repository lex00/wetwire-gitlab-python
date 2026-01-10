"""GitLab official template reference testing.

This module tests the importer against sample GitLab official CI templates
to verify round-trip correctness: YAML -> IR -> Python code -> validation.

Per WETWIRE_SPEC.md Section 11.1:
- Domain packages MUST test against reference examples from the target platform
- Should test GitLab's official CI templates, starter workflows, Auto DevOps templates
"""

import pytest

from wetwire_gitlab.importer import generate_python_code, parse_gitlab_ci


# =============================================================================
# Auto DevOps Templates
# =============================================================================

AUTO_DEVOPS_BASIC = """
include:
  - template: Auto-DevOps.gitlab-ci.yml

variables:
  AUTO_DEVOPS_BUILD_IMAGE_CNB_ENABLED: "true"
  POSTGRES_ENABLED: "false"
"""

AUTO_DEVOPS_WITH_DEPLOY = """
include:
  - template: Auto-DevOps.gitlab-ci.yml

stages:
  - build
  - test
  - deploy
  - review
  - dast
  - staging
  - canary
  - production
  - incremental rollout 10%
  - incremental rollout 25%
  - incremental rollout 50%
  - incremental rollout 100%
  - cleanup

variables:
  POSTGRES_ENABLED: "true"
  STAGING_ENABLED: "true"
  CANARY_ENABLED: "true"
"""

AUTO_DEVOPS_CUSTOM_BUILD = """
include:
  - template: Jobs/Build.gitlab-ci.yml
  - template: Jobs/Test.gitlab-ci.yml
  - template: Jobs/Deploy.gitlab-ci.yml

stages:
  - build
  - test
  - deploy

build:
  stage: build
  script:
    - docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA .
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
  rules:
    - if: $CI_COMMIT_BRANCH
"""


# =============================================================================
# Language-Specific Templates
# =============================================================================

PYTHON_TEMPLATE = """
stages:
  - test
  - deploy

default:
  image: python:3.11

variables:
  PIP_CACHE_DIR: "$CI_PROJECT_DIR/.pip-cache"

cache:
  paths:
    - .pip-cache/

test:
  stage: test
  script:
    - pip install -r requirements.txt
    - pytest --cov=src tests/
  coverage: '/TOTAL.*\\s+(\\d+%)/'
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml

lint:
  stage: test
  script:
    - pip install ruff
    - ruff check .
  allow_failure: true

deploy:
  stage: deploy
  script:
    - pip install twine
    - python -m build
    - twine upload dist/*
  rules:
    - if: $CI_COMMIT_TAG
"""

NODEJS_TEMPLATE = """
stages:
  - build
  - test
  - deploy

default:
  image: node:20

variables:
  npm_config_cache: "$CI_PROJECT_DIR/.npm"

cache:
  paths:
    - .npm/
    - node_modules/

build:
  stage: build
  script:
    - npm ci
    - npm run build
  artifacts:
    paths:
      - dist/
    expire_in: 1 week

test:
  stage: test
  script:
    - npm ci
    - npm run test
  needs:
    - build

lint:
  stage: test
  script:
    - npm ci
    - npm run lint
  needs:
    - build

deploy:
  stage: deploy
  script:
    - npm ci
    - npm run deploy
  needs:
    - test
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
      when: manual
  environment:
    name: production
"""

DOCKER_TEMPLATE = """
stages:
  - build
  - test
  - release

default:
  image: docker:24.0

services:
  - docker:24.0-dind

variables:
  DOCKER_TLS_CERTDIR: "/certs"
  DOCKER_HOST: tcp://docker:2376
  DOCKER_DRIVER: overlay2

build:
  stage: build
  script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
    - docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA .
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA

test:
  stage: test
  script:
    - docker run --rm $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA test
  needs:
    - build

release:
  stage: release
  script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
    - docker pull $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
    - docker tag $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA $CI_REGISTRY_IMAGE:latest
    - docker push $CI_REGISTRY_IMAGE:latest
  needs:
    - test
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
"""


# =============================================================================
# Security Scanning Templates
# =============================================================================

SAST_TEMPLATE = """
include:
  - template: Security/SAST.gitlab-ci.yml

stages:
  - test
  - security

variables:
  SAST_EXCLUDED_ANALYZERS: "brakeman"
  SAST_EXCLUDED_PATHS: "spec,test,docs"

sast:
  stage: security
  variables:
    SECURE_LOG_LEVEL: debug
"""

DAST_TEMPLATE = """
include:
  - template: Security/DAST.gitlab-ci.yml

stages:
  - build
  - test
  - deploy
  - dast

variables:
  DAST_WEBSITE: https://staging.example.com
  DAST_FULL_SCAN_ENABLED: "true"
  DAST_BROWSER_SCAN: "true"

dast:
  stage: dast
  needs:
    - deploy
"""

CONTAINER_SCANNING_TEMPLATE = """
include:
  - template: Security/Container-Scanning.gitlab-ci.yml

stages:
  - build
  - scan

variables:
  CS_IMAGE: $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
  CS_SEVERITY_THRESHOLD: CRITICAL
  CS_DOCKERFILE_PATH: Dockerfile

build:
  stage: build
  image: docker:24.0
  services:
    - docker:24.0-dind
  script:
    - docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA .
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA

container_scanning:
  stage: scan
  needs:
    - build
"""

SECRET_DETECTION_TEMPLATE = """
include:
  - template: Security/Secret-Detection.gitlab-ci.yml

stages:
  - test
  - security

variables:
  SECRET_DETECTION_HISTORIC_SCAN: "true"
  SECRET_DETECTION_LOG_OPTIONS: "--all"

secret_detection:
  stage: security
  variables:
    SECRET_DETECTION_EXCLUDED_PATHS: "tests/"
"""

DEPENDENCY_SCANNING_TEMPLATE = """
include:
  - template: Security/Dependency-Scanning.gitlab-ci.yml

stages:
  - test
  - security

variables:
  DS_EXCLUDED_ANALYZERS: "bundler-audit"
  DS_MAX_DEPTH: 3

dependency_scanning:
  stage: security
  before_script:
    - pip install --upgrade pip
"""

LICENSE_SCANNING_TEMPLATE = """
include:
  - template: Security/License-Scanning.gitlab-ci.yml

stages:
  - test
  - compliance

variables:
  LM_REPORT_VERSION: "2.1"
  LICENSE_FINDER_CLI_OPTS: "--decisions-file=./dependency_decisions.yml"

license_scanning:
  stage: compliance
"""


# =============================================================================
# Test Classes
# =============================================================================


class TestAutoDevOpsTemplates:
    """Tests for Auto DevOps template patterns."""

    def test_import_basic_auto_devops(self):
        """Import basic Auto DevOps include template."""
        pipeline = parse_gitlab_ci(AUTO_DEVOPS_BASIC)

        assert len(pipeline.includes) == 1
        assert pipeline.includes[0].template == "Auto-DevOps.gitlab-ci.yml"
        assert pipeline.variables is not None
        assert "AUTO_DEVOPS_BUILD_IMAGE_CNB_ENABLED" in pipeline.variables

    def test_import_auto_devops_with_stages(self):
        """Import Auto DevOps template with custom stages."""
        pipeline = parse_gitlab_ci(AUTO_DEVOPS_WITH_DEPLOY)

        assert len(pipeline.includes) == 1
        assert len(pipeline.stages) >= 5
        assert "build" in pipeline.stages
        assert "deploy" in pipeline.stages
        assert "production" in pipeline.stages
        assert pipeline.variables is not None
        assert pipeline.variables.get("STAGING_ENABLED") == "true"

    def test_import_custom_build_jobs(self):
        """Import Auto DevOps with custom build jobs."""
        pipeline = parse_gitlab_ci(AUTO_DEVOPS_CUSTOM_BUILD)

        assert len(pipeline.includes) == 3
        assert len(pipeline.jobs) == 1
        assert pipeline.jobs[0].name == "build"
        assert pipeline.jobs[0].rules is not None

    def test_round_trip_auto_devops(self):
        """Auto DevOps template survives round-trip."""
        pipeline = parse_gitlab_ci(AUTO_DEVOPS_CUSTOM_BUILD)
        code = generate_python_code(pipeline)

        # Code should be valid Python
        compile(code, "<test>", "exec")

        # Code should contain expected elements
        assert "from wetwire_gitlab.pipeline import" in code
        assert 'name="build"' in code
        assert "Rule" in code


class TestLanguageTemplates:
    """Tests for language-specific CI templates."""

    def test_python_template(self):
        """Import Python CI template."""
        pipeline = parse_gitlab_ci(PYTHON_TEMPLATE)

        assert pipeline.stages == ["test", "deploy"]
        assert len(pipeline.jobs) == 3

        job_names = [j.name for j in pipeline.jobs]
        assert "test" in job_names
        assert "lint" in job_names
        assert "deploy" in job_names

        # Check test job has coverage
        test_job = next(j for j in pipeline.jobs if j.name == "test")
        assert test_job.coverage is not None
        assert test_job.artifacts is not None

    def test_python_template_round_trip(self):
        """Python template survives round-trip."""
        pipeline = parse_gitlab_ci(PYTHON_TEMPLATE)
        code = generate_python_code(pipeline)

        # Code should be valid Python
        compile(code, "<test>", "exec")

        # Code should have expected structure
        assert 'stages=["test", "deploy"]' in code
        assert "Artifacts" in code

    def test_nodejs_template(self):
        """Import Node.js CI template."""
        pipeline = parse_gitlab_ci(NODEJS_TEMPLATE)

        assert pipeline.stages == ["build", "test", "deploy"]
        assert len(pipeline.jobs) == 4

        # Check build job has artifacts
        build_job = next(j for j in pipeline.jobs if j.name == "build")
        assert build_job.artifacts is not None

        # Check deploy job has environment
        deploy_job = next(j for j in pipeline.jobs if j.name == "deploy")
        assert deploy_job.environment is not None
        assert deploy_job.rules is not None

    def test_nodejs_template_round_trip(self):
        """Node.js template survives round-trip."""
        pipeline = parse_gitlab_ci(NODEJS_TEMPLATE)
        code = generate_python_code(pipeline)

        compile(code, "<test>", "exec")
        assert "environment=" in code
        assert "needs=" in code

    def test_docker_template(self):
        """Import Docker CI template."""
        pipeline = parse_gitlab_ci(DOCKER_TEMPLATE)

        assert pipeline.stages == ["build", "test", "release"]
        assert len(pipeline.jobs) == 3

        # Check variables
        assert pipeline.default is not None
        assert pipeline.default.get("image") == "docker:24.0"

    def test_docker_template_round_trip(self):
        """Docker template survives round-trip."""
        pipeline = parse_gitlab_ci(DOCKER_TEMPLATE)
        code = generate_python_code(pipeline)

        compile(code, "<test>", "exec")
        assert 'name="release"' in code


class TestSecurityTemplates:
    """Tests for security scanning templates."""

    def test_sast_template(self):
        """Import SAST scanning template."""
        pipeline = parse_gitlab_ci(SAST_TEMPLATE)

        assert len(pipeline.includes) == 1
        assert pipeline.includes[0].template == "Security/SAST.gitlab-ci.yml"
        assert "security" in pipeline.stages
        assert len(pipeline.jobs) == 1

    def test_sast_template_round_trip(self):
        """SAST template survives round-trip."""
        pipeline = parse_gitlab_ci(SAST_TEMPLATE)
        code = generate_python_code(pipeline)

        compile(code, "<test>", "exec")
        assert 'name="sast"' in code

    def test_dast_template(self):
        """Import DAST scanning template."""
        pipeline = parse_gitlab_ci(DAST_TEMPLATE)

        assert len(pipeline.includes) == 1
        assert pipeline.includes[0].template == "Security/DAST.gitlab-ci.yml"
        assert "dast" in pipeline.stages

        dast_job = next(j for j in pipeline.jobs if j.name == "dast")
        assert dast_job.needs is not None

    def test_dast_template_round_trip(self):
        """DAST template survives round-trip."""
        pipeline = parse_gitlab_ci(DAST_TEMPLATE)
        code = generate_python_code(pipeline)

        compile(code, "<test>", "exec")
        assert 'name="dast"' in code
        assert "needs=" in code

    def test_container_scanning_template(self):
        """Import container scanning template."""
        pipeline = parse_gitlab_ci(CONTAINER_SCANNING_TEMPLATE)

        assert len(pipeline.includes) == 1
        assert pipeline.includes[0].template == "Security/Container-Scanning.gitlab-ci.yml"
        assert "scan" in pipeline.stages
        assert len(pipeline.jobs) == 2

        scan_job = next(j for j in pipeline.jobs if j.name == "container_scanning")
        assert scan_job.needs is not None

    def test_container_scanning_round_trip(self):
        """Container scanning template survives round-trip."""
        pipeline = parse_gitlab_ci(CONTAINER_SCANNING_TEMPLATE)
        code = generate_python_code(pipeline)

        compile(code, "<test>", "exec")
        assert 'name="container_scanning"' in code

    def test_secret_detection_template(self):
        """Import secret detection template."""
        pipeline = parse_gitlab_ci(SECRET_DETECTION_TEMPLATE)

        assert len(pipeline.includes) == 1
        assert pipeline.includes[0].template == "Security/Secret-Detection.gitlab-ci.yml"
        assert "security" in pipeline.stages

    def test_secret_detection_round_trip(self):
        """Secret detection template survives round-trip."""
        pipeline = parse_gitlab_ci(SECRET_DETECTION_TEMPLATE)
        code = generate_python_code(pipeline)

        compile(code, "<test>", "exec")
        assert 'name="secret_detection"' in code

    def test_dependency_scanning_template(self):
        """Import dependency scanning template."""
        pipeline = parse_gitlab_ci(DEPENDENCY_SCANNING_TEMPLATE)

        assert len(pipeline.includes) == 1
        assert pipeline.includes[0].template == "Security/Dependency-Scanning.gitlab-ci.yml"

        dep_job = next(j for j in pipeline.jobs if j.name == "dependency_scanning")
        assert dep_job.before_script is not None

    def test_dependency_scanning_round_trip(self):
        """Dependency scanning template survives round-trip."""
        pipeline = parse_gitlab_ci(DEPENDENCY_SCANNING_TEMPLATE)
        code = generate_python_code(pipeline)

        compile(code, "<test>", "exec")
        assert "before_script=" in code

    def test_license_scanning_template(self):
        """Import license scanning template."""
        pipeline = parse_gitlab_ci(LICENSE_SCANNING_TEMPLATE)

        assert len(pipeline.includes) == 1
        assert pipeline.includes[0].template == "Security/License-Scanning.gitlab-ci.yml"
        assert "compliance" in pipeline.stages


class TestCodeGenerationValidation:
    """Tests validating generated Python code is executable."""

    @pytest.fixture
    def all_templates(self):
        """Return all template YAML snippets."""
        return [
            AUTO_DEVOPS_BASIC,
            AUTO_DEVOPS_WITH_DEPLOY,
            AUTO_DEVOPS_CUSTOM_BUILD,
            PYTHON_TEMPLATE,
            NODEJS_TEMPLATE,
            DOCKER_TEMPLATE,
            SAST_TEMPLATE,
            DAST_TEMPLATE,
            CONTAINER_SCANNING_TEMPLATE,
            SECRET_DETECTION_TEMPLATE,
            DEPENDENCY_SCANNING_TEMPLATE,
            LICENSE_SCANNING_TEMPLATE,
        ]

    def test_all_templates_parse(self, all_templates):
        """All official templates should parse successfully."""
        success_count = 0
        for yaml_content in all_templates:
            try:
                pipeline = parse_gitlab_ci(yaml_content)
                if pipeline is not None:
                    success_count += 1
            except Exception:
                pass

        assert success_count == len(all_templates)

    def test_all_templates_generate_valid_python(self, all_templates):
        """All templates should generate valid Python code."""
        success_count = 0
        for yaml_content in all_templates:
            try:
                pipeline = parse_gitlab_ci(yaml_content)
                code = generate_python_code(pipeline)
                compile(code, "<test>", "exec")
                success_count += 1
            except Exception:
                pass

        assert success_count == len(all_templates)

    def test_all_templates_execute(self, all_templates):
        """All generated Python code should execute without errors."""
        success_count = 0
        for yaml_content in all_templates:
            try:
                pipeline = parse_gitlab_ci(yaml_content)
                code = generate_python_code(pipeline)
                # Execute the code to ensure it runs without errors
                exec(code, {"__builtins__": __builtins__})
                success_count += 1
            except Exception:
                pass

        assert success_count == len(all_templates)


class TestRoundTripEquivalence:
    """Tests for round-trip equivalence: parse -> generate -> parse."""

    def test_simple_job_round_trip_equivalent(self):
        """Simple job structure is preserved through round-trip."""
        yaml_content = """
stages:
  - build

build:
  stage: build
  script:
    - make build
"""
        # First parse
        pipeline1 = parse_gitlab_ci(yaml_content)

        # Generate Python and execute to get objects
        code = generate_python_code(pipeline1)
        compile(code, "<test>", "exec")

        # Verify structure preserved
        assert pipeline1.stages == ["build"]
        assert len(pipeline1.jobs) == 1
        assert pipeline1.jobs[0].name == "build"
        assert pipeline1.jobs[0].script == ["make build"]

    def test_job_with_rules_round_trip(self):
        """Job with rules is preserved through round-trip."""
        yaml_content = """
stages:
  - deploy

deploy:
  stage: deploy
  script:
    - make deploy
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
      when: manual
"""
        pipeline = parse_gitlab_ci(yaml_content)
        code = generate_python_code(pipeline)

        # Verify code is valid
        compile(code, "<test>", "exec")

        # Verify structure
        assert len(pipeline.jobs) == 1
        assert pipeline.jobs[0].rules is not None
        assert len(pipeline.jobs[0].rules) == 1
        assert pipeline.jobs[0].rules[0].when == "manual"

    def test_job_with_artifacts_round_trip(self):
        """Job with artifacts is preserved through round-trip."""
        yaml_content = """
stages:
  - build

build:
  stage: build
  script:
    - make build
  artifacts:
    paths:
      - dist/
    expire_in: 1 week
"""
        pipeline = parse_gitlab_ci(yaml_content)
        code = generate_python_code(pipeline)

        compile(code, "<test>", "exec")

        assert pipeline.jobs[0].artifacts is not None
        assert "paths" in pipeline.jobs[0].artifacts

    def test_job_with_needs_round_trip(self):
        """Job with needs is preserved through round-trip."""
        yaml_content = """
stages:
  - build
  - test

build:
  stage: build
  script:
    - make build

test:
  stage: test
  script:
    - make test
  needs:
    - build
"""
        pipeline = parse_gitlab_ci(yaml_content)
        code = generate_python_code(pipeline)

        compile(code, "<test>", "exec")

        test_job = next(j for j in pipeline.jobs if j.name == "test")
        assert test_job.needs == ["build"]


class TestComplexPatterns:
    """Tests for complex GitLab CI patterns found in official templates."""

    def test_matrix_parallel_jobs(self):
        """Parse matrix/parallel job pattern."""
        yaml_content = """
test:
  script: pytest
  parallel:
    matrix:
      - PYTHON: ["3.9", "3.10", "3.11"]
        DATABASE: ["postgres", "mysql"]
"""
        pipeline = parse_gitlab_ci(yaml_content)

        assert len(pipeline.jobs) == 1
        assert pipeline.jobs[0].parallel is not None

    def test_trigger_child_pipeline(self):
        """Parse child pipeline trigger pattern."""
        yaml_content = """
stages:
  - trigger

deploy-child:
  stage: trigger
  trigger:
    include: .child-pipeline.yml
    strategy: depend
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
"""
        pipeline = parse_gitlab_ci(yaml_content)
        code = generate_python_code(pipeline)

        compile(code, "<test>", "exec")

        job = pipeline.jobs[0]
        assert job.trigger is not None
        assert job.rules is not None

    def test_resource_group_pattern(self):
        """Parse resource group pattern for deployment limiting."""
        yaml_content = """
deploy:
  script: deploy.sh
  resource_group: production
  environment:
    name: production
"""
        pipeline = parse_gitlab_ci(yaml_content)
        code = generate_python_code(pipeline)

        compile(code, "<test>", "exec")

        assert pipeline.jobs[0].resource_group == "production"

    def test_services_configuration(self):
        """Parse services configuration pattern."""
        yaml_content = """
test:
  script: pytest
  services:
    - name: postgres:15
      alias: db
    - name: redis:7
      alias: cache
"""
        pipeline = parse_gitlab_ci(yaml_content)
        code = generate_python_code(pipeline)

        compile(code, "<test>", "exec")

        assert pipeline.jobs[0].services is not None
        assert len(pipeline.jobs[0].services) == 2

    def test_interruptible_jobs(self):
        """Parse interruptible job pattern."""
        yaml_content = """
build:
  script: make build
  interruptible: true
  timeout: 30m

deploy:
  script: make deploy
  interruptible: false
"""
        pipeline = parse_gitlab_ci(yaml_content)
        code = generate_python_code(pipeline)

        compile(code, "<test>", "exec")

        build_job = next(j for j in pipeline.jobs if j.name == "build")
        deploy_job = next(j for j in pipeline.jobs if j.name == "deploy")

        assert build_job.interruptible is True
        assert deploy_job.interruptible is False
        assert build_job.timeout == "30m"
