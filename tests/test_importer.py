"""Tests for YAML importer module."""

import tempfile
from pathlib import Path


class TestImporterIR:
    """Tests for importer intermediate representation types."""

    def test_ir_job_creation(self):
        """Create IRJob with basic fields."""
        from wetwire_gitlab.importer import IRJob

        job = IRJob(
            name="build",
            stage="build",
            script=["make build"],
        )

        assert job.name == "build"
        assert job.stage == "build"
        assert job.script == ["make build"]

    def test_ir_job_with_rules(self):
        """Create IRJob with rules."""
        from wetwire_gitlab.importer import IRJob, IRRule

        rules = [IRRule(if_="$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH")]
        job = IRJob(
            name="deploy",
            stage="deploy",
            script=["deploy.sh"],
            rules=rules,
        )

        assert len(job.rules) == 1
        assert job.rules[0].if_ == "$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH"

    def test_ir_pipeline_creation(self):
        """Create IRPipeline with basic fields."""
        from wetwire_gitlab.importer import IRPipeline

        pipeline = IRPipeline(
            stages=["build", "test", "deploy"],
        )

        assert pipeline.stages == ["build", "test", "deploy"]

    def test_ir_pipeline_with_jobs(self):
        """Create IRPipeline with jobs."""
        from wetwire_gitlab.importer import IRJob, IRPipeline

        jobs = [
            IRJob(name="build", stage="build", script=["make"]),
            IRJob(name="test", stage="test", script=["pytest"]),
        ]
        pipeline = IRPipeline(stages=["build", "test"], jobs=jobs)

        assert len(pipeline.jobs) == 2

    def test_ir_rule_creation(self):
        """Create IRRule with conditions."""
        from wetwire_gitlab.importer import IRRule

        rule = IRRule(
            if_="$CI_COMMIT_BRANCH",
            when="manual",
            allow_failure=True,
        )

        assert rule.if_ == "$CI_COMMIT_BRANCH"
        assert rule.when == "manual"
        assert rule.allow_failure is True

    def test_ir_include_creation(self):
        """Create IRInclude for tracking include files."""
        from wetwire_gitlab.importer import IRInclude

        include = IRInclude(
            local="/.gitlab/ci/build.yml",
        )

        assert include.local == "/.gitlab/ci/build.yml"

    def test_ir_include_remote(self):
        """Create IRInclude for remote file."""
        from wetwire_gitlab.importer import IRInclude

        include = IRInclude(
            remote="https://gitlab.com/example/config.yml",
        )

        assert include.remote == "https://gitlab.com/example/config.yml"


class TestYAMLParser:
    """Tests for YAML parsing functionality."""

    def test_parse_simple_pipeline(self):
        """Parse a simple pipeline YAML."""
        from wetwire_gitlab.importer import parse_gitlab_ci

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
    - pytest
"""

        pipeline = parse_gitlab_ci(yaml_content)

        assert pipeline.stages == ["build", "test"]
        assert len(pipeline.jobs) == 2

    def test_parse_job_with_rules(self):
        """Parse job with rules."""
        from wetwire_gitlab.importer import parse_gitlab_ci

        yaml_content = """
stages:
  - deploy

deploy:
  stage: deploy
  script:
    - deploy.sh
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
      when: always
    - when: manual
"""

        pipeline = parse_gitlab_ci(yaml_content)
        deploy_job = next(j for j in pipeline.jobs if j.name == "deploy")

        assert len(deploy_job.rules) == 2

    def test_parse_job_with_artifacts(self):
        """Parse job with artifacts."""
        from wetwire_gitlab.importer import parse_gitlab_ci

        yaml_content = """
build:
  script:
    - make build
  artifacts:
    paths:
      - build/
    expire_in: 1 week
"""

        pipeline = parse_gitlab_ci(yaml_content)
        build_job = next(j for j in pipeline.jobs if j.name == "build")

        assert build_job.artifacts is not None
        assert "paths" in build_job.artifacts
        assert build_job.artifacts["paths"] == ["build/"]

    def test_parse_job_with_cache(self):
        """Parse job with cache."""
        from wetwire_gitlab.importer import parse_gitlab_ci

        yaml_content = """
test:
  script:
    - pytest
  cache:
    paths:
      - .cache/
    key: "$CI_COMMIT_REF_SLUG"
"""

        pipeline = parse_gitlab_ci(yaml_content)
        test_job = next(j for j in pipeline.jobs if j.name == "test")

        assert test_job.cache is not None
        assert "paths" in test_job.cache

    def test_parse_includes(self):
        """Parse pipeline with includes."""
        from wetwire_gitlab.importer import parse_gitlab_ci

        yaml_content = """
include:
  - local: /.gitlab/ci/build.yml
  - remote: https://gitlab.com/example/ci.yml
  - template: Security/SAST.gitlab-ci.yml

stages:
  - build
"""

        pipeline = parse_gitlab_ci(yaml_content)

        assert len(pipeline.includes) == 3

    def test_parse_variables(self):
        """Parse pipeline with variables."""
        from wetwire_gitlab.importer import parse_gitlab_ci

        yaml_content = """
variables:
  BUILD_DIR: "build"
  TEST_COVERAGE: "80"

build:
  script:
    - make build
"""

        pipeline = parse_gitlab_ci(yaml_content)

        assert pipeline.variables is not None
        assert pipeline.variables["BUILD_DIR"] == "build"

    def test_parse_default(self):
        """Parse pipeline with default configuration."""
        from wetwire_gitlab.importer import parse_gitlab_ci

        yaml_content = """
default:
  image: python:3.11
  before_script:
    - pip install -r requirements.txt

build:
  script:
    - make build
"""

        pipeline = parse_gitlab_ci(yaml_content)

        assert pipeline.default is not None
        assert pipeline.default.get("image") == "python:3.11"


class TestYAMLParserFromFile:
    """Tests for parsing from file."""

    def test_parse_file(self):
        """Parse pipeline from file path."""
        from wetwire_gitlab.importer import parse_gitlab_ci_file

        yaml_content = """
stages:
  - test

test:
  script:
    - echo test
"""

        with tempfile.NamedTemporaryFile(
            suffix=".yml", delete=False, mode="w"
        ) as f:
            f.write(yaml_content)
            f.flush()
            pipeline = parse_gitlab_ci_file(Path(f.name))

        assert pipeline.stages == ["test"]
        assert len(pipeline.jobs) == 1

    def test_parse_empty_file(self):
        """Parse empty YAML file."""
        from wetwire_gitlab.importer import parse_gitlab_ci

        pipeline = parse_gitlab_ci("")

        assert pipeline.stages == []
        assert pipeline.jobs == []


class TestIncludeResolution:
    """Tests for include resolution tracking."""

    def test_track_unresolved_includes(self):
        """Track includes that need resolution."""
        from wetwire_gitlab.importer import parse_gitlab_ci

        yaml_content = """
include:
  - local: /.gitlab/ci/build.yml
  - project: group/project
    file: /templates/ci.yml

stages:
  - build
"""

        pipeline = parse_gitlab_ci(yaml_content)

        # Includes should be tracked
        assert len(pipeline.includes) == 2
        assert any(i.local == "/.gitlab/ci/build.yml" for i in pipeline.includes)

    def test_include_with_component(self):
        """Parse include with component reference."""
        from wetwire_gitlab.importer import parse_gitlab_ci

        yaml_content = """
include:
  - component: gitlab.com/components/sast@main

stages:
  - test
"""

        pipeline = parse_gitlab_ci(yaml_content)

        assert len(pipeline.includes) == 1
        assert pipeline.includes[0].component == "gitlab.com/components/sast@main"
