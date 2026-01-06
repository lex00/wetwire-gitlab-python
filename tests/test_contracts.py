"""Tests for contracts module."""



class TestJobRef:
    """Tests for JobRef dataclass."""

    def test_jobref_creation(self):
        """JobRef can be created with job name."""
        from wetwire_gitlab.contracts import JobRef

        ref = JobRef(job="build")
        assert ref.job == "build"

    def test_jobref_with_artifacts(self):
        """JobRef can specify artifacts download."""
        from wetwire_gitlab.contracts import JobRef

        ref = JobRef(job="build", artifacts=True)
        assert ref.artifacts is True

    def test_jobref_to_dict_simple(self):
        """JobRef.to_dict returns string for simple case."""
        from wetwire_gitlab.contracts import JobRef

        ref = JobRef(job="build")
        assert ref.to_dict() == "build"

    def test_jobref_to_dict_with_artifacts(self):
        """JobRef.to_dict returns dict when artifacts specified."""
        from wetwire_gitlab.contracts import JobRef

        ref = JobRef(job="build", artifacts=True)
        result = ref.to_dict()
        assert result == {"job": "build", "artifacts": True}

    def test_jobref_is_empty_false(self):
        """JobRef.is_empty returns False for valid ref."""
        from wetwire_gitlab.contracts import JobRef

        ref = JobRef(job="build")
        assert ref.is_empty() is False

    def test_jobref_is_empty_true(self):
        """JobRef.is_empty returns True for empty job."""
        from wetwire_gitlab.contracts import JobRef

        ref = JobRef(job="")
        assert ref.is_empty() is True


class TestDiscoveredJob:
    """Tests for DiscoveredJob dataclass."""

    def test_discovered_job_creation(self):
        """DiscoveredJob can be created."""
        from wetwire_gitlab.contracts import DiscoveredJob

        job = DiscoveredJob(
            name="build",
            variable_name="build_job",
            file_path="/path/to/jobs.py",
            line_number=10,
        )
        assert job.name == "build"
        assert job.variable_name == "build_job"
        assert job.file_path == "/path/to/jobs.py"
        assert job.line_number == 10

    def test_discovered_job_with_dependencies(self):
        """DiscoveredJob can have dependencies."""
        from wetwire_gitlab.contracts import DiscoveredJob

        job = DiscoveredJob(
            name="test",
            variable_name="test_job",
            file_path="/path/to/jobs.py",
            line_number=20,
            dependencies=["build_job"],
        )
        assert job.dependencies == ["build_job"]


class TestDiscoveredPipeline:
    """Tests for DiscoveredPipeline dataclass."""

    def test_discovered_pipeline_creation(self):
        """DiscoveredPipeline can be created."""
        from wetwire_gitlab.contracts import DiscoveredPipeline

        pipeline = DiscoveredPipeline(
            name="main",
            file_path="/path/to/pipeline.py",
            jobs=["build", "test"],
        )
        assert pipeline.name == "main"
        assert pipeline.jobs == ["build", "test"]


class TestResultTypes:
    """Tests for result dataclasses."""

    def test_build_result(self):
        """BuildResult can be created."""
        from wetwire_gitlab.contracts import BuildResult

        result = BuildResult(
            success=True,
            output_path=".gitlab-ci.yml",
            jobs_count=5,
        )
        assert result.success is True
        assert result.jobs_count == 5

    def test_build_result_with_errors(self):
        """BuildResult can contain errors."""
        from wetwire_gitlab.contracts import BuildResult

        result = BuildResult(
            success=False,
            output_path=None,
            jobs_count=0,
            errors=["Circular dependency detected"],
        )
        assert result.success is False
        assert "Circular dependency" in result.errors[0]

    def test_lint_result(self):
        """LintResult can be created."""
        from wetwire_gitlab.contracts import LintResult

        result = LintResult(
            success=True,
            issues=[],
            files_checked=10,
        )
        assert result.success is True
        assert result.files_checked == 10

    def test_lint_result_with_issues(self):
        """LintResult can contain issues."""
        from wetwire_gitlab.contracts import LintIssue, LintResult

        result = LintResult(
            success=False,
            issues=[
                LintIssue(
                    code="WGL001",
                    message="Use typed component wrapper",
                    file_path="/path/to/file.py",
                    line_number=10,
                )
            ],
            files_checked=5,
        )
        assert len(result.issues) == 1
        assert result.issues[0].code == "WGL001"

    def test_validate_result(self):
        """ValidateResult can be created."""
        from wetwire_gitlab.contracts import ValidateResult

        result = ValidateResult(
            valid=True,
            errors=None,
            merged_yaml=None,
        )
        assert result.valid is True

    def test_validate_result_invalid(self):
        """ValidateResult can contain validation errors."""
        from wetwire_gitlab.contracts import ValidateResult

        result = ValidateResult(
            valid=False,
            errors=["jobs:build:script is empty"],
            merged_yaml=None,
        )
        assert result.valid is False
        assert len(result.errors) == 1

    def test_list_result(self):
        """ListResult can be created."""
        from wetwire_gitlab.contracts import DiscoveredJob, ListResult

        result = ListResult(
            jobs=[
                DiscoveredJob(
                    name="build",
                    variable_name="build_job",
                    file_path="/path/to/jobs.py",
                    line_number=10,
                )
            ],
            pipelines=[],
        )
        assert len(result.jobs) == 1
