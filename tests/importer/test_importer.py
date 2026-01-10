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

        with tempfile.NamedTemporaryFile(suffix=".yml", delete=False, mode="w") as f:
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


class TestCodegenEdgeCases:
    """Tests for code generation edge cases to improve coverage."""

    def test_sanitize_identifier_starts_with_digit(self):
        """Test identifier sanitization when name starts with digit."""
        from wetwire_gitlab.importer import IRJob, IRPipeline, generate_python_code

        job = IRJob(name="1-build", stage="build", script=["make"])
        pipeline = IRPipeline(jobs=[job])

        code = generate_python_code(pipeline)

        # Should add underscore prefix for identifiers starting with digits
        assert "_1_build = Job(" in code

    def test_format_none_value(self):
        """Test formatting None values in job attributes."""
        from wetwire_gitlab.importer import IRJob, IRPipeline, generate_python_code

        job = IRJob(
            name="test",
            script=["pytest"],
            allow_failure=None,
        )
        pipeline = IRPipeline(jobs=[job])

        code = generate_python_code(pipeline)

        # None values should not appear in the generated code
        assert "allow_failure" not in code

    def test_format_false_boolean(self):
        """Test formatting False boolean values."""
        from wetwire_gitlab.importer import IRJob, IRPipeline, generate_python_code

        job = IRJob(
            name="deploy",
            script=["deploy.sh"],
            allow_failure=False,
        )
        pipeline = IRPipeline(jobs=[job])

        code = generate_python_code(pipeline)

        # False should be formatted as Python False
        assert "allow_failure=False" in code

    def test_format_empty_list_in_nested_value(self):
        """Test formatting empty list in nested values where it matters."""
        from wetwire_gitlab.importer.codegen import _format_value

        # Test empty list directly through _format_value
        result = _format_value([])
        assert result == "[]"

    def test_format_empty_dict_in_nested_value(self):
        """Test formatting empty dict in nested values where it matters."""
        from wetwire_gitlab.importer.codegen import _format_value

        # Test empty dict directly through _format_value
        result = _format_value({})
        assert result == "{}"

    def test_format_none_in_nested_value(self):
        """Test formatting None in nested values."""
        from wetwire_gitlab.importer.codegen import _format_value

        # Test None directly through _format_value
        result = _format_value(None)
        assert result == "None"

    def test_format_false_in_nested_value(self):
        """Test formatting False in nested values."""
        from wetwire_gitlab.importer.codegen import _format_value

        # Test False directly through _format_value
        result = _format_value(False)
        assert result == "False"

    def test_format_other_types_in_nested_value(self):
        """Test formatting of unusual value types using repr fallback."""
        from wetwire_gitlab.importer.codegen import _format_value

        # Test a tuple (not in the explicit type checks)
        result = _format_value((1, 2, 3))
        assert result == "(1, 2, 3)"

    def test_format_other_value_types(self):
        """Test formatting of unusual value types using repr fallback."""
        from wetwire_gitlab.importer import IRJob, IRPipeline, generate_python_code

        # Use a complex nested structure
        job = IRJob(
            name="test",
            script=["pytest"],
            parallel={"matrix": [{"VERSION": ["1", "2"]}]},
        )
        pipeline = IRPipeline(jobs=[job])

        code = generate_python_code(pipeline)

        # Should contain formatted parallel config
        assert "parallel=" in code

    def test_rule_with_allow_failure(self):
        """Test rule generation with allow_failure attribute."""
        from wetwire_gitlab.importer import (
            IRJob,
            IRPipeline,
            IRRule,
            generate_python_code,
        )

        rule = IRRule(
            if_="$CI_COMMIT_BRANCH",
            allow_failure=True,
        )
        job = IRJob(
            name="test",
            script=["pytest"],
            rules=[rule],
        )
        pipeline = IRPipeline(jobs=[job])

        code = generate_python_code(pipeline)

        assert "allow_failure=True" in code
        assert "Rule" in code

    def test_rule_with_changes(self):
        """Test rule generation with changes attribute."""
        from wetwire_gitlab.importer import (
            IRJob,
            IRPipeline,
            IRRule,
            generate_python_code,
        )

        rule = IRRule(
            if_="$CI_COMMIT_BRANCH",
            changes=["src/**/*.py"],
        )
        job = IRJob(
            name="test",
            script=["pytest"],
            rules=[rule],
        )
        pipeline = IRPipeline(jobs=[job])

        code = generate_python_code(pipeline)

        assert "changes=" in code
        assert "src/**/*.py" in code

    def test_rule_with_exists(self):
        """Test rule generation with exists attribute."""
        from wetwire_gitlab.importer import (
            IRJob,
            IRPipeline,
            IRRule,
            generate_python_code,
        )

        rule = IRRule(
            if_="$CI_COMMIT_BRANCH",
            exists=["Dockerfile"],
        )
        job = IRJob(
            name="build",
            script=["docker build"],
            rules=[rule],
        )
        pipeline = IRPipeline(jobs=[job])

        code = generate_python_code(pipeline)

        assert "exists=" in code
        assert "Dockerfile" in code

    def test_rule_with_variables(self):
        """Test rule generation with variables attribute."""
        from wetwire_gitlab.importer import (
            IRJob,
            IRPipeline,
            IRRule,
            generate_python_code,
        )

        rule = IRRule(
            if_="$CI_COMMIT_BRANCH",
            variables={"DEPLOY": "true"},
        )
        job = IRJob(
            name="deploy",
            script=["deploy.sh"],
            rules=[rule],
        )
        pipeline = IRPipeline(jobs=[job])

        code = generate_python_code(pipeline)

        assert "variables=" in code
        assert "DEPLOY" in code

    def test_rule_multiline_format(self):
        """Test rule generation with many attributes for multi-line format."""
        from wetwire_gitlab.importer import (
            IRJob,
            IRPipeline,
            IRRule,
            generate_python_code,
        )

        rule = IRRule(
            if_="$CI_COMMIT_BRANCH",
            when="manual",
            allow_failure=True,
            changes=["src/**/*.py"],
        )
        job = IRJob(
            name="test",
            script=["pytest"],
            rules=[rule],
        )
        pipeline = IRPipeline(jobs=[job])

        code = generate_python_code(pipeline)

        # With >2 parts, should use multi-line format
        assert "Rule(" in code
        assert "if_=" in code
        assert "when=" in code
        assert "allow_failure=" in code
        assert "changes=" in code

    def test_job_with_before_script(self):
        """Test job generation with before_script."""
        from wetwire_gitlab.importer import IRJob, IRPipeline, generate_python_code

        job = IRJob(
            name="build",
            script=["make build"],
            before_script=["pip install -r requirements.txt"],
        )
        pipeline = IRPipeline(jobs=[job])

        code = generate_python_code(pipeline)

        assert "before_script=" in code
        assert "pip install -r requirements.txt" in code

    def test_job_with_after_script(self):
        """Test job generation with after_script."""
        from wetwire_gitlab.importer import IRJob, IRPipeline, generate_python_code

        job = IRJob(
            name="test",
            script=["pytest"],
            after_script=["coverage report"],
        )
        pipeline = IRPipeline(jobs=[job])

        code = generate_python_code(pipeline)

        assert "after_script=" in code
        assert "coverage report" in code

    def test_job_with_image_string(self):
        """Test job generation with image as string."""
        from wetwire_gitlab.importer import IRJob, IRPipeline, generate_python_code

        job = IRJob(
            name="test",
            script=["pytest"],
            image="python:3.11",
        )
        pipeline = IRPipeline(jobs=[job])

        code = generate_python_code(pipeline)

        assert 'image="python:3.11"' in code

    def test_job_with_image_dict(self):
        """Test job generation with image as dict."""
        from wetwire_gitlab.importer import IRJob, IRPipeline, generate_python_code

        job = IRJob(
            name="test",
            script=["pytest"],
            image={"name": "python:3.11", "entrypoint": ["/bin/bash"]},
        )
        pipeline = IRPipeline(jobs=[job])

        code = generate_python_code(pipeline)

        assert "image=" in code
        assert "python:3.11" in code
        assert "entrypoint" in code

    def test_job_with_multiple_rules(self):
        """Test job generation with multiple rules."""
        from wetwire_gitlab.importer import (
            IRJob,
            IRPipeline,
            IRRule,
            generate_python_code,
        )

        rules = [
            IRRule(if_="$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH"),
            IRRule(when="manual", allow_failure=True),
        ]
        job = IRJob(
            name="deploy",
            script=["deploy.sh"],
            rules=rules,
        )
        pipeline = IRPipeline(jobs=[job])

        code = generate_python_code(pipeline)

        # Multiple rules should be on separate lines
        assert "rules=[" in code
        assert code.count("Rule(") == 2

    def test_job_with_cache(self):
        """Test job generation with cache."""
        from wetwire_gitlab.importer import IRJob, IRPipeline, generate_python_code

        job = IRJob(
            name="test",
            script=["pytest"],
            cache={"paths": [".cache/"], "key": "$CI_COMMIT_REF_SLUG"},
        )
        pipeline = IRPipeline(jobs=[job])

        code = generate_python_code(pipeline)

        assert "cache=" in code
        assert ".cache/" in code
        # Should trigger Cache import
        assert "from wetwire_gitlab.pipeline import" in code
        assert "Cache" in code

    def test_job_with_variables(self):
        """Test job generation with variables."""
        from wetwire_gitlab.importer import IRJob, IRPipeline, generate_python_code

        job = IRJob(
            name="build",
            script=["make build"],
            variables={"BUILD_DIR": "dist", "NODE_ENV": "production"},
        )
        pipeline = IRPipeline(jobs=[job])

        code = generate_python_code(pipeline)

        assert "variables=" in code
        assert "BUILD_DIR" in code
        assert "NODE_ENV" in code

    def test_job_with_tags(self):
        """Test job generation with tags."""
        from wetwire_gitlab.importer import IRJob, IRPipeline, generate_python_code

        job = IRJob(
            name="build",
            script=["make build"],
            tags=["docker", "linux"],
        )
        pipeline = IRPipeline(jobs=[job])

        code = generate_python_code(pipeline)

        assert "tags=" in code
        assert "docker" in code
        assert "linux" in code

    def test_job_with_when(self):
        """Test job generation with when attribute."""
        from wetwire_gitlab.importer import IRJob, IRPipeline, generate_python_code

        job = IRJob(
            name="deploy",
            script=["deploy.sh"],
            when="manual",
        )
        pipeline = IRPipeline(jobs=[job])

        code = generate_python_code(pipeline)

        assert 'when="manual"' in code

    def test_job_with_allow_failure_true(self):
        """Test job generation with allow_failure=True."""
        from wetwire_gitlab.importer import IRJob, IRPipeline, generate_python_code

        job = IRJob(
            name="test",
            script=["pytest"],
            allow_failure=True,
        )
        pipeline = IRPipeline(jobs=[job])

        code = generate_python_code(pipeline)

        assert "allow_failure=True" in code

    def test_job_with_timeout(self):
        """Test job generation with timeout."""
        from wetwire_gitlab.importer import IRJob, IRPipeline, generate_python_code

        job = IRJob(
            name="build",
            script=["make build"],
            timeout="2h",
        )
        pipeline = IRPipeline(jobs=[job])

        code = generate_python_code(pipeline)

        assert 'timeout="2h"' in code

    def test_job_with_retry(self):
        """Test job generation with retry."""
        from wetwire_gitlab.importer import IRJob, IRPipeline, generate_python_code

        job = IRJob(
            name="test",
            script=["pytest"],
            retry={"max": 2, "when": ["runner_system_failure"]},
        )
        pipeline = IRPipeline(jobs=[job])

        code = generate_python_code(pipeline)

        assert "retry=" in code
        assert "max" in code

    def test_job_with_extends_string(self):
        """Test job generation with extends as string."""
        from wetwire_gitlab.importer import IRJob, IRPipeline, generate_python_code

        job = IRJob(
            name="test",
            script=["pytest"],
            extends=".base",
        )
        pipeline = IRPipeline(jobs=[job])

        code = generate_python_code(pipeline)

        assert 'extends=".base"' in code

    def test_job_with_extends_list(self):
        """Test job generation with extends as list."""
        from wetwire_gitlab.importer import IRJob, IRPipeline, generate_python_code

        job = IRJob(
            name="test",
            script=["pytest"],
            extends=[".base", ".coverage"],
        )
        pipeline = IRPipeline(jobs=[job])

        code = generate_python_code(pipeline)

        assert "extends=" in code
        assert ".base" in code
        assert ".coverage" in code

    def test_job_with_dependencies(self):
        """Test job generation with dependencies."""
        from wetwire_gitlab.importer import IRJob, IRPipeline, generate_python_code

        job = IRJob(
            name="deploy",
            script=["deploy.sh"],
            dependencies=["build", "test"],
        )
        pipeline = IRPipeline(jobs=[job])

        code = generate_python_code(pipeline)

        assert "dependencies=" in code
        assert "build" in code
        assert "test" in code

    def test_job_with_services(self):
        """Test job generation with services."""
        from wetwire_gitlab.importer import IRJob, IRPipeline, generate_python_code

        job = IRJob(
            name="test",
            script=["pytest"],
            services=["postgres:13", "redis:6"],
        )
        pipeline = IRPipeline(jobs=[job])

        code = generate_python_code(pipeline)

        assert "services=" in code
        assert "postgres:13" in code
        assert "redis:6" in code

    def test_job_with_environment_string(self):
        """Test job generation with environment as string."""
        from wetwire_gitlab.importer import IRJob, IRPipeline, generate_python_code

        job = IRJob(
            name="deploy",
            script=["deploy.sh"],
            environment="production",
        )
        pipeline = IRPipeline(jobs=[job])

        code = generate_python_code(pipeline)

        assert 'environment="production"' in code

    def test_job_with_environment_dict(self):
        """Test job generation with environment as dict."""
        from wetwire_gitlab.importer import IRJob, IRPipeline, generate_python_code

        job = IRJob(
            name="deploy",
            script=["deploy.sh"],
            environment={"name": "production", "url": "https://example.com"},
        )
        pipeline = IRPipeline(jobs=[job])

        code = generate_python_code(pipeline)

        assert "environment=" in code
        assert "production" in code
        assert "https://example.com" in code

    def test_job_with_coverage(self):
        """Test job generation with coverage regex."""
        from wetwire_gitlab.importer import IRJob, IRPipeline, generate_python_code

        job = IRJob(
            name="test",
            script=["pytest"],
            coverage=r"/Coverage: \d+\.\d+/",
        )
        pipeline = IRPipeline(jobs=[job])

        code = generate_python_code(pipeline)

        assert "coverage=" in code
        assert "Coverage" in code

    def test_job_with_resource_group(self):
        """Test job generation with resource_group."""
        from wetwire_gitlab.importer import IRJob, IRPipeline, generate_python_code

        job = IRJob(
            name="deploy",
            script=["deploy.sh"],
            resource_group="production",
        )
        pipeline = IRPipeline(jobs=[job])

        code = generate_python_code(pipeline)

        assert 'resource_group="production"' in code

    def test_job_with_interruptible(self):
        """Test job generation with interruptible."""
        from wetwire_gitlab.importer import IRJob, IRPipeline, generate_python_code

        job = IRJob(
            name="test",
            script=["pytest"],
            interruptible=True,
        )
        pipeline = IRPipeline(jobs=[job])

        code = generate_python_code(pipeline)

        assert "interruptible=True" in code

    def test_job_with_parallel(self):
        """Test job generation with parallel."""
        from wetwire_gitlab.importer import IRJob, IRPipeline, generate_python_code

        job = IRJob(
            name="test",
            script=["pytest"],
            parallel=4,
        )
        pipeline = IRPipeline(jobs=[job])

        code = generate_python_code(pipeline)

        assert "parallel=4" in code

    def test_job_with_trigger(self):
        """Test job generation with trigger."""
        from wetwire_gitlab.importer import IRJob, IRPipeline, generate_python_code

        job = IRJob(
            name="trigger-downstream",
            script=None,
            trigger={"project": "group/downstream", "branch": "main"},
        )
        pipeline = IRPipeline(jobs=[job])

        code = generate_python_code(pipeline)

        assert "trigger=" in code
        assert "group/downstream" in code

    def test_job_with_release(self):
        """Test job generation with release."""
        from wetwire_gitlab.importer import IRJob, IRPipeline, generate_python_code

        job = IRJob(
            name="release",
            script=["echo 'Creating release'"],
            release={"tag_name": "v1.0.0", "description": "Release 1.0.0"},
        )
        pipeline = IRPipeline(jobs=[job])

        code = generate_python_code(pipeline)

        assert "release=" in code
        assert "v1.0.0" in code

    def test_pipeline_with_cache_import(self):
        """Test that Cache is imported when jobs have cache."""
        from wetwire_gitlab.importer import IRJob, IRPipeline, generate_python_code

        job = IRJob(
            name="test",
            script=["pytest"],
            cache={"paths": [".cache/"]},
        )
        pipeline = IRPipeline(stages=["test"], jobs=[job])

        code = generate_python_code(pipeline)

        # Should import Cache
        assert "Cache" in code
        # Should be in sorted import list
        assert "from wetwire_gitlab.pipeline import" in code

    def test_pipeline_with_artifacts_import(self):
        """Test that Artifacts is imported when jobs have artifacts."""
        from wetwire_gitlab.importer import IRJob, IRPipeline, generate_python_code

        job = IRJob(
            name="build",
            script=["make build"],
            artifacts={"paths": ["dist/"]},
        )
        pipeline = IRPipeline(stages=["build"], jobs=[job])

        code = generate_python_code(pipeline)

        # Should import Artifacts
        assert "Artifacts" in code
        # Should be in sorted import list
        assert "from wetwire_gitlab.pipeline import" in code

    def test_job_with_needs(self):
        """Test job generation with needs."""
        from wetwire_gitlab.importer import IRJob, IRPipeline, generate_python_code

        job = IRJob(
            name="deploy",
            script=["deploy.sh"],
            needs=["build", "test"],
        )
        pipeline = IRPipeline(jobs=[job])

        code = generate_python_code(pipeline)

        assert "needs=" in code
        assert "build" in code
        assert "test" in code

    def test_complex_nested_values(self):
        """Test formatting of complex nested structures."""
        from wetwire_gitlab.importer import IRJob, IRPipeline, generate_python_code

        job = IRJob(
            name="test",
            script=["pytest"],
            parallel={
                "matrix": [
                    {"PLATFORM": ["linux", "mac"], "VERSION": ["3.9", "3.10"]},
                ]
            },
        )
        pipeline = IRPipeline(jobs=[job])

        code = generate_python_code(pipeline)

        assert "parallel=" in code
        assert "matrix" in code
        assert "PLATFORM" in code
        assert "VERSION" in code
