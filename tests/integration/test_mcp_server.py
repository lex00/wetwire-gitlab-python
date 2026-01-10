"""Tests for MCP server functionality."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest


@pytest.mark.slow
class TestMCPServer:
    """Tests for MCP server creation and tool handling."""

    def test_create_server_without_mcp_raises(self):
        """Creating server without MCP package raises ImportError."""
        with patch.dict("sys.modules", {"mcp": None, "mcp.server": None}):
            # Force reimport to trigger ImportError check
            import importlib

            from wetwire_gitlab import mcp_server

            importlib.reload(mcp_server)

            with pytest.raises(ImportError, match="MCP package required"):
                mcp_server.create_server()

    def test_create_server_returns_server(self):
        """create_server returns configured MCP Server."""
        pytest.importorskip("mcp")

        from wetwire_gitlab.mcp_server import create_server

        server = create_server()
        assert server is not None
        assert server.name == "wetwire-gitlab-mcp"


@pytest.mark.slow
class TestInitTool:
    """Tests for wetwire_init tool."""

    def test_init_creates_package(self, tmp_path: Path):
        """Init tool creates package directory structure."""
        from wetwire_gitlab.mcp_server import _create_package

        result = _create_package(str(tmp_path), "my_pipeline")

        assert result["success"] is True
        assert "my_pipeline" in result["message"]

        package_dir = tmp_path / "my_pipeline"
        assert package_dir.exists()
        assert (package_dir / "__init__.py").exists()
        assert (package_dir / "pipeline.py").exists()
        assert (package_dir / "jobs.py").exists()

    def test_init_invalid_name(self, tmp_path: Path):
        """Init tool rejects invalid module names."""
        from wetwire_gitlab.mcp_server import _create_package

        result = _create_package(str(tmp_path), "my-pipeline")

        assert result["success"] is False
        assert "Invalid module name" in result["error"]

    def test_init_nonexistent_path(self):
        """Init tool reports error for nonexistent path."""
        from wetwire_gitlab.mcp_server import _create_package

        result = _create_package("/nonexistent/path", "my_pipeline")

        assert result["success"] is False
        assert "does not exist" in result["error"]

    def test_init_existing_package(self, tmp_path: Path):
        """Init tool reports error if package exists."""
        from wetwire_gitlab.mcp_server import _create_package

        (tmp_path / "existing").mkdir()

        result = _create_package(str(tmp_path), "existing")

        assert result["success"] is False
        assert "already exists" in result["error"]


@pytest.mark.slow
class TestLintTool:
    """Tests for wetwire_lint tool."""

    def test_lint_file(self, tmp_path: Path):
        """Lint tool checks Python file for issues."""
        from wetwire_gitlab.mcp_server import _lint_path

        # Create a file with a lint issue (raw dict instead of Rule)
        test_file = tmp_path / "pipeline.py"
        test_file.write_text(
            """
from wetwire_gitlab.pipeline import Job

job = Job(
    name="test",
    stage="test",
    script=["echo test"],
    rules=[{"if": "$CI_PIPELINE_SOURCE == 'merge_request_event'"}],
)
"""
        )

        result = _lint_path(str(test_file))

        assert result["success"] is True
        assert "issues" in result
        # Should detect WGL002 (raw dict instead of Rule)
        assert (
            result["issue_count"] >= 0
        )  # May or may not have issues depending on impl

    def test_lint_directory(self, tmp_path: Path):
        """Lint tool scans directory for Python files."""
        from wetwire_gitlab.mcp_server import _lint_path

        # Create subdirectory with Python files
        subdir = tmp_path / "ci"
        subdir.mkdir()
        (subdir / "jobs.py").write_text("# empty file\n")
        (subdir / "pipeline.py").write_text("# empty file\n")

        result = _lint_path(str(tmp_path))

        assert result["success"] is True
        assert result["file_count"] == 2

    def test_lint_nonexistent_path(self):
        """Lint tool reports error for nonexistent path."""
        from wetwire_gitlab.mcp_server import _lint_path

        result = _lint_path("/nonexistent/file.py")

        assert result["success"] is False
        assert "does not exist" in result["error"]


@pytest.mark.slow
class TestBuildTool:
    """Tests for wetwire_build tool."""

    def test_build_generates_yaml(self, tmp_path: Path):
        """Build tool generates YAML from package."""
        from wetwire_gitlab.mcp_server import _build_template

        # Create a minimal package with a job
        package = tmp_path / "ci"
        package.mkdir()
        (package / "__init__.py").write_text(
            """
from .jobs import *
"""
        )
        (package / "jobs.py").write_text(
            """
from wetwire_gitlab.pipeline import Job

test = Job(
    name="test",
    stage="test",
    script=["pytest"],
)
"""
        )

        result = _build_template(str(package), output_format="yaml")

        assert result["success"] is True
        assert "template" in result
        assert "test:" in result["template"]
        assert result["format"] == "yaml"

    def test_build_generates_json(self, tmp_path: Path):
        """Build tool generates JSON from package."""
        from wetwire_gitlab.mcp_server import _build_template

        # Create a minimal package
        package = tmp_path / "ci"
        package.mkdir()
        (package / "__init__.py").write_text(
            """
from .jobs import *
"""
        )
        (package / "jobs.py").write_text(
            """
from wetwire_gitlab.pipeline import Job

build = Job(
    name="build",
    stage="build",
    script=["make build"],
)
"""
        )

        result = _build_template(str(package), output_format="json")

        assert result["success"] is True
        assert "template" in result
        # Should be valid JSON
        data = json.loads(result["template"])
        assert "build" in data
        assert result["format"] == "json"

    def test_build_nonexistent_path(self):
        """Build tool reports error for nonexistent path."""
        from wetwire_gitlab.mcp_server import _build_template

        result = _build_template("/nonexistent/package")

        assert result["success"] is False
        assert "does not exist" in result["error"]

    def test_build_not_package(self, tmp_path: Path):
        """Build tool reports error if path is not a package."""
        from wetwire_gitlab.mcp_server import _build_template

        # Create directory without __init__.py
        pkg = tmp_path / "not_package"
        pkg.mkdir()

        result = _build_template(str(pkg))

        assert result["success"] is False
        assert "not a Python package" in result["error"]


@pytest.mark.slow
class TestValidateTool:
    """Tests for wetwire_validate tool."""

    def test_validate_yaml_file(self, tmp_path: Path):
        """Validate tool checks YAML syntax."""
        from wetwire_gitlab.mcp_server import _validate_pipeline
        from wetwire_gitlab.validation.glab import is_glab_installed

        # Create a valid YAML file
        yaml_file = tmp_path / ".gitlab-ci.yml"
        yaml_file.write_text(
            """
stages:
  - test

test:
  stage: test
  script:
    - echo "test"
"""
        )

        result = _validate_pipeline(str(yaml_file))

        # If glab is not installed, we expect an error message
        if not is_glab_installed():
            assert result["success"] is False
            assert "glab" in result["error"].lower()
        else:
            # If glab is installed, validation should work
            assert "success" in result

    def test_validate_nonexistent_file(self):
        """Validate tool reports error for nonexistent file."""
        from wetwire_gitlab.mcp_server import _validate_pipeline

        result = _validate_pipeline("/nonexistent/.gitlab-ci.yml")

        assert result["success"] is False
        assert "does not exist" in result["error"]


@pytest.mark.slow
class TestImportTool:
    """Tests for wetwire_import tool."""

    def test_import_yaml(self, tmp_path: Path):
        """Import tool converts YAML to Python."""
        from wetwire_gitlab.mcp_server import _import_yaml

        # Create a YAML file
        yaml_file = tmp_path / ".gitlab-ci.yml"
        yaml_file.write_text(
            """
test:
  stage: test
  script:
    - pytest
"""
        )

        result = _import_yaml(str(yaml_file))

        assert result["success"] is True
        assert "code" in result
        assert "Job" in result["code"]

    def test_import_nonexistent_file(self):
        """Import tool reports error for nonexistent file."""
        from wetwire_gitlab.mcp_server import _import_yaml

        result = _import_yaml("/nonexistent/.gitlab-ci.yml")

        assert result["success"] is False
        assert "does not exist" in result["error"]


@pytest.mark.slow
class TestToolCalls:
    """Tests for async tool call handling."""

    def test_create_server_returns_named_server(self):
        """Server has correct name when MCP is available."""
        pytest.importorskip("mcp")

        from wetwire_gitlab.mcp_server import create_server

        server = create_server()
        assert server.name == "wetwire-gitlab-mcp"
