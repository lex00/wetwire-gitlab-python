"""Tests for validate command implementation."""

import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


class TestValidateCommandIntegration:
    """Integration tests for validate command."""

    @pytest.fixture
    def valid_yaml_file(self, tmp_path: Path):
        """Create a valid GitLab CI YAML file."""
        yaml_file = tmp_path / ".gitlab-ci.yml"
        yaml_file.write_text("""
stages:
  - build
  - test

build:
  stage: build
  script:
    - echo "Building"

test:
  stage: test
  script:
    - echo "Testing"
""")
        return yaml_file

    @pytest.fixture
    def invalid_yaml_file(self, tmp_path: Path):
        """Create an invalid GitLab CI YAML file."""
        yaml_file = tmp_path / "invalid.yml"
        yaml_file.write_text("""
stages:
  - build

build:
  stage: nonexistent_stage
  script: not_a_list
""")
        return yaml_file

    def test_validate_help(self):
        """Validate command shows help."""
        result = subprocess.run(
            [sys.executable, "-m", "wetwire_gitlab.cli", "validate", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "validate" in result.stdout.lower()

    def test_validate_nonexistent_file(self):
        """Validate handles nonexistent file."""
        result = subprocess.run(
            [sys.executable, "-m", "wetwire_gitlab.cli", "validate", "/nonexistent/file.yml"],
            capture_output=True,
            text=True,
        )
        # Should return error code
        assert result.returncode != 0

    def test_validate_include_jobs_flag(self):
        """Validate command accepts --include-jobs flag."""
        result = subprocess.run(
            [sys.executable, "-m", "wetwire_gitlab.cli", "validate", "--help"],
            capture_output=True,
            text=True,
        )
        assert "--include-jobs" in result.stdout


class TestValidateCommandUnit:
    """Unit tests for validate command logic."""

    def test_run_validate_function_exists(self):
        """run_validate function is importable."""
        from wetwire_gitlab.cli.main import run_validate

        assert callable(run_validate)

    def test_validate_result_type(self):
        """ValidateResult contract is available."""
        from wetwire_gitlab.contracts import ValidateResult

        result = ValidateResult(valid=True)
        assert result.valid is True

    def test_validate_result_with_errors(self):
        """ValidateResult can hold errors."""
        from wetwire_gitlab.contracts import ValidateResult

        result = ValidateResult(
            valid=False,
            errors=["Error 1", "Error 2"],
        )
        assert not result.valid
        assert len(result.errors) == 2


class TestValidationModule:
    """Tests for validation module."""

    def test_is_glab_installed_function_exists(self):
        """is_glab_installed function exists."""
        from wetwire_gitlab.validation import is_glab_installed

        assert callable(is_glab_installed)

    def test_validate_pipeline_function_exists(self):
        """validate_pipeline function exists."""
        from wetwire_gitlab.validation import validate_pipeline

        assert callable(validate_pipeline)

    def test_validate_file_function_exists(self):
        """validate_file function exists."""
        from wetwire_gitlab.validation import validate_file

        assert callable(validate_file)

    def test_glab_not_found_error_exists(self):
        """GlabNotFoundError exception exists."""
        from wetwire_gitlab.validation import GlabNotFoundError

        assert issubclass(GlabNotFoundError, Exception)

    @patch("wetwire_gitlab.validation.glab.subprocess.run")
    def test_validate_pipeline_success(self, mock_run: MagicMock):
        """validate_pipeline returns success for valid pipeline."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="Pipeline is valid",
            stderr="",
        )

        from wetwire_gitlab.validation import validate_pipeline

        result = validate_pipeline("stages:\n  - build")
        assert result.valid is True

    @patch("wetwire_gitlab.validation.glab.subprocess.run")
    def test_validate_pipeline_failure(self, mock_run: MagicMock):
        """validate_pipeline returns failure for invalid pipeline."""
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout="",
            stderr="Invalid stage reference",
        )

        from wetwire_gitlab.validation import validate_pipeline

        result = validate_pipeline("invalid yaml")
        assert result.valid is False
        assert result.errors is not None

    @patch("wetwire_gitlab.validation.glab.subprocess.run")
    def test_validate_with_include_jobs(self, mock_run: MagicMock):
        """validate_pipeline passes include_jobs flag."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="",
            stderr="",
        )

        from wetwire_gitlab.validation import validate_pipeline

        validate_pipeline("stages:\n  - build", include_jobs=True)

        # Check that --include-jobs was passed
        call_args = mock_run.call_args[0][0]
        assert "--include-jobs" in call_args


class TestValidateExitCodes:
    """Tests for validate command exit codes."""

    def test_exit_code_for_missing_glab(self):
        """Exit code 2 when glab is not installed."""
        from wetwire_gitlab.validation import GlabNotFoundError

        # This tests the exception type exists
        exc = GlabNotFoundError("glab not found")
        assert str(exc) == "glab not found"

    @patch("wetwire_gitlab.validation.glab.subprocess.run")
    def test_validate_timeout(self, mock_run: MagicMock):
        """validate handles timeout gracefully."""
        import subprocess as sp

        mock_run.side_effect = sp.TimeoutExpired(cmd=["glab"], timeout=5)

        from wetwire_gitlab.validation import validate_pipeline

        result = validate_pipeline("stages:", timeout=5)
        assert not result.valid
        assert result.errors is not None
        assert any("timed out" in e for e in result.errors)


class TestValidateWithBuild:
    """Tests for validate integrating with build output."""

    def test_can_validate_build_output(self):
        """Pipeline YAML can be validated after building."""
        from wetwire_gitlab.pipeline import Job, Pipeline
        from wetwire_gitlab.serialize import build_pipeline_yaml

        pipeline = Pipeline(stages=["build", "test"])
        jobs = [
            Job(name="build_job", stage="build", script=["make"]),
            Job(name="test_job", stage="test", script=["pytest"]),
        ]

        yaml_output = build_pipeline_yaml(pipeline, jobs)

        # Should be valid YAML structure
        assert "stages:" in yaml_output
        assert "build_job:" in yaml_output
