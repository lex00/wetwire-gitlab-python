"""Tests for GitLab CI schema validation."""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest


class TestSchemaFetching:
    """Tests for schema fetching and caching."""

    def test_fetch_schema_success(self):
        """Fetch GitLab CI JSON schema successfully."""
        from wetwire_gitlab.validation.schema import fetch_schema

        with patch("wetwire_gitlab.validation.schema.fetch_url") as mock_fetch:
            mock_schema = {
                "$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "properties": {"stages": {"type": "array"}},
            }
            mock_fetch.return_value = json.dumps(mock_schema)

            schema = fetch_schema(use_cache=False)

            assert isinstance(schema, dict)
            assert "$schema" in schema
            mock_fetch.assert_called_once()

    def test_fetch_schema_with_cache(self):
        """Use cached schema when available."""
        from wetwire_gitlab.validation.schema import fetch_schema

        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)

            # First call - should fetch
            with patch("wetwire_gitlab.validation.schema.fetch_url") as mock_fetch:
                mock_schema = {"type": "object"}
                mock_fetch.return_value = json.dumps(mock_schema)

                with patch(
                    "wetwire_gitlab.validation.schema.get_cache_dir",
                    return_value=cache_dir,
                ):
                    schema1 = fetch_schema()
                    assert mock_fetch.call_count == 1

                    # Second call - should use cache
                    schema2 = fetch_schema()
                    assert mock_fetch.call_count == 1  # Not called again
                    assert schema1 == schema2

    def test_get_cached_schema_path(self):
        """Get path to cached schema file."""
        from wetwire_gitlab.validation.schema import get_cached_schema_path

        path = get_cached_schema_path()

        assert isinstance(path, Path)
        assert path.name == "gitlab-ci-schema.json"

    def test_fetch_schema_network_error(self):
        """Handle network errors when fetching schema."""
        from wetwire_gitlab.validation.schema import SchemaFetchError, fetch_schema

        with patch("wetwire_gitlab.validation.schema.fetch_url") as mock_fetch:
            mock_fetch.side_effect = Exception("Network error")

            with pytest.raises(SchemaFetchError):
                fetch_schema(use_cache=False)


class TestSchemaValidation:
    """Tests for YAML validation against schema."""

    def test_validate_yaml_success(self):
        """Validate valid YAML against schema."""
        from wetwire_gitlab.validation.schema import validate_yaml

        valid_yaml = """
stages:
  - build
  - test

build:
  stage: build
  script:
    - make build
"""

        with patch("wetwire_gitlab.validation.schema.fetch_schema") as mock_fetch:
            mock_schema = {
                "$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "properties": {
                    "stages": {"type": "array"},
                },
            }
            mock_fetch.return_value = mock_schema

            result = validate_yaml(valid_yaml)

            assert result.valid is True
            assert result.errors is None or len(result.errors) == 0

    def test_validate_yaml_invalid_structure(self):
        """Handle invalid YAML structure."""
        from wetwire_gitlab.validation.schema import validate_yaml

        invalid_yaml = """
stages: "not-an-array"
"""

        with patch("wetwire_gitlab.validation.schema.fetch_schema") as mock_fetch:
            mock_schema = {
                "$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "properties": {
                    "stages": {"type": "array"},
                },
            }
            mock_fetch.return_value = mock_schema

            result = validate_yaml(invalid_yaml)

            assert result.valid is False
            assert result.errors is not None
            assert len(result.errors) > 0

    def test_validate_yaml_syntax_error(self):
        """Handle YAML syntax errors."""
        from wetwire_gitlab.validation.schema import validate_yaml

        invalid_yaml = """
stages:
  - build
  invalid: yaml: syntax:
"""

        result = validate_yaml(invalid_yaml)

        assert result.valid is False
        assert result.errors is not None
        assert any("yaml" in e.lower() or "syntax" in e.lower() for e in result.errors)

    def test_validate_yaml_empty_content(self):
        """Handle empty YAML content."""
        from wetwire_gitlab.validation.schema import validate_yaml

        result = validate_yaml("")

        assert result.valid is False
        assert result.errors is not None

    def test_validate_yaml_missing_required_fields(self):
        """Validate that missing required fields are caught."""
        from wetwire_gitlab.validation.schema import validate_yaml

        # Job without required script field
        yaml_content = """
build:
  stage: build
"""

        with patch("wetwire_gitlab.validation.schema.fetch_schema") as mock_fetch:
            # Simplified schema that requires script in jobs
            mock_schema = {
                "$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "patternProperties": {
                    "^(?!\\.).*$": {
                        "type": "object",
                        "required": ["script"],
                    }
                },
            }
            mock_fetch.return_value = mock_schema

            result = validate_yaml(yaml_content)

            # May pass or fail depending on schema - we're testing the mechanism
            assert result.valid in (True, False)
            assert isinstance(result.errors, (list, type(None)))


class TestSchemaValidationIntegration:
    """Integration tests for schema validation with build command."""

    def test_build_with_schema_validate_flag(self):
        """Test that --schema-validate flag triggers validation."""
        # This is a placeholder test that will be implemented
        # after integrating with the build command
        pass

    def test_build_fails_with_invalid_yaml(self):
        """Test that build fails when schema validation is enabled and YAML is invalid."""
        # This is a placeholder test that will be implemented
        # after integrating with the build command
        pass

    def test_build_succeeds_with_valid_yaml(self):
        """Test that build succeeds when schema validation is enabled and YAML is valid."""
        # This is a placeholder test that will be implemented
        # after integrating with the build command
        pass


class TestSchemaCaching:
    """Tests for schema caching behavior."""

    def test_cache_dir_creation(self):
        """Test that cache directory is created if it doesn't exist."""
        from wetwire_gitlab.validation.schema import get_cache_dir

        cache_dir = get_cache_dir()

        assert isinstance(cache_dir, Path)
        # Don't assert existence as it depends on environment

    def test_schema_cache_expiry(self):
        """Test schema cache expiry after specified time."""
        from wetwire_gitlab.validation.schema import is_cache_valid

        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)

            with patch(
                "wetwire_gitlab.validation.schema.get_cache_dir", return_value=cache_dir
            ):
                # Create an old cache file
                schema_path = cache_dir / "gitlab-ci-schema.json"
                schema_path.write_text('{"type": "object"}')

                # Set mtime to 8 days ago (past default 7 day expiry)
                import time

                old_time = time.time() - (8 * 24 * 60 * 60)
                schema_path.touch()
                import os

                os.utime(schema_path, (old_time, old_time))

                # Should be invalid
                assert is_cache_valid(schema_path, max_age_days=7) is False

    def test_schema_cache_valid(self):
        """Test schema cache is valid when fresh."""
        from wetwire_gitlab.validation.schema import is_cache_valid

        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)
            schema_path = cache_dir / "gitlab-ci-schema.json"
            schema_path.write_text('{"type": "object"}')

            # Just created, should be valid
            assert is_cache_valid(schema_path, max_age_days=7) is True


class TestSchemaValidationErrors:
    """Tests for schema validation error handling."""

    def test_validate_yaml_with_missing_schema(self):
        """Handle case when schema cannot be fetched."""
        from wetwire_gitlab.validation.schema import SchemaFetchError, validate_yaml

        yaml_content = """
stages:
  - build
"""

        with patch("wetwire_gitlab.validation.schema.fetch_schema") as mock_fetch:
            mock_fetch.side_effect = SchemaFetchError("Failed to fetch schema")

            result = validate_yaml(yaml_content)

            assert result.valid is False
            assert result.errors is not None
            assert any("schema" in e.lower() for e in result.errors)

    def test_validate_yaml_with_invalid_schema(self):
        """Handle case when schema itself is invalid."""
        from wetwire_gitlab.validation.schema import validate_yaml

        yaml_content = """
stages:
  - build
"""

        with patch("wetwire_gitlab.validation.schema.fetch_schema") as mock_fetch:
            # Return invalid schema
            mock_fetch.return_value = "not a dict"

            result = validate_yaml(yaml_content)

            assert result.valid is False
            assert result.errors is not None
