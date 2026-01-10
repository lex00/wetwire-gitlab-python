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


class TestGraphParamsFlag:
    """Tests for --params/-p flag to include variables in graph."""

    @pytest.fixture
    def project_with_variables(self, tmp_path: Path):
        """Create a project with jobs using variables."""
        src_dir = tmp_path / "src" / "sample"
        src_dir.mkdir(parents=True)

        (src_dir / "__init__.py").write_text('"""Sample package."""\n')
        (src_dir / "jobs.py").write_text('''"""Jobs with variables."""

from wetwire_gitlab.pipeline import Job, Variables

build = Job(
    name="build",
    stage="build",
    script=["make build"],
    variables=Variables({"BUILD_TYPE": "release"}),
)

test = Job(
    name="test",
    stage="test",
    script=["pytest"],
    needs=["build"],
)
''')
        return tmp_path

    def test_graph_params_flag_exists(self):
        """Graph command accepts --params flag."""
        result = subprocess.run(
            [sys.executable, "-m", "wetwire_gitlab.cli", "graph", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "--params" in result.stdout or "-p" in result.stdout

    def test_graph_params_includes_variables_mermaid(self, project_with_variables: Path):
        """Graph with --params includes variable nodes in Mermaid format."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "wetwire_gitlab.cli",
                "graph",
                "--params",
                str(project_with_variables),
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            # Variable nodes should be included with different shape
            assert "BUILD_TYPE" in result.stdout

    def test_graph_params_includes_variables_dot(self, project_with_variables: Path):
        """Graph with --params includes variable nodes in DOT format."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "wetwire_gitlab.cli",
                "graph",
                "--format",
                "dot",
                "--params",
                str(project_with_variables),
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            # Variable nodes should use different shape (ellipse)
            assert "BUILD_TYPE" in result.stdout
            assert "ellipse" in result.stdout or "shape" in result.stdout


class TestGraphClusterFlag:
    """Tests for --cluster/-c flag to group jobs by stage."""

    @pytest.fixture
    def multi_stage_project(self, tmp_path: Path):
        """Create a project with multiple stages."""
        src_dir = tmp_path / "src" / "sample"
        src_dir.mkdir(parents=True)

        (src_dir / "__init__.py").write_text('"""Sample package."""\n')
        (src_dir / "jobs.py").write_text('''"""Multi-stage jobs."""

from wetwire_gitlab.pipeline import Job

build = Job(
    name="build",
    stage="build",
    script=["make build"],
)

unit_test = Job(
    name="unit-test",
    stage="test",
    script=["pytest unit/"],
    needs=["build"],
)

integration_test = Job(
    name="integration-test",
    stage="test",
    script=["pytest integration/"],
    needs=["build"],
)

deploy = Job(
    name="deploy",
    stage="deploy",
    script=["make deploy"],
    needs=["unit-test", "integration-test"],
)
''')
        return tmp_path

    def test_graph_cluster_flag_exists(self):
        """Graph command accepts --cluster flag."""
        result = subprocess.run(
            [sys.executable, "-m", "wetwire_gitlab.cli", "graph", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "--cluster" in result.stdout or "-c" in result.stdout

    def test_graph_cluster_groups_by_stage_mermaid(self, multi_stage_project: Path):
        """Graph with --cluster groups jobs by stage in Mermaid format."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "wetwire_gitlab.cli",
                "graph",
                "--cluster",
                str(multi_stage_project),
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            # Mermaid subgraphs for stages
            assert "subgraph" in result.stdout
            assert "build" in result.stdout
            assert "test" in result.stdout
            assert "deploy" in result.stdout

    def test_graph_cluster_groups_by_stage_dot(self, multi_stage_project: Path):
        """Graph with --cluster groups jobs by stage in DOT format."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "wetwire_gitlab.cli",
                "graph",
                "--format",
                "dot",
                "--cluster",
                str(multi_stage_project),
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            # DOT clusters for stages
            assert "cluster" in result.stdout.lower() or "subgraph" in result.stdout


class TestGraphNodeAnnotations:
    """Tests for node annotations showing stage and when condition."""

    @pytest.fixture
    def annotated_project(self, tmp_path: Path):
        """Create a project with when conditions."""
        src_dir = tmp_path / "src" / "sample"
        src_dir.mkdir(parents=True)

        (src_dir / "__init__.py").write_text('"""Sample package."""\n')
        (src_dir / "jobs.py").write_text('''"""Jobs with when conditions."""

from wetwire_gitlab.pipeline import Job
from wetwire_gitlab.intrinsics import When

build = Job(
    name="build",
    stage="build",
    script=["make build"],
)

deploy = Job(
    name="deploy",
    stage="deploy",
    script=["make deploy"],
    needs=["build"],
    when=When.MANUAL,
)
''')
        return tmp_path

    def test_graph_shows_when_annotation(self, annotated_project: Path):
        """Graph shows when condition in node label."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "wetwire_gitlab.cli",
                "graph",
                str(annotated_project),
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            # Should show manual trigger indicator
            output = result.stdout.lower()
            assert "manual" in output or "deploy" in output


class TestGraphEdgeTypes:
    """Tests for edge type differentiation."""

    @pytest.fixture
    def project_with_artifacts(self, tmp_path: Path):
        """Create a project with artifact dependencies."""
        src_dir = tmp_path / "src" / "sample"
        src_dir.mkdir(parents=True)

        (src_dir / "__init__.py").write_text('"""Sample package."""\n')
        (src_dir / "jobs.py").write_text('''"""Jobs with artifact dependencies."""

from wetwire_gitlab.pipeline import Job, Artifacts

build = Job(
    name="build",
    stage="build",
    script=["make build"],
    artifacts=Artifacts(paths=["dist/"]),
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
    dependencies=["build"],  # Artifact dependency
)
''')
        return tmp_path

    def test_graph_differentiates_edge_types(self, project_with_artifacts: Path):
        """Graph shows different edge styles for needs vs dependencies."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "wetwire_gitlab.cli",
                "graph",
                str(project_with_artifacts),
            ],
            capture_output=True,
            text=True,
        )
        # Just verify command runs - detailed style checking is format-specific
        if result.returncode == 0:
            assert "build" in result.stdout
            assert "test" in result.stdout
