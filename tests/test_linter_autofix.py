"""Tests for linter auto-fix functionality."""

import tempfile
from pathlib import Path


class TestFixCode:
    """Tests for fix_code function."""

    def test_fix_code_importable(self):
        """fix_code function is importable."""
        from wetwire_gitlab.linter import fix_code

        assert callable(fix_code)

    def test_fix_code_returns_unchanged_for_clean_code(self):
        """fix_code returns unchanged code when no issues found."""
        from wetwire_gitlab.linter import fix_code

        code = """from wetwire_gitlab.pipeline import Job
from wetwire_gitlab.intrinsics import When

job = Job(name="test", stage="test", script=["echo test"], when=When.MANUAL)
"""
        result = fix_code(code)
        assert result == code

    def test_fix_code_fixes_wgl010_when_string(self):
        """fix_code fixes WGL010 when string to When constant."""
        from wetwire_gitlab.linter import fix_code

        code = '''from wetwire_gitlab.pipeline import Job

job = Job(name="deploy", stage="deploy", script=["deploy"], when="manual")
'''
        result = fix_code(code)
        assert 'when="manual"' not in result
        assert "When.MANUAL" in result
        assert "from wetwire_gitlab.intrinsics import When" in result

    def test_fix_code_fixes_multiple_when_strings(self):
        """fix_code fixes multiple when string issues."""
        from wetwire_gitlab.linter import fix_code

        code = '''from wetwire_gitlab.pipeline import Job

job1 = Job(name="deploy", stage="deploy", script=["deploy"], when="manual")
job2 = Job(name="cleanup", stage="deploy", script=["cleanup"], when="always")
'''
        result = fix_code(code)
        assert 'when="manual"' not in result
        assert 'when="always"' not in result
        assert "When.MANUAL" in result
        assert "When.ALWAYS" in result

    def test_fix_code_adds_imports(self):
        """fix_code adds required imports for fixes."""
        from wetwire_gitlab.linter import fix_code

        code = '''from wetwire_gitlab.pipeline import Job

job = Job(name="deploy", stage="deploy", script=["deploy"], when="always")
'''
        result = fix_code(code)
        assert "from wetwire_gitlab.intrinsics import When" in result


class TestFixFile:
    """Tests for fix_file function."""

    def test_fix_file_importable(self):
        """fix_file function is importable."""
        from wetwire_gitlab.linter import fix_file

        assert callable(fix_file)

    def test_fix_file_reads_and_fixes_code(self):
        """fix_file reads file, applies fixes, and returns fixed code."""
        from wetwire_gitlab.linter import fix_file

        code = '''from wetwire_gitlab.pipeline import Job

job = Job(name="deploy", stage="deploy", script=["deploy"], when="manual")
'''
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as f:
            f.write(code)
            f.flush()
            result = fix_file(f.name)

        assert 'when="manual"' not in result
        assert "When.MANUAL" in result

    def test_fix_file_write_mode(self):
        """fix_file with write=True writes fixed code to file."""
        from wetwire_gitlab.linter import fix_file

        code = '''from wetwire_gitlab.pipeline import Job

job = Job(name="deploy", stage="deploy", script=["deploy"], when="manual")
'''
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as f:
            f.write(code)
            f.flush()
            filepath = f.name

        fix_file(filepath, write=True)

        with open(filepath) as f:
            result = f.read()

        assert 'when="manual"' not in result
        assert "When.MANUAL" in result


class TestLintIssueFixFields:
    """Tests for LintIssue fix-related fields."""

    def test_lint_issue_has_original_field(self):
        """LintIssue has original field for auto-fix."""
        from wetwire_gitlab.contracts import LintIssue

        issue = LintIssue(
            code="WGL010",
            message="test",
            file_path="test.py",
            line_number=1,
            original='when="manual"',
            suggestion="when=When.MANUAL",
        )
        assert issue.original == 'when="manual"'

    def test_lint_issue_has_suggestion_field(self):
        """LintIssue has suggestion field for auto-fix."""
        from wetwire_gitlab.contracts import LintIssue

        issue = LintIssue(
            code="WGL010",
            message="test",
            file_path="test.py",
            line_number=1,
            suggestion="when=When.MANUAL",
        )
        assert issue.suggestion == "when=When.MANUAL"

    def test_lint_issue_has_fix_imports_field(self):
        """LintIssue has fix_imports field for required imports."""
        from wetwire_gitlab.contracts import LintIssue

        issue = LintIssue(
            code="WGL010",
            message="test",
            file_path="test.py",
            line_number=1,
            fix_imports=["from wetwire_gitlab.intrinsics import When"],
        )
        assert "from wetwire_gitlab.intrinsics import When" in issue.fix_imports


class TestAutoFixCLI:
    """Tests for auto-fix CLI integration."""

    def test_lint_command_has_fix_flag(self):
        """Lint command accepts --fix flag."""
        import subprocess
        import sys

        result = subprocess.run(
            [sys.executable, "-m", "wetwire_gitlab.cli", "lint", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "--fix" in result.stdout

    def test_lint_fix_applies_changes(self):
        """Lint with --fix applies fixes to files."""
        import subprocess
        import sys

        code = '''from wetwire_gitlab.pipeline import Job

job = Job(name="deploy", stage="deploy", script=["deploy"], when="manual")
'''
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as f:
            f.write(code)
            f.flush()
            filepath = f.name

        result = subprocess.run(
            [sys.executable, "-m", "wetwire_gitlab.cli", "lint", "--fix", filepath],
            capture_output=True,
            text=True,
        )

        with open(filepath) as f:
            fixed = f.read()

        # Should have been fixed
        assert 'when="manual"' not in fixed, "Fix should have been applied"
        assert "When.MANUAL" in fixed
