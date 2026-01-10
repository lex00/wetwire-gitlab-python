"""Tests for Job reference support in needs/dependencies.

Tests for Issue #79: Job Reference Support
"""

import pytest

from wetwire_gitlab.pipeline import Job
from wetwire_gitlab.serialize import build_pipeline_yaml, to_dict


@pytest.mark.slow
class TestJobReferenceInNeeds:
    """Tests for using Job instances in needs field."""

    def test_needs_with_job_instance(self):
        """needs can accept Job instance directly."""
        build = Job(name="build", stage="build", script=["make build"])
        test = Job(name="test", stage="test", script=["make test"], needs=[build])

        result = to_dict(test)
        assert result["needs"] == ["build"]

    def test_needs_with_string_still_works(self):
        """needs continues to work with string (backwards compatible)."""
        test = Job(name="test", stage="test", script=["make test"], needs=["build"])

        result = to_dict(test)
        assert result["needs"] == ["build"]

    def test_needs_with_mixed_references(self):
        """needs can mix Job instances and strings."""
        build = Job(name="build", stage="build", script=["make build"])
        test = Job(
            name="test",
            stage="test",
            script=["make test"],
            needs=[build, "lint"],  # Mix of Job instance and string
        )

        result = to_dict(test)
        assert result["needs"] == ["build", "lint"]

    def test_needs_with_multiple_jobs(self):
        """needs can accept multiple Job instances."""
        build = Job(name="build", stage="build", script=["make build"])
        lint = Job(name="lint", stage="test", script=["make lint"])
        deploy = Job(
            name="deploy",
            stage="deploy",
            script=["make deploy"],
            needs=[build, lint],
        )

        result = to_dict(deploy)
        assert result["needs"] == ["build", "lint"]


@pytest.mark.slow
class TestJobReferenceInDependencies:
    """Tests for using Job instances in dependencies field."""

    def test_dependencies_with_job_instance(self):
        """dependencies can accept Job instance directly."""
        build = Job(name="build", stage="build", script=["make build"])
        test = Job(
            name="test",
            stage="test",
            script=["make test"],
            dependencies=[build],
        )

        result = to_dict(test)
        assert result["dependencies"] == ["build"]

    def test_dependencies_with_string_still_works(self):
        """dependencies continues to work with string."""
        test = Job(
            name="test",
            stage="test",
            script=["make test"],
            dependencies=["build"],
        )

        result = to_dict(test)
        assert result["dependencies"] == ["build"]


@pytest.mark.slow
class TestJobReferenceInBuildYaml:
    """Tests for Job references in full YAML build."""

    def test_build_yaml_with_job_references(self):
        """Build YAML with Job references produces correct output."""
        from wetwire_gitlab.pipeline import Pipeline

        pipeline = Pipeline(stages=["build", "test", "deploy"])
        build = Job(name="build", stage="build", script=["make build"])
        test = Job(name="test", stage="test", script=["make test"], needs=[build])
        deploy = Job(
            name="deploy", stage="deploy", script=["make deploy"], needs=[test]
        )

        yaml_output = build_pipeline_yaml(pipeline, [build, test, deploy])

        assert "needs:" in yaml_output
        assert "- build" in yaml_output

    def test_build_yaml_preserves_job_order(self):
        """Build YAML respects job definition order."""
        from wetwire_gitlab.pipeline import Pipeline

        pipeline = Pipeline(stages=["build", "test"])
        build = Job(name="build", stage="build", script=["make build"])
        test = Job(name="test", stage="test", script=["make test"], needs=[build])

        yaml_output = build_pipeline_yaml(pipeline, [build, test])

        # "build" should appear before "test" in the output
        build_pos = yaml_output.find("build:")
        test_pos = yaml_output.find("test:")
        assert build_pos < test_pos


@pytest.mark.slow
class TestJobReferenceExtractsName:
    """Tests for extracting job name from Job instance."""

    def test_job_name_extracted_correctly(self):
        """Job name is extracted from name field."""
        build = Job(name="my-build-job", stage="build", script=["make"])
        test = Job(name="test", stage="test", script=["make test"], needs=[build])

        result = to_dict(test)
        assert result["needs"] == ["my-build-job"]

    def test_job_with_empty_name_uses_variable(self):
        """Job without name field handles gracefully."""
        # This tests edge case handling
        build = Job(stage="build", script=["make"])  # No name set (empty string)
        test = Job(name="test", stage="test", script=["make test"], needs=[build])

        result = to_dict(test)
        # Should still work - empty string is serialized
        assert result["needs"] == [""]
