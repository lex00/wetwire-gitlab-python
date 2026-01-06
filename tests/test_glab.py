"""Tests for glab CLI integration."""

import subprocess
from unittest.mock import MagicMock, patch


class TestGlabValidation:
    """Tests for glab pipeline validation."""

    def test_validate_pipeline_success(self):
        """Validate a pipeline successfully."""
        from wetwire_gitlab.validation.glab import validate_pipeline

        yaml_content = """
stages:
  - build
  - test

build:
  stage: build
  script:
    - make build
"""

        with patch("wetwire_gitlab.validation.glab.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout="Syntax is correct",
                stderr="",
            )

            result = validate_pipeline(yaml_content)

        assert result.valid is True
        assert result.errors is None or len(result.errors) == 0

    def test_validate_pipeline_failure(self):
        """Handle invalid pipeline configuration."""
        from wetwire_gitlab.validation.glab import validate_pipeline

        yaml_content = "invalid: yaml: content:"

        with patch("wetwire_gitlab.validation.glab.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=1,
                stdout="",
                stderr="jobs config should contain at least one visible job",
            )

            result = validate_pipeline(yaml_content)

        assert result.valid is False
        assert result.errors is not None
        assert len(result.errors) > 0

    def test_validate_pipeline_with_include_jobs(self):
        """Validate pipeline with include-jobs option."""
        from wetwire_gitlab.validation.glab import validate_pipeline

        yaml_content = """
stages:
  - test
test:
  stage: test
  script: ["echo test"]
"""

        with patch("wetwire_gitlab.validation.glab.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout="Syntax is correct",
                stderr="",
            )

            validate_pipeline(yaml_content, include_jobs=True)

        # Check that --include-jobs was passed
        call_args = mock_run.call_args
        assert "--include-jobs" in call_args[0][0]

    def test_validate_pipeline_dry_run(self):
        """Validate pipeline with dry-run option."""
        from wetwire_gitlab.validation.glab import validate_pipeline

        yaml_content = """
stages:
  - test
test:
  stage: test
  script: ["echo test"]
"""

        with patch("wetwire_gitlab.validation.glab.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout="Syntax is correct",
                stderr="",
            )

            validate_pipeline(yaml_content, dry_run=True)

        # Check that --dry-run was passed
        call_args = mock_run.call_args
        assert "--dry-run" in call_args[0][0]

    def test_validate_pipeline_returns_merged_yaml(self):
        """Validate pipeline returns merged YAML content."""
        from wetwire_gitlab.validation.glab import validate_pipeline

        yaml_content = """
stages:
  - test
test:
  stage: test
  script: ["echo test"]
"""

        merged_yaml = """
stages:
  - test
test:
  stage: test
  script:
    - echo test
"""

        with patch("wetwire_gitlab.validation.glab.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout=merged_yaml,
                stderr="",
            )

            result = validate_pipeline(yaml_content)

        assert result.merged_yaml is not None


class TestGlabAvailability:
    """Tests for glab CLI availability checking."""

    def test_check_glab_installed(self):
        """Check if glab is installed."""
        from wetwire_gitlab.validation.glab import is_glab_installed

        with patch("wetwire_gitlab.validation.glab.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            assert is_glab_installed() is True

    def test_check_glab_not_installed(self):
        """Handle glab not being installed."""
        from wetwire_gitlab.validation.glab import is_glab_installed

        with patch("wetwire_gitlab.validation.glab.subprocess.run") as mock_run:
            mock_run.side_effect = FileNotFoundError()
            assert is_glab_installed() is False


class TestGlabValidationFromFile:
    """Tests for validating from a file path."""

    def test_validate_file(self):
        """Validate a pipeline from file path."""
        import tempfile
        from pathlib import Path

        from wetwire_gitlab.validation.glab import validate_file

        yaml_content = """
stages:
  - test
test:
  stage: test
  script: ["echo test"]
"""

        with tempfile.NamedTemporaryFile(
            suffix=".yml", delete=False, mode="w"
        ) as f:
            f.write(yaml_content)
            f.flush()

            with patch("wetwire_gitlab.validation.glab.subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(
                    returncode=0,
                    stdout="Syntax is correct",
                    stderr="",
                )

                result = validate_file(Path(f.name))

        assert result.valid is True


class TestGlabErrors:
    """Tests for error handling in glab integration."""

    def test_glab_not_found_error(self):
        """Handle glab command not found."""
        from wetwire_gitlab.validation.glab import GlabNotFoundError, validate_pipeline

        yaml_content = "stages: [test]"

        with patch("wetwire_gitlab.validation.glab.subprocess.run") as mock_run:
            mock_run.side_effect = FileNotFoundError()

            try:
                validate_pipeline(yaml_content)
                assert False, "Expected GlabNotFoundError"
            except GlabNotFoundError:
                pass

    def test_glab_timeout_error(self):
        """Handle glab command timeout."""
        from wetwire_gitlab.validation.glab import validate_pipeline

        yaml_content = "stages: [test]"

        with patch("wetwire_gitlab.validation.glab.subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired("glab", 30)

            result = validate_pipeline(yaml_content, timeout=30)

        assert result.valid is False
        assert result.errors is not None
        assert any("timed out" in e.lower() for e in result.errors)

    def test_glab_generic_error(self):
        """Handle generic subprocess errors."""
        from wetwire_gitlab.validation.glab import validate_pipeline

        yaml_content = "stages: [test]"

        with patch("wetwire_gitlab.validation.glab.subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.SubprocessError("Unknown error")

            result = validate_pipeline(yaml_content)

        assert result.valid is False
        assert result.errors is not None
