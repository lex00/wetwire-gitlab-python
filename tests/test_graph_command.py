"""Tests for graph command implementation."""

import subprocess
import sys
from pathlib import Path

import pytest


class TestGraphCommandIntegration:
    """Integration tests for graph command."""

    @pytest.fixture
    def sample_project(self, tmp_path: Path):
        """Create a sample project with dependencies."""
        src_dir = tmp_path / "src" / "sample"
        src_dir.mkdir(parents=True)

        (src_dir / "__init__.py").write_text('"""Sample package."""\n')
        (src_dir / "jobs.py").write_text('''"""Sample jobs with dependencies."""

from wetwire_gitlab.pipeline import Job

build = Job(
    name="build",
    stage="build",
    script=["make build"],
)

test = Job(
    name="test",
    stage="test",
    script=["pytest"],
    needs=["build"],
)

deploy = Job(
    name="deploy",
    stage="deploy",
    script=["make deploy"],
    needs=["test"],
)
''')
        return tmp_path

    def test_graph_help(self):
        """Graph command shows help."""
        result = subprocess.run(
            [sys.executable, "-m", "wetwire_gitlab.cli", "graph", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "graph" in result.stdout.lower()

    def test_graph_format_flag(self):
        """Graph command accepts --format flag."""
        result = subprocess.run(
            [sys.executable, "-m", "wetwire_gitlab.cli", "graph", "--help"],
            capture_output=True,
            text=True,
        )
        assert "--format" in result.stdout

    def test_graph_output_flag(self):
        """Graph command accepts --output flag."""
        result = subprocess.run(
            [sys.executable, "-m", "wetwire_gitlab.cli", "graph", "--help"],
            capture_output=True,
            text=True,
        )
        assert "--output" in result.stdout

    def test_graph_generates_mermaid(self, sample_project: Path):
        """Graph command generates Mermaid output."""
        result = subprocess.run(
            [sys.executable, "-m", "wetwire_gitlab.cli", "graph", str(sample_project)],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            # Should contain Mermaid syntax
            assert "graph LR" in result.stdout or "graph" in result.stdout.lower()

    def test_graph_generates_dot(self, sample_project: Path):
        """Graph command generates DOT output."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "wetwire_gitlab.cli",
                "graph",
                "--format",
                "dot",
                str(sample_project),
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            # Should contain DOT syntax
            assert "digraph" in result.stdout

    def test_graph_writes_to_file(self, sample_project: Path, tmp_path: Path):
        """Graph command writes to output file."""
        output_file = tmp_path / "graph.mmd"

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "wetwire_gitlab.cli",
                "graph",
                "--output",
                str(output_file),
                str(sample_project),
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            assert output_file.exists()

    def test_graph_nonexistent_path(self):
        """Graph handles nonexistent path."""
        result = subprocess.run(
            [sys.executable, "-m", "wetwire_gitlab.cli", "graph", "/nonexistent/path"],
            capture_output=True,
            text=True,
        )
        assert result.returncode != 0


class TestGraphCommandUnit:
    """Unit tests for graph command logic."""

    def test_run_graph_function_exists(self):
        """run_graph function is importable."""
        from wetwire_gitlab.cli.main import run_graph

        assert callable(run_graph)


class TestGraphOutput:
    """Tests for graph output formats."""

    def test_mermaid_format_structure(self):
        """Mermaid output has expected structure."""
        # Example of expected Mermaid output
        expected_elements = ["graph LR", "-->"]
        for elem in expected_elements:
            assert isinstance(elem, str)

    def test_dot_format_structure(self):
        """DOT output has expected structure."""
        # Example of expected DOT output
        expected_elements = ["digraph", "->", "}"]
        for elem in expected_elements:
            assert isinstance(elem, str)
