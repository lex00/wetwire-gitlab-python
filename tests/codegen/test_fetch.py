"""Tests for schema fetching module."""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch


class TestSchemaURLs:
    """Tests for schema URL constants."""

    def test_ci_schema_url(self):
        """CI schema URL is correct."""
        from wetwire_gitlab.codegen.fetch import CI_SCHEMA_URL

        assert "gitlab.com" in CI_SCHEMA_URL
        assert "ci.json" in CI_SCHEMA_URL

    def test_component_urls(self):
        """Component URLs are correct."""
        from wetwire_gitlab.codegen.fetch import COMPONENT_URLS

        assert "sast" in COMPONENT_URLS
        assert "secret-detection" in COMPONENT_URLS
        assert "dast" in COMPONENT_URLS


class TestHTTPFetcher:
    """Tests for HTTP fetcher with retry logic."""

    def test_fetch_url_success(self):
        """Fetch URL returns content on success."""
        from wetwire_gitlab.codegen.fetch import fetch_url

        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_response = MagicMock()
            mock_response.read.return_value = b'{"test": "data"}'
            mock_response.__enter__ = MagicMock(return_value=mock_response)
            mock_response.__exit__ = MagicMock(return_value=False)
            mock_urlopen.return_value = mock_response

            result = fetch_url("https://example.com/test.json")
            assert result == '{"test": "data"}'

    def test_fetch_url_retry_on_failure(self):
        """Fetch URL retries on failure."""
        from wetwire_gitlab.codegen.fetch import fetch_url

        with patch("urllib.request.urlopen") as mock_urlopen:
            # First call fails, second succeeds
            mock_response = MagicMock()
            mock_response.read.return_value = b"success"
            mock_response.__enter__ = MagicMock(return_value=mock_response)
            mock_response.__exit__ = MagicMock(return_value=False)

            mock_urlopen.side_effect = [
                Exception("Connection failed"),
                mock_response,
            ]

            result = fetch_url("https://example.com/test.json", retries=2)
            assert result == "success"
            assert mock_urlopen.call_count == 2

    def test_fetch_url_raises_after_retries(self):
        """Fetch URL raises after exhausting retries."""
        from wetwire_gitlab.codegen.fetch import FetchError, fetch_url

        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_urlopen.side_effect = Exception("Connection failed")

            try:
                fetch_url("https://example.com/test.json", retries=2)
                assert False, "Should have raised FetchError"
            except FetchError as e:
                assert "Connection failed" in str(e)


class TestFetchCISchema:
    """Tests for fetching CI schema."""

    def test_fetch_ci_schema(self):
        """Fetch CI schema returns parsed JSON."""
        from wetwire_gitlab.codegen.fetch import fetch_ci_schema

        with patch("wetwire_gitlab.codegen.fetch.fetch_url") as mock_fetch:
            mock_fetch.return_value = (
                '{"$schema": "http://json-schema.org/draft-07/schema#"}'
            )

            result = fetch_ci_schema()
            assert "$schema" in result
            mock_fetch.assert_called_once()


class TestFetchComponentSpec:
    """Tests for fetching component specifications."""

    def test_fetch_component_spec(self):
        """Fetch component spec returns content."""
        from wetwire_gitlab.codegen.fetch import fetch_component_spec

        with patch("wetwire_gitlab.codegen.fetch.fetch_url") as mock_fetch:
            mock_fetch.return_value = "spec:\n  inputs:\n    - name: stage"

            result = fetch_component_spec("sast")
            assert "spec:" in result
            mock_fetch.assert_called_once()

    def test_fetch_component_spec_unknown(self):
        """Fetch unknown component raises error."""
        from wetwire_gitlab.codegen.fetch import FetchError, fetch_component_spec

        try:
            fetch_component_spec("unknown-component")
            assert False, "Should have raised FetchError"
        except FetchError:
            pass


class TestFetchAllSchemas:
    """Tests for fetching all schemas."""

    def test_fetch_all_schemas(self):
        """Fetch all schemas creates manifest."""
        from wetwire_gitlab.codegen.fetch import fetch_all_schemas

        with patch("wetwire_gitlab.codegen.fetch.fetch_ci_schema") as mock_ci:
            with patch(
                "wetwire_gitlab.codegen.fetch.fetch_component_spec"
            ) as mock_comp:
                mock_ci.return_value = {"$schema": "test"}
                mock_comp.return_value = "spec: test"

                with tempfile.TemporaryDirectory() as tmpdir:
                    result = fetch_all_schemas(Path(tmpdir))

                    assert result["ci_schema"] is True
                    assert "sast" in result["components"]
                    assert Path(tmpdir, "ci-schema.json").exists()
                    assert Path(tmpdir, "manifest.json").exists()


class TestManifest:
    """Tests for manifest handling."""

    def test_create_manifest(self):
        """Create manifest writes valid JSON."""
        from wetwire_gitlab.codegen.fetch import create_manifest

        with tempfile.TemporaryDirectory() as tmpdir:
            specs_dir = Path(tmpdir)
            components = {"sast": True, "dast": True}

            create_manifest(specs_dir, ci_schema=True, components=components)

            manifest_path = specs_dir / "manifest.json"
            assert manifest_path.exists()

            with open(manifest_path) as f:
                data = json.load(f)

            assert data["ci_schema"] is True
            assert data["components"]["sast"] is True

    def test_load_manifest(self):
        """Load manifest reads existing manifest."""
        from wetwire_gitlab.codegen.fetch import load_manifest

        with tempfile.TemporaryDirectory() as tmpdir:
            specs_dir = Path(tmpdir)
            manifest_path = specs_dir / "manifest.json"

            manifest_data = {
                "version": "1.0",
                "ci_schema": True,
                "components": {"sast": True},
            }

            with open(manifest_path, "w") as f:
                json.dump(manifest_data, f)

            result = load_manifest(specs_dir)
            assert result["ci_schema"] is True
            assert result["components"]["sast"] is True

    def test_load_manifest_not_found(self):
        """Load manifest returns None if not found."""
        from wetwire_gitlab.codegen.fetch import load_manifest

        with tempfile.TemporaryDirectory() as tmpdir:
            result = load_manifest(Path(tmpdir))
            assert result is None
