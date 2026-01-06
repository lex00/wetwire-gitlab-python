"""GitLab CLI (glab) integration for pipeline validation.

This module provides integration with the glab CLI tool for validating
GitLab CI/CD pipeline configurations.
"""

import subprocess
import tempfile
from pathlib import Path

from ..contracts import ValidateResult


class GlabNotFoundError(Exception):
    """Raised when the glab CLI is not installed or not found."""


def is_glab_installed() -> bool:
    """Check if the glab CLI is installed and available.

    Returns:
        True if glab is installed and accessible.
    """
    try:
        subprocess.run(
            ["glab", "--version"],
            capture_output=True,
            check=False,
        )
        return True
    except FileNotFoundError:
        return False


def validate_pipeline(
    yaml_content: str,
    *,
    include_jobs: bool = False,
    dry_run: bool = False,
    timeout: int | None = None,
) -> ValidateResult:
    """Validate a pipeline configuration using glab.

    Args:
        yaml_content: The YAML content to validate.
        include_jobs: Include job information in validation output.
        dry_run: Perform a dry run without actually validating.
        timeout: Timeout in seconds for the glab command.

    Returns:
        ValidateResult with validation status and any errors.

    Raises:
        GlabNotFoundError: If glab CLI is not installed.
    """
    # Write YAML content to a temporary file
    with tempfile.NamedTemporaryFile(
        suffix=".yml", delete=False, mode="w"
    ) as f:
        f.write(yaml_content)
        f.flush()
        temp_path = Path(f.name)

    try:
        return validate_file(
            temp_path,
            include_jobs=include_jobs,
            dry_run=dry_run,
            timeout=timeout,
        )
    finally:
        temp_path.unlink(missing_ok=True)


def validate_file(
    file_path: Path,
    *,
    include_jobs: bool = False,
    dry_run: bool = False,
    timeout: int | None = None,
) -> ValidateResult:
    """Validate a pipeline configuration file using glab.

    Args:
        file_path: Path to the YAML file to validate.
        include_jobs: Include job information in validation output.
        dry_run: Perform a dry run without actually validating.
        timeout: Timeout in seconds for the glab command.

    Returns:
        ValidateResult with validation status and any errors.

    Raises:
        GlabNotFoundError: If glab CLI is not installed.
    """
    cmd = ["glab", "ci", "lint", str(file_path)]

    if include_jobs:
        cmd.append("--include-jobs")

    if dry_run:
        cmd.append("--dry-run")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )

        if result.returncode == 0:
            return ValidateResult(
                valid=True,
                errors=None,
                merged_yaml=result.stdout if result.stdout else None,
            )
        else:
            # Parse error messages from stderr
            errors = []
            if result.stderr:
                errors.append(result.stderr.strip())
            if result.stdout and "error" in result.stdout.lower():
                errors.append(result.stdout.strip())

            return ValidateResult(
                valid=False,
                errors=errors if errors else ["Validation failed"],
                merged_yaml=None,
            )

    except FileNotFoundError:
        raise GlabNotFoundError(
            "glab CLI not found. Install it from https://gitlab.com/gitlab-org/cli"
        )

    except subprocess.TimeoutExpired:
        return ValidateResult(
            valid=False,
            errors=[f"Validation timed out after {timeout} seconds"],
            merged_yaml=None,
        )

    except subprocess.SubprocessError as e:
        return ValidateResult(
            valid=False,
            errors=[f"Subprocess error: {e!s}"],
            merged_yaml=None,
        )
