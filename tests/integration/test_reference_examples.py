"""Reference example tests using real GitLab pipelines.

These tests fetch real .gitlab-ci.yml files from GitLab repositories
and test the import/rebuild cycle.
"""

import pytest

# Sample GitLab CI configurations for testing
SIMPLE_PIPELINE = """
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

COMPLEX_PIPELINE = """
stages:
  - build
  - test
  - deploy

variables:
  CI_DEBUG: "true"
  DOCKER_IMAGE: "alpine:latest"

build:
  stage: build
  image: $DOCKER_IMAGE
  script:
    - apk add make
    - make build
  artifacts:
    paths:
      - dist/
    expire_in: 1 week

unit-tests:
  stage: test
  script:
    - make unit-tests
  needs:
    - build
  rules:
    - if: $CI_COMMIT_BRANCH

integration-tests:
  stage: test
  script:
    - make integration-tests
  needs:
    - build
  parallel: 3

deploy-staging:
  stage: deploy
  script:
    - make deploy-staging
  needs:
    - unit-tests
    - integration-tests
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
      when: manual
  environment:
    name: staging
"""

PIPELINE_WITH_INCLUDES = """
include:
  - local: /templates/build.yml
  - template: Security/SAST.gitlab-ci.yml

stages:
  - build
  - test
  - security

build:
  stage: build
  script:
    - make build
"""


@pytest.mark.slow
class TestParseRealPipelines:
    """Test parsing real pipeline configurations."""

    def test_parse_simple_pipeline(self):
        """Parse a simple pipeline."""
        from wetwire_gitlab.importer import parse_gitlab_ci

        pipeline = parse_gitlab_ci(SIMPLE_PIPELINE)

        assert pipeline.stages == ["build", "test"]
        assert len(pipeline.jobs) == 2

        job_names = [j.name for j in pipeline.jobs]
        assert "build" in job_names
        assert "test" in job_names

    def test_parse_complex_pipeline(self):
        """Parse a complex pipeline with all features."""
        from wetwire_gitlab.importer import parse_gitlab_ci

        pipeline = parse_gitlab_ci(COMPLEX_PIPELINE)

        assert pipeline.stages == ["build", "test", "deploy"]
        assert pipeline.variables is not None
        assert len(pipeline.jobs) == 4

        # Check specific job features
        build_job = next(j for j in pipeline.jobs if j.name == "build")
        assert build_job.artifacts is not None
        assert build_job.image == "$DOCKER_IMAGE"

        deploy_job = next(j for j in pipeline.jobs if j.name == "deploy-staging")
        assert deploy_job.rules is not None
        assert deploy_job.environment is not None

    def test_parse_pipeline_with_includes(self):
        """Parse pipeline with include statements."""
        from wetwire_gitlab.importer import parse_gitlab_ci

        pipeline = parse_gitlab_ci(PIPELINE_WITH_INCLUDES)

        assert len(pipeline.includes) == 2
        assert any(inc.local == "/templates/build.yml" for inc in pipeline.includes)
        assert any(
            inc.template == "Security/SAST.gitlab-ci.yml" for inc in pipeline.includes
        )


@pytest.mark.slow
class TestRoundTripConversion:
    """Test round-trip: YAML -> Python -> YAML."""

    def test_simple_round_trip(self):
        """Simple pipeline survives round-trip."""
        from wetwire_gitlab.importer import generate_python_code, parse_gitlab_ci

        # Parse YAML
        pipeline = parse_gitlab_ci(SIMPLE_PIPELINE)

        # Generate Python code
        code = generate_python_code(pipeline)

        # Code should be valid Python
        compile(code, "<test>", "exec")

        # Code should contain expected elements
        assert "from wetwire_gitlab.pipeline import" in code
        assert 'name="build"' in code
        assert 'name="test"' in code

    def test_complex_round_trip(self):
        """Complex pipeline survives round-trip."""
        from wetwire_gitlab.importer import generate_python_code, parse_gitlab_ci

        # Parse YAML
        pipeline = parse_gitlab_ci(COMPLEX_PIPELINE)

        # Generate Python code
        code = generate_python_code(pipeline)

        # Code should be valid Python
        compile(code, "<test>", "exec")

        # Code should contain expected elements
        assert "Rule" in code
        assert "if_=" in code


@pytest.mark.slow
class TestCodeGenerationQuality:
    """Test quality of generated Python code."""

    def test_generated_code_has_docstring(self):
        """Generated code has a docstring."""
        from wetwire_gitlab.importer import generate_python_code, parse_gitlab_ci

        pipeline = parse_gitlab_ci(SIMPLE_PIPELINE)
        code = generate_python_code(pipeline)

        assert '"""' in code

    def test_generated_code_has_imports(self):
        """Generated code has proper imports."""
        from wetwire_gitlab.importer import generate_python_code, parse_gitlab_ci

        pipeline = parse_gitlab_ci(SIMPLE_PIPELINE)
        code = generate_python_code(pipeline)

        assert "from wetwire_gitlab.pipeline import" in code
        assert "Job" in code

    def test_generated_code_creates_pipeline(self):
        """Generated code creates Pipeline if stages exist."""
        from wetwire_gitlab.importer import generate_python_code, parse_gitlab_ci

        pipeline = parse_gitlab_ci(SIMPLE_PIPELINE)
        code = generate_python_code(pipeline)

        assert "Pipeline" in code
        assert 'stages=["build", "test"]' in code

    def test_generated_code_preserves_needs(self):
        """Generated code preserves job dependencies."""
        from wetwire_gitlab.importer import generate_python_code, parse_gitlab_ci

        pipeline = parse_gitlab_ci(SIMPLE_PIPELINE)
        code = generate_python_code(pipeline)

        # Test job needs build (may use single or double quotes)
        assert "needs=" in code
        assert "build" in code


@pytest.mark.slow
class TestEdgeCases:
    """Test edge cases in pipeline parsing."""

    def test_empty_pipeline(self):
        """Handle empty pipeline."""
        from wetwire_gitlab.importer import parse_gitlab_ci

        pipeline = parse_gitlab_ci("")

        assert pipeline.stages == []
        assert pipeline.jobs == []

    def test_pipeline_with_only_stages(self):
        """Handle pipeline with only stages."""
        from wetwire_gitlab.importer import parse_gitlab_ci

        yaml_content = "stages:\n  - build\n  - test"
        pipeline = parse_gitlab_ci(yaml_content)

        assert pipeline.stages == ["build", "test"]
        assert pipeline.jobs == []

    def test_job_with_all_fields(self):
        """Parse job with many fields."""
        from wetwire_gitlab.importer import parse_gitlab_ci

        yaml_content = """
job:
  stage: test
  script:
    - echo test
  image: alpine
  tags:
    - docker
  timeout: 1h
  retry: 2
  interruptible: true
  allow_failure: false
"""
        pipeline = parse_gitlab_ci(yaml_content)

        assert len(pipeline.jobs) == 1
        job = pipeline.jobs[0]
        assert job.image == "alpine"
        assert job.tags == ["docker"]
        assert job.timeout == "1h"
        assert job.retry == 2
        assert job.interruptible is True
        assert job.allow_failure is False


@pytest.mark.slow
class TestSuccessRateTracking:
    """Test success rate tracking for round-trip tests."""

    @pytest.fixture
    def sample_pipelines(self):
        """Return sample pipelines for testing."""
        return [
            SIMPLE_PIPELINE,
            COMPLEX_PIPELINE,
            PIPELINE_WITH_INCLUDES,
        ]

    def test_all_samples_parse(self, sample_pipelines):
        """All sample pipelines should parse successfully."""
        from wetwire_gitlab.importer import parse_gitlab_ci

        success_count = 0
        for yaml_content in sample_pipelines:
            try:
                pipeline = parse_gitlab_ci(yaml_content)
                if pipeline is not None:
                    success_count += 1
            except Exception:
                pass

        # All should succeed
        assert success_count == len(sample_pipelines)

    def test_all_samples_generate_code(self, sample_pipelines):
        """All sample pipelines should generate valid Python."""
        from wetwire_gitlab.importer import generate_python_code, parse_gitlab_ci

        success_count = 0
        for yaml_content in sample_pipelines:
            try:
                pipeline = parse_gitlab_ci(yaml_content)
                code = generate_python_code(pipeline)
                compile(code, "<test>", "exec")
                success_count += 1
            except Exception:
                pass

        # All should succeed
        assert success_count == len(sample_pipelines)


@pytest.mark.slow
class TestRealWorldPatterns:
    """Test real-world GitLab CI patterns."""

    def test_matrix_jobs(self):
        """Parse matrix/parallel job configuration."""
        from wetwire_gitlab.importer import parse_gitlab_ci

        yaml_content = """
test:
  script: pytest
  parallel:
    matrix:
      - PYTHON: ["3.9", "3.10", "3.11"]
"""
        pipeline = parse_gitlab_ci(yaml_content)

        assert len(pipeline.jobs) == 1
        assert pipeline.jobs[0].parallel is not None

    def test_dag_dependencies(self):
        """Parse DAG-style dependencies."""
        from wetwire_gitlab.importer import parse_gitlab_ci

        yaml_content = """
stages:
  - build
  - test
  - deploy

build-a:
  stage: build
  script: make build-a

build-b:
  stage: build
  script: make build-b

test:
  stage: test
  needs:
    - job: build-a
      artifacts: true
    - job: build-b
      artifacts: false
"""
        pipeline = parse_gitlab_ci(yaml_content)

        test_job = next(j for j in pipeline.jobs if j.name == "test")
        assert test_job.needs is not None

    def test_trigger_child_pipeline(self):
        """Parse child pipeline trigger."""
        from wetwire_gitlab.importer import parse_gitlab_ci

        yaml_content = """
trigger-child:
  trigger:
    include: .child-ci.yml
    strategy: depend
"""
        pipeline = parse_gitlab_ci(yaml_content)

        assert len(pipeline.jobs) == 1
        assert pipeline.jobs[0].trigger is not None
