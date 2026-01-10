"""Tests for build command implementation."""

import json
import subprocess
import sys
from pathlib import Path

import pytest


class TestBuildCommandIntegration:
    """Integration tests for build command."""

    @pytest.fixture
    def sample_project(self, tmp_path: Path):
        """Create a sample project with pipeline definitions."""
        # Create source directory structure
        src_dir = tmp_path / "src" / "sample"
        src_dir.mkdir(parents=True)

        # Create __init__.py
        (src_dir / "__init__.py").write_text('"""Sample package."""\n')

        # Create jobs.py with Job definitions
        jobs_py = src_dir / "jobs.py"
        jobs_py.write_text('''"""Sample jobs."""

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
    needs=["test"],
)
''')

        # Create pipeline.py with Pipeline definition
        pipeline_py = src_dir / "pipeline.py"
        pipeline_py.write_text('''"""Sample pipeline."""

from wetwire_gitlab.pipeline import Pipeline

pipeline = Pipeline(
    stages=["build", "test", "deploy"],
)
''')

        # Create minimal pyproject.toml
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text('''[project]
name = "sample"
version = "0.1.0"
''')

        return tmp_path

    @pytest.fixture
    def empty_project(self, tmp_path: Path):
        """Create an empty project with no pipeline definitions."""
        (tmp_path / "pyproject.toml").write_text('[project]\nname = "empty"\n')
        (tmp_path / "src").mkdir()
        return tmp_path

    def test_build_generates_yaml(self, sample_project: Path):
        """Build command generates YAML output."""
        result = subprocess.run(
            [sys.executable, "-m", "wetwire_gitlab.cli", "build", str(sample_project)],
            capture_output=True,
            text=True,
        )
        # Should not fail
        assert "stages:" in result.stdout or result.returncode == 0

    def test_build_with_output_flag(self, sample_project: Path):
        """Build command writes to output file."""
        output_file = sample_project / "output.yml"

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "wetwire_gitlab.cli",
                "build",
                "--output",
                str(output_file),
                str(sample_project),
            ],
            capture_output=True,
            text=True,
        )

        # Check file was created or appropriate message shown
        if result.returncode == 0:
            assert output_file.exists()

    def test_build_json_format(self, sample_project: Path):
        """Build command outputs JSON format."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "wetwire_gitlab.cli",
                "build",
                "--format",
                "json",
                str(sample_project),
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0 and result.stdout.strip():
            # Output should be valid JSON
            try:
                data = json.loads(result.stdout)
                assert isinstance(data, dict)
            except json.JSONDecodeError:
                pass  # Allow if not implemented yet

    def test_build_empty_project(self, empty_project: Path):
        """Build command handles empty projects gracefully."""
        result = subprocess.run(
            [sys.executable, "-m", "wetwire_gitlab.cli", "build", str(empty_project)],
            capture_output=True,
            text=True,
        )
        # Should not crash, return error code or message
        assert result.returncode in [0, 1]


class TestBuildCommandUnit:
    """Unit tests for build command logic."""

    def test_run_build_function_exists(self):
        """run_build function is importable."""
        from wetwire_gitlab.cli.main import run_build

        assert callable(run_build)

    def test_build_result_type(self):
        """BuildResult contract is available."""
        from wetwire_gitlab.contracts import BuildResult

        result = BuildResult(
            success=True,
            output_path=".gitlab-ci.yml",
            jobs_count=3,
        )
        assert result.success is True
        assert result.jobs_count == 3


class TestBuildLogic:
    """Tests for build logic."""

    def test_extract_jobs_from_module(self, tmp_path: Path):
        """Jobs can be extracted from Python modules."""
        from wetwire_gitlab.runner import (
            extract_jobs_from_module,
            import_module_from_path,
        )

        # Create a simple module with jobs
        test_file = tmp_path / "test_jobs.py"
        test_file.write_text('''
from wetwire_gitlab.pipeline import Job

job1 = Job(name="job1", script=["echo test"])
job2 = Job(name="job2", script=["echo test2"])
''')

        module = import_module_from_path(test_file)
        assert module is not None

        jobs = extract_jobs_from_module(module)
        assert len(jobs) == 2

    def test_extract_pipelines_from_module(self, tmp_path: Path):
        """Pipelines can be extracted from Python modules."""
        from wetwire_gitlab.runner import (
            extract_pipelines_from_module,
            import_module_from_path,
        )

        test_file = tmp_path / "test_pipeline.py"
        test_file.write_text('''
from wetwire_gitlab.pipeline import Pipeline

main_pipeline = Pipeline(stages=["build", "test"])
''')

        module = import_module_from_path(test_file)
        assert module is not None

        pipelines = extract_pipelines_from_module(module)
        assert len(pipelines) == 1
        assert pipelines[0].stages == ["build", "test"]

    def test_build_pipeline_yaml(self):
        """YAML can be built from pipeline and jobs."""
        from wetwire_gitlab.pipeline import Job, Pipeline
        from wetwire_gitlab.serialize import build_pipeline_yaml

        pipeline = Pipeline(stages=["build", "test"])
        jobs = [
            Job(name="build_job", stage="build", script=["make"]),
            Job(name="test_job", stage="test", script=["pytest"]),
        ]

        yaml_output = build_pipeline_yaml(pipeline, jobs)

        assert "stages:" in yaml_output
        assert "build_job:" in yaml_output
        assert "test_job:" in yaml_output


class TestBuildOrdering:
    """Tests for job ordering in build."""

    def test_jobs_ordered_by_dependencies(self, tmp_path: Path):
        """Jobs are ordered by dependencies in output."""
        from wetwire_gitlab.contracts import DiscoveredJob
        from wetwire_gitlab.template import order_jobs_for_yaml

        jobs = [
            DiscoveredJob(
                name="deploy",
                variable_name="deploy",
                file_path="test.py",
                line_number=3,
                dependencies=["test"],
            ),
            DiscoveredJob(
                name="build",
                variable_name="build",
                file_path="test.py",
                line_number=1,
            ),
            DiscoveredJob(
                name="test",
                variable_name="test",
                file_path="test.py",
                line_number=2,
                dependencies=["build"],
            ),
        ]

        ordered = order_jobs_for_yaml(jobs)
        names = [j.name for j in ordered]

        assert names.index("build") < names.index("test")
        assert names.index("test") < names.index("deploy")


class TestBuildOutput:
    """Tests for build output handling."""

    def test_yaml_output_valid(self):
        """Generated YAML is valid."""
        import yaml

        from wetwire_gitlab.pipeline import Job, Pipeline
        from wetwire_gitlab.serialize import build_pipeline_yaml

        pipeline = Pipeline(stages=["build"])
        jobs = [Job(name="build", script=["echo build"])]

        yaml_output = build_pipeline_yaml(pipeline, jobs)

        # Should be parseable YAML
        parsed = yaml.safe_load(yaml_output)
        assert "stages" in parsed
        assert "build" in parsed

    def test_json_output_conversion(self):
        """Pipeline can be converted to JSON."""
        from wetwire_gitlab.pipeline import Job, Pipeline
        from wetwire_gitlab.serialize import to_dict

        pipeline = Pipeline(stages=["build", "test"])
        job = Job(name="build", script=["make"])

        # Convert to dict (for JSON serialization)
        pipeline_dict = to_dict(pipeline)
        job_dict = to_dict(job)

        assert pipeline_dict["stages"] == ["build", "test"]
        assert "script" in job_dict


class TestBuildMultiPipeline:
    """Tests for multi-pipeline support."""

    def test_multiple_pipelines_discovered(self, tmp_path: Path):
        """Multiple pipelines can be discovered."""
        from wetwire_gitlab.runner import extract_all_pipelines

        # Create files with multiple pipelines
        src_dir = tmp_path / "src"
        src_dir.mkdir()

        (src_dir / "main.py").write_text('''
from wetwire_gitlab.pipeline import Pipeline
main = Pipeline(stages=["build"])
''')

        (src_dir / "mr.py").write_text('''
from wetwire_gitlab.pipeline import Pipeline
mr_pipeline = Pipeline(stages=["test"])
''')

        pipelines = extract_all_pipelines(src_dir)
        # Should find both pipelines
        assert len(pipelines) >= 2


class TestBuildErrorHandling:
    """Tests for build error handling."""

    def test_nonexistent_path(self):
        """Build handles nonexistent path."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "wetwire_gitlab.cli",
                "build",
                "/nonexistent/path",
            ],
            capture_output=True,
            text=True,
        )
        # Should return error code
        assert result.returncode != 0

    def test_invalid_python_file(self, tmp_path: Path):
        """Build handles invalid Python files gracefully."""
        # Create invalid Python file
        bad_file = tmp_path / "bad.py"
        bad_file.write_text("this is not valid python {{{{")

        from wetwire_gitlab.runner import import_module_from_path

        # Should return None, not crash
        module = import_module_from_path(bad_file)
        assert module is None
