"""GitLab CI schema validation using JSON Schema.

This module provides functionality to validate GitLab CI YAML against
the official JSON schema from gitlab-org/gitlab repository.
"""

import json
import time
from pathlib import Path
from typing import Any

import yaml

from ..codegen.fetch import CI_SCHEMA_URL, fetch_url
from ..contracts import ValidateResult


class SchemaFetchError(Exception):
    """Raised when schema fetching fails."""

    pass


class SchemaValidationError(Exception):
    """Raised when schema validation encounters an error."""

    pass


def get_cache_dir() -> Path:
    """Get the cache directory for storing schemas.

    Returns:
        Path to cache directory.
    """
    # Use platform-appropriate cache directory
    cache_root = Path.home() / ".cache" / "wetwire-gitlab"
    cache_root.mkdir(parents=True, exist_ok=True)
    return cache_root


def get_cached_schema_path() -> Path:
    """Get path to cached schema file.

    Returns:
        Path where schema is cached.
    """
    return get_cache_dir() / "gitlab-ci-schema.json"


def is_cache_valid(cache_path: Path, max_age_days: int = 7) -> bool:
    """Check if cached schema is still valid.

    Args:
        cache_path: Path to cached schema file.
        max_age_days: Maximum age in days before cache is considered stale.

    Returns:
        True if cache exists and is fresh enough.
    """
    if not cache_path.exists():
        return False

    # Check file age
    mtime = cache_path.stat().st_mtime
    age_seconds = time.time() - mtime
    age_days = age_seconds / (24 * 60 * 60)

    return age_days < max_age_days


def fetch_schema(use_cache: bool = True, max_age_days: int = 7) -> dict[str, Any]:
    """Fetch the GitLab CI JSON schema.

    Args:
        use_cache: Whether to use cached schema if available.
        max_age_days: Maximum cache age in days.

    Returns:
        Parsed JSON schema as a dictionary.

    Raises:
        SchemaFetchError: If fetching fails.
    """
    cache_path = get_cached_schema_path()

    # Try to use cache if enabled
    if use_cache and is_cache_valid(cache_path, max_age_days):
        try:
            with open(cache_path) as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            # Cache is corrupted, fall through to fetch
            pass

    # Fetch fresh schema
    try:
        content = fetch_url(CI_SCHEMA_URL)
        schema = json.loads(content)

        # Save to cache
        try:
            with open(cache_path, "w") as f:
                json.dump(schema, f, indent=2)
        except OSError:
            # Non-fatal if we can't write cache
            pass

        return schema

    except Exception as e:
        raise SchemaFetchError(f"Failed to fetch GitLab CI schema: {e}") from e


def validate_yaml(
    yaml_content: str,
    use_cache: bool = True,
) -> ValidateResult:
    """Validate YAML content against GitLab CI JSON schema.

    Args:
        yaml_content: The YAML content to validate.
        use_cache: Whether to use cached schema.

    Returns:
        ValidateResult with validation status and any errors.
    """
    errors: list[str] = []

    # Parse YAML
    try:
        if not yaml_content or not yaml_content.strip():
            return ValidateResult(
                valid=False,
                errors=["YAML content is empty"],
                merged_yaml=None,
            )

        data = yaml.safe_load(yaml_content)

        if data is None:
            return ValidateResult(
                valid=False,
                errors=["YAML content is empty or invalid"],
                merged_yaml=None,
            )

    except yaml.YAMLError as e:
        return ValidateResult(
            valid=False,
            errors=[f"YAML syntax error: {e!s}"],
            merged_yaml=None,
        )

    # Fetch schema
    try:
        schema = fetch_schema(use_cache=use_cache)
    except SchemaFetchError as e:
        return ValidateResult(
            valid=False,
            errors=[f"Schema fetch error: {e!s}"],
            merged_yaml=None,
        )

    # Validate against schema
    try:
        from jsonschema import Draft7Validator

        # Create validator
        validator = Draft7Validator(schema)

        # Validate and collect errors
        validation_errors = list(validator.iter_errors(data))

        if validation_errors:
            for error in validation_errors:
                # Format error message with path
                path = ".".join(str(p) for p in error.path) if error.path else "root"
                errors.append(f"{path}: {error.message}")

            return ValidateResult(
                valid=False,
                errors=errors,
                merged_yaml=None,
            )

        return ValidateResult(
            valid=True,
            errors=None,
            merged_yaml=None,
        )

    except ImportError:
        return ValidateResult(
            valid=False,
            errors=[
                "jsonschema package is required for schema validation. "
                "Install with: pip install 'wetwire-gitlab[schema]'"
            ],
            merged_yaml=None,
        )
    except Exception as e:
        return ValidateResult(
            valid=False,
            errors=[f"Schema validation error: {e!s}"],
            merged_yaml=None,
        )


def validate_file(
    file_path: Path,
    use_cache: bool = True,
) -> ValidateResult:
    """Validate a YAML file against GitLab CI JSON schema.

    Args:
        file_path: Path to the YAML file to validate.
        use_cache: Whether to use cached schema.

    Returns:
        ValidateResult with validation status and any errors.
    """
    try:
        yaml_content = file_path.read_text()
        return validate_yaml(yaml_content, use_cache=use_cache)
    except OSError as e:
        return ValidateResult(
            valid=False,
            errors=[f"Failed to read file: {e!s}"],
            merged_yaml=None,
        )
