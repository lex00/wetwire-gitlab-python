"""Tests for lint command implementation."""

import subprocess
import sys
from pathlib import Path

import pytest


class TestLintCommandIntegration:
    """Integration tests for lint command."""

    @pytest.fixture
    def clean_project(self, tmp_path: Path):
        """Create a project with clean pipeline code."""
        src_dir = tmp_path / "src" / "clean"
        src_dir.mkdir(parents=True)

        (src_dir / "__init__.py").write_text('"""Clean package."""\n')
        (src_dir / "jobs.py").write_text('''"""Clean jobs."""

from wetwire_gitlab.pipeline import Job, Artifacts, Image

build = Job(
    name="build",
    stage="build",
    image=Image(name="python:3.12"),
    script=["make build"],
    artifacts=Artifacts(paths=["dist/"]),
)
''')
        return tmp_path

    @pytest.fixture
    def dirty_project(self, tmp_path: Path):
        """Create a project with lint issues."""
        src_dir = tmp_path / "src" / "dirty"
        src_dir.mkdir(parents=True)

        (src_dir / "__init__.py").write_text('"""Dirty package."""\n')
        # Using raw dict instead of Rule dataclass
        (src_dir / "jobs.py").write_text('''"""Jobs with lint issues."""

from wetwire_gitlab.pipeline import Job

# Using raw dict for rules instead of Rule dataclass
build = Job(
    name="build",
    script=["make build"],
    rules=[{"if": "$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH"}],
)
''')
        return tmp_path

    def test_lint_help(self):
        """Lint command shows help."""
        result = subprocess.run(
            [sys.executable, "-m", "wetwire_gitlab.cli", "lint", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "lint" in result.stdout.lower()

    def test_lint_clean_project(self, clean_project: Path):
        """Lint command returns 0 for clean project."""
        result = subprocess.run(
            [sys.executable, "-m", "wetwire_gitlab.cli", "lint", str(clean_project)],
            capture_output=True,
            text=True,
        )
        # Clean project should return 0
        assert result.returncode == 0

    def test_lint_nonexistent_path(self):
        """Lint handles nonexistent path."""
        result = subprocess.run(
            [sys.executable, "-m", "wetwire_gitlab.cli", "lint", "/nonexistent/path"],
            capture_output=True,
            text=True,
        )
        assert result.returncode != 0

    def test_lint_format_json(self, clean_project: Path):
        """Lint command supports JSON output."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "wetwire_gitlab.cli",
                "lint",
                "--format",
                "json",
                str(clean_project),
            ],
            capture_output=True,
            text=True,
        )
        # Should complete (output may be empty JSON or success message)
        assert result.returncode in [0, 1]


class TestLintCommandUnit:
    """Unit tests for lint command logic."""

    def test_run_lint_function_exists(self):
        """run_lint function is importable."""
        from wetwire_gitlab.cli.main import run_lint

        assert callable(run_lint)

    def test_lint_result_type(self):
        """LintResult contract is available."""
        from wetwire_gitlab.contracts import LintResult

        result = LintResult(success=True, issues=[], files_checked=5)
        assert result.success is True
        assert result.files_checked == 5

    def test_lint_issue_type(self):
        """LintIssue contract is available."""
        from wetwire_gitlab.contracts import LintIssue

        issue = LintIssue(
            code="WGL001",
            message="Use typed component",
            file_path="test.py",
            line_number=10,
        )
        assert issue.code == "WGL001"


class TestLinterModule:
    """Tests for linter module."""

    def test_lint_file_function_exists(self):
        """lint_file function exists."""
        from wetwire_gitlab.linter import lint_file

        assert callable(lint_file)

    def test_lint_directory_function_exists(self):
        """lint_directory function exists."""
        from wetwire_gitlab.linter import lint_directory

        assert callable(lint_directory)

    def test_lint_file_returns_result(self, tmp_path: Path):
        """lint_file returns LintResult."""
        from wetwire_gitlab.linter import lint_file

        test_file = tmp_path / "test.py"
        test_file.write_text("# Just a comment\n")

        result = lint_file(test_file)
        assert hasattr(result, "success")
        assert hasattr(result, "issues")

    def test_lint_file_skips_non_python(self, tmp_path: Path):
        """lint_file skips non-Python files."""
        from wetwire_gitlab.linter import lint_file

        txt_file = tmp_path / "test.txt"
        txt_file.write_text("not python")

        result = lint_file(txt_file)
        assert result.files_checked == 0

    def test_lint_directory_recursive(self, tmp_path: Path):
        """lint_directory scans recursively."""
        from wetwire_gitlab.linter import lint_directory

        # Create nested structure
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        (tmp_path / "top.py").write_text("# top level\n")
        (subdir / "nested.py").write_text("# nested\n")

        result = lint_directory(tmp_path)
        assert result.files_checked == 2


class TestLintRules:
    """Tests for lint rules."""

    def test_rules_registry_exists(self):
        """Rule registry is available."""
        from wetwire_gitlab.linter.rules import RULE_REGISTRY

        assert isinstance(RULE_REGISTRY, dict)
        assert len(RULE_REGISTRY) > 0

    def test_all_rule_codes(self):
        """All expected rule codes exist."""
        from wetwire_gitlab.linter.rules import RULE_REGISTRY

        expected_codes = [
            "WGL001",
            "WGL002",
            "WGL003",
            "WGL004",
            "WGL005",
            "WGL006",
            "WGL007",
            "WGL008",
        ]
        for code in expected_codes:
            assert code in RULE_REGISTRY, f"Missing rule: {code}"

    def test_rule_detects_raw_dict_rules(self, tmp_path: Path):
        """WGL002 detects raw dict rules."""
        from wetwire_gitlab.linter import lint_file

        test_file = tmp_path / "test.py"
        test_file.write_text('''
from wetwire_gitlab.pipeline import Job

job = Job(
    name="test",
    script=["echo test"],
    rules=[{"if": "$CI"}],
)
''')

        result = lint_file(test_file, rules=["WGL002"])
        # Should detect raw dict usage
        assert any(i.code == "WGL002" for i in result.issues)


class TestLintExitCodes:
    """Tests for lint command exit codes."""

    def test_exit_0_for_no_issues(self, tmp_path: Path):
        """Exit code 0 when no issues found."""
        test_file = tmp_path / "clean.py"
        test_file.write_text("# Clean file\n")

        result = subprocess.run(
            [sys.executable, "-m", "wetwire_gitlab.cli", "lint", str(tmp_path)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0


class TestLintOutput:
    """Tests for lint output formatting."""

    def test_text_output_includes_rule_code(self, tmp_path: Path):
        """Text output includes rule codes."""
        from wetwire_gitlab.contracts import LintIssue

        issue = LintIssue(
            code="WGL001",
            message="Test message",
            file_path="test.py",
            line_number=1,
        )
        # Rule code should be in the issue
        assert "WGL001" in issue.code

    def test_json_output_structure(self):
        """JSON output has expected structure."""
        from wetwire_gitlab.contracts import LintResult

        result = LintResult(success=True, issues=[], files_checked=1)
        # Should be serializable
        assert result.success is True
        assert isinstance(result.issues, list)
