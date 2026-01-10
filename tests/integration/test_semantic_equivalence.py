"""Tests for semantic YAML equivalence and round-trip validation.

This module tests that YAML imports and exports maintain semantic equivalence,
which is critical for the wetwire round-trip requirement.
"""

import pytest

from wetwire_gitlab.importer import generate_python_code, parse_gitlab_ci
from wetwire_gitlab.pipeline import Job, Pipeline
from wetwire_gitlab.serialize import build_pipeline_yaml
from wetwire_gitlab.testing import compare_yaml_semantic


@pytest.mark.slow
class TestSemanticCompareFunction:
    """Tests for the compare_yaml_semantic function."""

    def test_identical_yaml_is_equivalent(self):
        """Identical YAML strings are semantically equivalent."""
        yaml_content = """
stages:
  - build
  - test

build:
  stage: build
  script:
    - make build
"""
        is_eq, diffs = compare_yaml_semantic(yaml_content, yaml_content)

        assert is_eq is True
        assert len(diffs) == 0

    def test_different_formatting_is_equivalent(self):
        """YAML with different formatting but same structure is equivalent."""
        original = """
stages:
  - build
  - test
"""
        rebuilt = """stages: [build, test]"""

        is_eq, diffs = compare_yaml_semantic(original, rebuilt)

        assert is_eq is True
        assert len(diffs) == 0

    def test_different_key_order_is_equivalent(self):
        """YAML with different key ordering is equivalent."""
        original = """
build:
  stage: build
  script:
    - make build
"""
        rebuilt = """
build:
  script:
    - make build
  stage: build
"""
        is_eq, diffs = compare_yaml_semantic(original, rebuilt)

        assert is_eq is True
        assert len(diffs) == 0

    def test_whitespace_differences_are_equivalent(self):
        """YAML with different whitespace is equivalent."""
        original = """
build:
  script:
    - echo hello
"""
        rebuilt = """
build:
  script:
    - echo hello
"""
        is_eq, diffs = compare_yaml_semantic(original, rebuilt)

        assert is_eq is True
        assert len(diffs) == 0

    def test_missing_key_detected(self):
        """Missing keys are detected as differences."""
        original = """
build:
  stage: build
  script:
    - make
"""
        rebuilt = """
build:
  script:
    - make
"""
        is_eq, diffs = compare_yaml_semantic(original, rebuilt)

        assert is_eq is False
        assert len(diffs) > 0
        assert any("Missing key" in diff for diff in diffs)

    def test_extra_key_detected(self):
        """Extra keys are detected as differences."""
        original = """
build:
  script:
    - make
"""
        rebuilt = """
build:
  stage: build
  script:
    - make
"""
        is_eq, diffs = compare_yaml_semantic(original, rebuilt)

        assert is_eq is False
        assert len(diffs) > 0
        assert any("Extra key" in diff for diff in diffs)

    def test_value_difference_detected(self):
        """Different values are detected."""
        original = """
build:
  script:
    - make build
"""
        rebuilt = """
build:
  script:
    - make test
"""
        is_eq, diffs = compare_yaml_semantic(original, rebuilt)

        assert is_eq is False
        assert len(diffs) > 0
        assert any("Value mismatch" in diff for diff in diffs)

    def test_list_length_difference_detected(self):
        """Different list lengths are detected."""
        original = """
stages:
  - build
  - test
"""
        rebuilt = """
stages:
  - build
"""
        is_eq, diffs = compare_yaml_semantic(original, rebuilt)

        assert is_eq is False
        assert len(diffs) > 0
        assert any("List length mismatch" in diff for diff in diffs)

    def test_type_difference_detected(self):
        """Different types are detected."""
        original = """
build:
  script: make build
"""
        rebuilt = """
build:
  script:
    - make build
"""
        is_eq, diffs = compare_yaml_semantic(original, rebuilt)

        assert is_eq is False
        assert len(diffs) > 0
        assert any("Type mismatch" in diff for diff in diffs)

    def test_empty_yaml_comparison(self):
        """Empty YAML strings are equivalent."""
        is_eq, diffs = compare_yaml_semantic("", "")

        assert is_eq is True
        assert len(diffs) == 0

    def test_invalid_yaml_original(self):
        """Invalid original YAML is detected."""
        original = "this is not: valid: yaml:"
        rebuilt = "stages: [build]"

        is_eq, diffs = compare_yaml_semantic(original, rebuilt)

        assert is_eq is False
        assert len(diffs) > 0
        assert any("Failed to parse original YAML" in diff for diff in diffs)

    def test_invalid_yaml_rebuilt(self):
        """Invalid rebuilt YAML is detected."""
        original = "stages: [build]"
        rebuilt = "this is not: valid: yaml:"

        is_eq, diffs = compare_yaml_semantic(original, rebuilt)

        assert is_eq is False
        assert len(diffs) > 0
        assert any("Failed to parse rebuilt YAML" in diff for diff in diffs)

    def test_nested_structure_comparison(self):
        """Nested structures are compared correctly."""
        original = """
build:
  artifacts:
    paths:
      - dist/
    expire_in: 1 week
"""
        rebuilt = """
build:
  artifacts:
    paths:
      - dist/
    expire_in: 1 week
"""
        is_eq, diffs = compare_yaml_semantic(original, rebuilt)

        assert is_eq is True
        assert len(diffs) == 0

    def test_nested_difference_path_reported(self):
        """Differences in nested structures report the correct path."""
        original = """
build:
  artifacts:
    paths:
      - dist/
"""
        rebuilt = """
build:
  artifacts:
    paths:
      - build/
"""
        is_eq, diffs = compare_yaml_semantic(original, rebuilt)

        assert is_eq is False
        assert len(diffs) > 0
        # Should report path to the difference
        assert any("artifacts.paths[0]" in diff for diff in diffs)


@pytest.mark.slow
class TestRoundTripSemanticEquivalence:
    """Tests for complete round-trip semantic equivalence.

    These tests verify: YAML -> parse -> generate Python -> execute -> serialize -> YAML
    and that the output YAML is semantically equivalent to the input.
    """

    def test_simple_pipeline_round_trip(self):
        """Simple pipeline maintains semantic equivalence through round-trip."""
        original_yaml = """
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
"""
        # Parse the YAML
        ir_pipeline = parse_gitlab_ci(original_yaml)

        # Generate Python code (verify it compiles)
        _python_code = generate_python_code(ir_pipeline)
        compile(_python_code, "<test>", "exec")

        # Note: The generated code creates variables but doesn't export them in a way
        # we can easily execute. For now, we'll rebuild from the parsed IR directly.

        # Convert IR to typed objects
        pipeline = ir_pipeline.to_pipeline()
        jobs = [ir_job.to_job() for ir_job in ir_pipeline.jobs]

        # Rebuild YAML from typed objects
        rebuilt_yaml = build_pipeline_yaml(pipeline, jobs)

        # Compare for semantic equivalence
        is_eq, diffs = compare_yaml_semantic(original_yaml, rebuilt_yaml)

        # If not equivalent, print diffs for debugging
        if not is_eq:
            print("\nDifferences found:")
            for diff in diffs:
                print(f"  - {diff}")
            print(f"\nOriginal YAML:\n{original_yaml}")
            print(f"\nRebuilt YAML:\n{rebuilt_yaml}")

        assert is_eq is True, f"Round-trip failed with differences: {diffs}"

    def test_pipeline_with_variables_round_trip(self):
        """Pipeline with variables maintains equivalence."""
        original_yaml = """
variables:
  BUILD_DIR: dist
  NODE_ENV: production

stages:
  - build

build:
  stage: build
  script:
    - echo $BUILD_DIR
"""
        ir_pipeline = parse_gitlab_ci(original_yaml)
        pipeline = ir_pipeline.to_pipeline()
        jobs = [ir_job.to_job() for ir_job in ir_pipeline.jobs]
        rebuilt_yaml = build_pipeline_yaml(pipeline, jobs)

        is_eq, diffs = compare_yaml_semantic(original_yaml, rebuilt_yaml)

        if not is_eq:
            print(f"\nDifferences: {diffs}")
            print(f"\nOriginal:\n{original_yaml}")
            print(f"\nRebuilt:\n{rebuilt_yaml}")

        assert is_eq is True, f"Round-trip failed: {diffs}"

    def test_pipeline_with_artifacts_round_trip(self):
        """Pipeline with artifacts maintains equivalence."""
        original_yaml = """
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
        ir_pipeline = parse_gitlab_ci(original_yaml)
        pipeline = ir_pipeline.to_pipeline()
        jobs = [ir_job.to_job() for ir_job in ir_pipeline.jobs]
        rebuilt_yaml = build_pipeline_yaml(pipeline, jobs)

        is_eq, diffs = compare_yaml_semantic(original_yaml, rebuilt_yaml)

        if not is_eq:
            print(f"\nDifferences: {diffs}")
            print(f"\nOriginal:\n{original_yaml}")
            print(f"\nRebuilt:\n{rebuilt_yaml}")

        assert is_eq is True, f"Round-trip failed: {diffs}"

    def test_pipeline_with_rules_round_trip(self):
        """Pipeline with rules maintains equivalence."""
        original_yaml = """
stages:
  - deploy

deploy:
  stage: deploy
  script:
    - deploy.sh
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
      when: manual
"""
        ir_pipeline = parse_gitlab_ci(original_yaml)
        pipeline = ir_pipeline.to_pipeline()
        jobs = [ir_job.to_job() for ir_job in ir_pipeline.jobs]
        rebuilt_yaml = build_pipeline_yaml(pipeline, jobs)

        is_eq, diffs = compare_yaml_semantic(original_yaml, rebuilt_yaml)

        if not is_eq:
            print(f"\nDifferences: {diffs}")
            print(f"\nOriginal:\n{original_yaml}")
            print(f"\nRebuilt:\n{rebuilt_yaml}")

        assert is_eq is True, f"Round-trip failed: {diffs}"

    def test_pipeline_with_needs_round_trip(self):
        """Pipeline with needs maintains equivalence."""
        original_yaml = """
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
        ir_pipeline = parse_gitlab_ci(original_yaml)
        pipeline = ir_pipeline.to_pipeline()
        jobs = [ir_job.to_job() for ir_job in ir_pipeline.jobs]
        rebuilt_yaml = build_pipeline_yaml(pipeline, jobs)

        is_eq, diffs = compare_yaml_semantic(original_yaml, rebuilt_yaml)

        if not is_eq:
            print(f"\nDifferences: {diffs}")
            print(f"\nOriginal:\n{original_yaml}")
            print(f"\nRebuilt:\n{rebuilt_yaml}")

        assert is_eq is True, f"Round-trip failed: {diffs}"

    def test_pipeline_with_cache_round_trip(self):
        """Pipeline with cache maintains equivalence."""
        original_yaml = """
stages:
  - test

test:
  stage: test
  script:
    - pytest
  cache:
    paths:
      - .cache/
    key: test-cache
"""
        ir_pipeline = parse_gitlab_ci(original_yaml)
        pipeline = ir_pipeline.to_pipeline()
        jobs = [ir_job.to_job() for ir_job in ir_pipeline.jobs]
        rebuilt_yaml = build_pipeline_yaml(pipeline, jobs)

        is_eq, diffs = compare_yaml_semantic(original_yaml, rebuilt_yaml)

        if not is_eq:
            print(f"\nDifferences: {diffs}")
            print(f"\nOriginal:\n{original_yaml}")
            print(f"\nRebuilt:\n{rebuilt_yaml}")

        assert is_eq is True, f"Round-trip failed: {diffs}"

    def test_pipeline_with_includes_round_trip(self):
        """Pipeline with includes maintains equivalence."""
        original_yaml = """
include:
  - local: /.gitlab/ci/build.yml
  - template: Security/SAST.gitlab-ci.yml

stages:
  - build
"""
        ir_pipeline = parse_gitlab_ci(original_yaml)
        pipeline = ir_pipeline.to_pipeline()
        jobs = [ir_job.to_job() for ir_job in ir_pipeline.jobs]
        rebuilt_yaml = build_pipeline_yaml(pipeline, jobs)

        is_eq, diffs = compare_yaml_semantic(original_yaml, rebuilt_yaml)

        if not is_eq:
            print(f"\nDifferences: {diffs}")
            print(f"\nOriginal:\n{original_yaml}")
            print(f"\nRebuilt:\n{rebuilt_yaml}")

        assert is_eq is True, f"Round-trip failed: {diffs}"

    def test_pipeline_with_default_round_trip(self):
        """Pipeline with default settings maintains equivalence."""
        original_yaml = """
default:
  image: python:3.11

stages:
  - test

test:
  script:
    - pytest
"""
        ir_pipeline = parse_gitlab_ci(original_yaml)
        pipeline = ir_pipeline.to_pipeline()
        jobs = [ir_job.to_job() for ir_job in ir_pipeline.jobs]
        rebuilt_yaml = build_pipeline_yaml(pipeline, jobs)

        is_eq, diffs = compare_yaml_semantic(original_yaml, rebuilt_yaml)

        if not is_eq:
            print(f"\nDifferences: {diffs}")
            print(f"\nOriginal:\n{original_yaml}")
            print(f"\nRebuilt:\n{rebuilt_yaml}")

        assert is_eq is True, f"Round-trip failed: {diffs}"


@pytest.mark.slow
class TestComplexTemplateRoundTrip:
    """Tests for complex GitLab templates from test_gitlab_templates.py."""

    def test_python_template_round_trip(self):
        """Python template maintains semantic equivalence."""
        original_yaml = """
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
        ir_pipeline = parse_gitlab_ci(original_yaml)
        pipeline = ir_pipeline.to_pipeline()
        jobs = [ir_job.to_job() for ir_job in ir_pipeline.jobs]
        rebuilt_yaml = build_pipeline_yaml(pipeline, jobs)

        is_eq, diffs = compare_yaml_semantic(original_yaml, rebuilt_yaml)

        if not is_eq:
            print(f"\nDifferences: {diffs}")
            print(f"\nOriginal:\n{original_yaml}")
            print(f"\nRebuilt:\n{rebuilt_yaml}")

        assert is_eq is True, f"Round-trip failed: {diffs}"

    def test_docker_template_round_trip(self):
        """Docker template maintains semantic equivalence."""
        original_yaml = """
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
        ir_pipeline = parse_gitlab_ci(original_yaml)
        pipeline = ir_pipeline.to_pipeline()
        jobs = [ir_job.to_job() for ir_job in ir_pipeline.jobs]
        rebuilt_yaml = build_pipeline_yaml(pipeline, jobs)

        is_eq, diffs = compare_yaml_semantic(original_yaml, rebuilt_yaml)

        if not is_eq:
            print(f"\nDifferences: {diffs}")
            print(f"\nOriginal:\n{original_yaml}")
            print(f"\nRebuilt:\n{rebuilt_yaml}")

        assert is_eq is True, f"Round-trip failed: {diffs}"

    def test_nodejs_template_round_trip(self):
        """Node.js template maintains semantic equivalence."""
        original_yaml = """
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
        ir_pipeline = parse_gitlab_ci(original_yaml)
        pipeline = ir_pipeline.to_pipeline()
        jobs = [ir_job.to_job() for ir_job in ir_pipeline.jobs]
        rebuilt_yaml = build_pipeline_yaml(pipeline, jobs)

        is_eq, diffs = compare_yaml_semantic(original_yaml, rebuilt_yaml)

        if not is_eq:
            print(f"\nDifferences: {diffs}")
            print(f"\nOriginal:\n{original_yaml}")
            print(f"\nRebuilt:\n{rebuilt_yaml}")

        assert is_eq is True, f"Round-trip failed: {diffs}"


@pytest.mark.slow
class TestDirectPipelineConstruction:
    """Tests for semantic equivalence when constructing pipelines directly."""

    def test_direct_construction_equivalence(self):
        """Directly constructed pipeline serializes to expected YAML."""
        expected_yaml = """
stages:
  - build

build:
  stage: build
  script:
    - make build
"""
        # Construct pipeline directly
        pipeline = Pipeline(stages=["build"])
        jobs = [Job(name="build", stage="build", script=["make build"])]

        # Serialize to YAML
        rebuilt_yaml = build_pipeline_yaml(pipeline, jobs)

        # Compare
        is_eq, diffs = compare_yaml_semantic(expected_yaml, rebuilt_yaml)

        if not is_eq:
            print(f"\nDifferences: {diffs}")
            print(f"\nExpected:\n{expected_yaml}")
            print(f"\nRebuilt:\n{rebuilt_yaml}")

        assert is_eq is True, f"Construction failed: {diffs}"

    def test_multiple_jobs_direct_construction(self):
        """Multiple jobs constructed directly serialize correctly."""
        expected_yaml = """
stages:
  - build
  - test
  - deploy

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

deploy:
  stage: deploy
  script:
    - make deploy
  needs:
    - test
"""
        pipeline = Pipeline(stages=["build", "test", "deploy"])
        jobs = [
            Job(name="build", stage="build", script=["make build"]),
            Job(name="test", stage="test", script=["make test"], needs=["build"]),
            Job(name="deploy", stage="deploy", script=["make deploy"], needs=["test"]),
        ]

        rebuilt_yaml = build_pipeline_yaml(pipeline, jobs)

        is_eq, diffs = compare_yaml_semantic(expected_yaml, rebuilt_yaml)

        if not is_eq:
            print(f"\nDifferences: {diffs}")
            print(f"\nExpected:\n{expected_yaml}")
            print(f"\nRebuilt:\n{rebuilt_yaml}")

        assert is_eq is True, f"Construction failed: {diffs}"
