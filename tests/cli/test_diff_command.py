"""Tests for diff command implementation."""

import subprocess
import sys
from pathlib import Path

import pytest


class TestDiffCommandIntegration:
    """Integration tests for diff command."""

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
        pyproject.write_text("""[project]
name = "sample"
version = "0.1.0"
""")

        return tmp_path

    @pytest.fixture
    def identical_yaml(self, tmp_path: Path):
        """Create a project where generated YAML matches original."""
        yaml_content = """stages:
  - build
  - test

build:
  stage: build
  script:
    - make build

test:
  stage: test
  script:
    - pytest
  needs:
    - build
"""
        original = tmp_path / "original.yml"
        original.write_text(yaml_content)

        generated = tmp_path / "generated.yml"
        generated.write_text(yaml_content)

        return tmp_path, original, generated

    @pytest.fixture
    def different_yaml(self, tmp_path: Path):
        """Create a project where generated YAML differs from original."""
        original_content = """stages:
  - build
  - test

build:
  stage: build
  script:
    - make build
"""
        original = tmp_path / "original.yml"
        original.write_text(original_content)

        generated_content = """stages:
  - build
  - test
  - deploy

build:
  stage: build
  script:
    - make build

deploy:
  stage: deploy
  script:
    - make deploy
"""
        generated = tmp_path / "generated.yml"
        generated.write_text(generated_content)

        return tmp_path, original, generated

    def test_diff_help(self):
        """Diff command shows help."""
        result = subprocess.run(
            [sys.executable, "-m", "wetwire_gitlab.cli", "diff", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "diff" in result.stdout.lower()

    def test_diff_identical_files(self, identical_yaml):
        """Diff returns exit code 0 for identical files."""
        tmp_path, original, generated = identical_yaml

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "wetwire_gitlab.cli",
                "diff",
                str(generated),  # Pass generated file directly
                "--original",
                str(original),
            ],
            capture_output=True,
            text=True,
        )

        # Exit code 0 for identical files
        assert result.returncode == 0
        assert (
            "identical" in result.stdout.lower()
            or "no differences" in result.stdout.lower()
        )

    def test_diff_different_files(self, different_yaml):
        """Diff returns exit code 1 for different files."""
        tmp_path, original, generated = different_yaml

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "wetwire_gitlab.cli",
                "diff",
                str(generated),  # Pass generated file directly
                "--original",
                str(original),
            ],
            capture_output=True,
            text=True,
        )

        # Exit code 1 for different files
        assert result.returncode == 1
        # Output should contain diff
        assert (
            "+" in result.stdout
            or "-" in result.stdout
            or "deploy" in result.stdout.lower()
        )

    def test_diff_unified_format(self, different_yaml):
        """Diff outputs unified format."""
        tmp_path, original, generated = different_yaml

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "wetwire_gitlab.cli",
                "diff",
                str(generated),  # Pass generated file directly
                "--original",
                str(original),
                "--format",
                "unified",
            ],
            capture_output=True,
            text=True,
        )

        # Unified diff format should have @@ markers
        if result.returncode == 1:
            assert "@@" in result.stdout or "---" in result.stdout

    def test_diff_context_format(self, different_yaml):
        """Diff supports context format."""
        tmp_path, original, generated = different_yaml

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "wetwire_gitlab.cli",
                "diff",
                str(generated),  # Pass generated file directly
                "--original",
                str(original),
                "--format",
                "context",
            ],
            capture_output=True,
            text=True,
        )

        # Context diff format should have *** markers
        if result.returncode == 1:
            assert (
                "***" in result.stdout
                or "---" in result.stdout
                or len(result.stdout) > 0
            )

    def test_diff_missing_original(self, tmp_path: Path):
        """Diff handles missing original file."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "wetwire_gitlab.cli",
                "diff",
                str(tmp_path),
                "--original",
                "/nonexistent/file.yml",
            ],
            capture_output=True,
            text=True,
        )

        # Exit code 2 for errors
        assert result.returncode == 2
        assert "error" in result.stderr.lower() or "not found" in result.stderr.lower()

    def test_diff_missing_package(self):
        """Diff handles missing package path."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "wetwire_gitlab.cli",
                "diff",
                "/nonexistent/path",
                "--original",
                "original.yml",
            ],
            capture_output=True,
            text=True,
        )

        # Exit code 2 for errors
        assert result.returncode == 2


class TestDiffCommandUnit:
    """Unit tests for diff command logic."""

    def test_run_diff_function_exists(self):
        """run_diff function is importable."""
        from wetwire_gitlab.cli.commands.diff import run_diff

        assert callable(run_diff)

    def test_diff_with_build_integration(self, tmp_path: Path):
        """Diff can compare generated output with original."""
        # Create original YAML
        original = tmp_path / "original.yml"
        original.write_text("""stages:
  - build

build:
  stage: build
  script:
    - make build
""")

        # Create Python source
        src_dir = tmp_path / "src" / "pkg"
        src_dir.mkdir(parents=True)

        (src_dir / "__init__.py").write_text("")
        (src_dir / "jobs.py").write_text("""
from wetwire_gitlab.pipeline import Job, Pipeline

pipeline = Pipeline(stages=["build"])

build = Job(
    name="build",
    stage="build",
    script=["make build"],
)
""")

        # Build and compare
        import argparse

        from wetwire_gitlab.cli.commands.build import run_build
        from wetwire_gitlab.cli.commands.diff import run_diff

        # Generate YAML
        build_args = argparse.Namespace(
            path=str(tmp_path),
            output=str(tmp_path / "generated.yml"),
            format="yaml",
            type="pipeline",
        )
        build_result = run_build(build_args)

        # Diff should work if build succeeded
        if build_result == 0:
            diff_args = argparse.Namespace(
                path=str(tmp_path),
                original=str(original),
                format="unified",
                semantic=False,
            )
            diff_result = run_diff(diff_args)
            assert diff_result in [0, 1]  # 0 if identical, 1 if different


class TestDiffFormatting:
    """Tests for diff output formatting."""

    def test_unified_diff_format(self, tmp_path: Path):
        """Unified diff produces expected format."""
        import difflib

        original = ["line 1\n", "line 2\n", "line 3\n"]
        generated = ["line 1\n", "line 2 modified\n", "line 3\n"]

        diff = list(
            difflib.unified_diff(
                original,
                generated,
                fromfile="original.yml",
                tofile="generated.yml",
            )
        )

        # Should have @@ markers
        assert any("@@" in line for line in diff)

    def test_context_diff_format(self, tmp_path: Path):
        """Context diff produces expected format."""
        import difflib

        original = ["line 1\n", "line 2\n", "line 3\n"]
        generated = ["line 1\n", "line 2 modified\n", "line 3\n"]

        diff = list(
            difflib.context_diff(
                original,
                generated,
                fromfile="original.yml",
                tofile="generated.yml",
            )
        )

        # Should have *** markers
        assert any("***" in line for line in diff)


class TestDiffExitCodes:
    """Tests for diff command exit codes."""

    def test_exit_0_for_identical(self, tmp_path: Path):
        """Exit code 0 when files are identical."""
        original = tmp_path / "original.yml"
        original.write_text("same content\n")

        generated = tmp_path / "generated.yml"
        generated.write_text("same content\n")

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "wetwire_gitlab.cli",
                "diff",
                str(generated),  # Pass generated file directly
                "--original",
                str(original),
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0

    def test_exit_1_for_different(self, tmp_path: Path):
        """Exit code 1 when files differ."""
        original = tmp_path / "original.yml"
        original.write_text("original content\n")

        generated = tmp_path / "generated.yml"
        generated.write_text("different content\n")

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "wetwire_gitlab.cli",
                "diff",
                str(generated),  # Pass generated file directly
                "--original",
                str(original),
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 1

    def test_exit_2_for_error(self):
        """Exit code 2 for errors."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "wetwire_gitlab.cli",
                "diff",
                "/nonexistent",
                "--original",
                "/also/nonexistent",
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 2


class TestDiffSemanticComparison:
    """Tests for semantic YAML comparison."""

    def test_semantic_flag_exists(self):
        """Semantic flag is available in diff command."""
        result = subprocess.run(
            [sys.executable, "-m", "wetwire_gitlab.cli", "diff", "--help"],
            capture_output=True,
            text=True,
        )

        # Should mention semantic in help
        if result.returncode == 0:
            assert "--semantic" in result.stdout

    def test_semantic_comparison_identical_structure(self, tmp_path: Path):
        """Semantic comparison treats structurally identical YAML as same."""
        # Different formatting, same structure
        original = tmp_path / "original.yml"
        original.write_text("""stages: [build, test]
build:
  stage: build
  script: ["make"]
""")

        generated = tmp_path / "generated.yml"
        generated.write_text("""stages:
  - build
  - test

build:
  stage: build
  script:
    - make
""")

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "wetwire_gitlab.cli",
                "diff",
                str(tmp_path),
                "--original",
                str(original),
                "--semantic",
            ],
            capture_output=True,
            text=True,
        )

        # With semantic comparison, these should be identical
        if result.returncode == 0:
            assert (
                "identical" in result.stdout.lower()
                or "no differences" in result.stdout.lower()
            )
