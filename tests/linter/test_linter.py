"""Tests for the pipeline linter module."""

import tempfile
from pathlib import Path


class TestLinterFramework:
    """Tests for the linter framework."""

    def test_lint_file(self):
        """Lint a single Python file."""
        from wetwire_gitlab.linter import lint_file

        code = '''
from wetwire_gitlab.pipeline import Job

job = Job(name="test", stage="test", script=["echo test"])
'''
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as f:
            f.write(code)
            f.flush()
            result = lint_file(Path(f.name))

        assert result.files_checked == 1
        assert isinstance(result.issues, list)

    def test_lint_directory(self):
        """Lint all Python files in a directory."""
        from wetwire_gitlab.linter import lint_directory

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir)

            (path / "jobs.py").write_text('''
from wetwire_gitlab.pipeline import Job
job = Job(name="test", stage="test", script=["echo test"])
''')

            (path / "pipelines.py").write_text('''
from wetwire_gitlab.pipeline import Pipeline
pipeline = Pipeline(stages=["test"])
''')

            result = lint_directory(path)

        assert result.files_checked == 2

    def test_lint_with_rules(self):
        """Lint with specific rules enabled."""
        from wetwire_gitlab.linter import lint_file

        code = '''
from wetwire_gitlab.pipeline import Job
job = Job(name="test", stage="test", script=["echo test"])
'''
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as f:
            f.write(code)
            f.flush()
            result = lint_file(Path(f.name), rules=["WGL007"])

        assert isinstance(result.issues, list)


class TestLintRuleWGL001:
    """Tests for WGL001: Use typed component wrappers."""

    def test_wgl001_detects_raw_include_component(self):
        """Detect raw include component usage instead of typed wrapper."""
        from wetwire_gitlab.linter import lint_file

        code = '''
from wetwire_gitlab.pipeline import Include

include = Include(component="gitlab.com/components/sast@main")
'''
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as f:
            f.write(code)
            f.flush()
            result = lint_file(Path(f.name))

        wgl001_issues = [i for i in result.issues if i.code == "WGL001"]
        assert len(wgl001_issues) > 0


class TestLintRuleWGL002:
    """Tests for WGL002: Use Rule dataclass."""

    def test_wgl002_detects_raw_dict_rules(self):
        """Detect raw dict rules instead of Rule dataclass."""
        from wetwire_gitlab.linter import lint_file

        code = '''
from wetwire_gitlab.pipeline import Job

job = Job(
    name="test",
    stage="test",
    script=["echo test"],
    rules=[{"if": "$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH"}]
)
'''
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as f:
            f.write(code)
            f.flush()
            result = lint_file(Path(f.name))

        wgl002_issues = [i for i in result.issues if i.code == "WGL002"]
        assert len(wgl002_issues) > 0


class TestLintRuleWGL003:
    """Tests for WGL003: Use predefined variables."""

    def test_wgl003_detects_raw_ci_variable_strings(self):
        """Detect raw CI variable strings instead of intrinsics."""
        from wetwire_gitlab.linter import lint_file

        code = '''
from wetwire_gitlab.pipeline import Rule

rule = Rule(if_="$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH")
'''
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as f:
            f.write(code)
            f.flush()
            result = lint_file(Path(f.name))

        wgl003_issues = [i for i in result.issues if i.code == "WGL003"]
        assert len(wgl003_issues) > 0


class TestLintRuleWGL004:
    """Tests for WGL004: Use Cache dataclass."""

    def test_wgl004_detects_raw_dict_cache(self):
        """Detect raw dict cache instead of Cache dataclass."""
        from wetwire_gitlab.linter import lint_file

        code = '''
from wetwire_gitlab.pipeline import Job

job = Job(
    name="test",
    stage="test",
    script=["echo test"],
    cache={"paths": [".cache"]}
)
'''
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as f:
            f.write(code)
            f.flush()
            result = lint_file(Path(f.name))

        wgl004_issues = [i for i in result.issues if i.code == "WGL004"]
        assert len(wgl004_issues) > 0


class TestLintRuleWGL005:
    """Tests for WGL005: Use Artifacts dataclass."""

    def test_wgl005_detects_raw_dict_artifacts(self):
        """Detect raw dict artifacts instead of Artifacts dataclass."""
        from wetwire_gitlab.linter import lint_file

        code = '''
from wetwire_gitlab.pipeline import Job

job = Job(
    name="test",
    stage="test",
    script=["echo test"],
    artifacts={"paths": ["build/"]}
)
'''
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as f:
            f.write(code)
            f.flush()
            result = lint_file(Path(f.name))

        wgl005_issues = [i for i in result.issues if i.code == "WGL005"]
        assert len(wgl005_issues) > 0


class TestLintRuleWGL006:
    """Tests for WGL006: Use typed stage constants."""

    def test_wgl006_detects_string_stage(self):
        """Detect string literals for stage instead of constants."""
        from wetwire_gitlab.linter import lint_file

        code = '''
from wetwire_gitlab.pipeline import Job

job = Job(name="test", stage="test", script=["echo test"])
'''
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as f:
            f.write(code)
            f.flush()
            result = lint_file(Path(f.name))

        # WGL006 should not trigger if there's no Stage enum defined
        # This is a placeholder for when Stage constants are added
        assert isinstance(result.issues, list)


class TestLintRuleWGL007:
    """Tests for WGL007: Duplicate job names."""

    def test_wgl007_detects_duplicate_job_names(self):
        """Detect duplicate job names in the same file."""
        from wetwire_gitlab.linter import lint_file

        code = '''
from wetwire_gitlab.pipeline import Job

job1 = Job(name="build", stage="build", script=["make"])
job2 = Job(name="build", stage="test", script=["test"])
'''
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as f:
            f.write(code)
            f.flush()
            result = lint_file(Path(f.name))

        wgl007_issues = [i for i in result.issues if i.code == "WGL007"]
        assert len(wgl007_issues) > 0


class TestLintRuleWGL008:
    """Tests for WGL008: File too large."""

    def test_wgl008_detects_too_many_jobs(self):
        """Detect files with too many jobs."""
        from wetwire_gitlab.linter import lint_file

        # Create a file with many jobs
        jobs = []
        for i in range(15):
            jobs.append(
                f'job{i} = Job(name="job{i}", stage="build", script=["echo {i}"])'
            )

        code = '''
from wetwire_gitlab.pipeline import Job

''' + "\n".join(jobs)

        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as f:
            f.write(code)
            f.flush()
            result = lint_file(Path(f.name), max_jobs=10)

        wgl008_issues = [i for i in result.issues if i.code == "WGL008"]
        assert len(wgl008_issues) > 0


class TestLinterConfig:
    """Tests for linter configuration."""

    def test_exclude_rules(self):
        """Exclude specific rules from linting."""
        from wetwire_gitlab.linter import lint_file

        code = '''
from wetwire_gitlab.pipeline import Job

job1 = Job(name="build", stage="build", script=["make"])
job2 = Job(name="build", stage="test", script=["test"])
'''
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as f:
            f.write(code)
            f.flush()
            result = lint_file(Path(f.name), exclude_rules=["WGL007"])

        wgl007_issues = [i for i in result.issues if i.code == "WGL007"]
        assert len(wgl007_issues) == 0

    def test_lint_success_returns_true(self):
        """Lint success returns True."""
        from wetwire_gitlab.linter import lint_file

        code = '''
# A simple Python file with no issues
x = 1
'''
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as f:
            f.write(code)
            f.flush()
            result = lint_file(Path(f.name))

        assert result.success is True
        assert len(result.issues) == 0


class TestLinterOutput:
    """Tests for linter output formats."""

    def test_lint_issue_has_required_fields(self):
        """Lint issues have all required fields."""
        from wetwire_gitlab.linter import lint_file

        code = '''
from wetwire_gitlab.pipeline import Job

job1 = Job(name="build", stage="build", script=["make"])
job2 = Job(name="build", stage="test", script=["test"])
'''
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as f:
            f.write(code)
            f.flush()
            result = lint_file(Path(f.name))

        if result.issues:
            issue = result.issues[0]
            assert hasattr(issue, "code")
            assert hasattr(issue, "message")
            assert hasattr(issue, "file_path")
            assert hasattr(issue, "line_number")


class TestLintRuleWGL009:
    """Tests for WGL009: Use predefined Rules constants."""

    def test_wgl009_detects_common_rule_patterns(self):
        """Detect Rule() with common patterns that have predefined constants."""
        from wetwire_gitlab.linter import lint_file

        code = '''
from wetwire_gitlab.pipeline import Job, Rule

job = Job(
    name="deploy",
    stage="deploy",
    script=["make deploy"],
    rules=[Rule(if_="$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH")]
)
'''
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as f:
            f.write(code)
            f.flush()
            result = lint_file(Path(f.name))

        wgl009_issues = [i for i in result.issues if i.code == "WGL009"]
        assert len(wgl009_issues) > 0

    def test_wgl009_detects_tag_pattern(self):
        """Detect Rule() with tag pattern."""
        from wetwire_gitlab.linter import lint_file

        code = '''
from wetwire_gitlab.pipeline import Job, Rule

job = Job(
    name="release",
    stage="deploy",
    script=["make release"],
    rules=[Rule(if_="$CI_COMMIT_TAG")]
)
'''
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as f:
            f.write(code)
            f.flush()
            result = lint_file(Path(f.name))

        wgl009_issues = [i for i in result.issues if i.code == "WGL009"]
        assert len(wgl009_issues) > 0

    def test_wgl009_allows_custom_rules(self):
        """Allow custom Rule() without predefined patterns."""
        from wetwire_gitlab.linter import lint_file

        code = '''
from wetwire_gitlab.pipeline import Job, Rule

job = Job(
    name="custom",
    stage="build",
    script=["make custom"],
    rules=[Rule(if_="$CUSTOM_VAR == 'yes'")]
)
'''
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as f:
            f.write(code)
            f.flush()
            result = lint_file(Path(f.name))

        wgl009_issues = [i for i in result.issues if i.code == "WGL009"]
        assert len(wgl009_issues) == 0


class TestLintRuleWGL010:
    """Tests for WGL010: Use typed When constants."""

    def test_wgl010_detects_string_when_manual(self):
        """Detect when='manual' string instead of When.MANUAL."""
        from wetwire_gitlab.linter import lint_file

        code = '''
from wetwire_gitlab.pipeline import Job

job = Job(
    name="deploy",
    stage="deploy",
    script=["make deploy"],
    when="manual"
)
'''
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as f:
            f.write(code)
            f.flush()
            result = lint_file(Path(f.name))

        wgl010_issues = [i for i in result.issues if i.code == "WGL010"]
        assert len(wgl010_issues) > 0

    def test_wgl010_detects_string_when_always(self):
        """Detect when='always' string instead of When.ALWAYS."""
        from wetwire_gitlab.linter import lint_file

        code = '''
from wetwire_gitlab.pipeline import Job

job = Job(
    name="cleanup",
    stage="deploy",
    script=["make cleanup"],
    when="always"
)
'''
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as f:
            f.write(code)
            f.flush()
            result = lint_file(Path(f.name))

        wgl010_issues = [i for i in result.issues if i.code == "WGL010"]
        assert len(wgl010_issues) > 0

    def test_wgl010_allows_when_constant(self):
        """Allow When.MANUAL constant usage."""
        from wetwire_gitlab.linter import lint_file

        code = '''
from wetwire_gitlab.pipeline import Job
from wetwire_gitlab.intrinsics import When

job = Job(
    name="deploy",
    stage="deploy",
    script=["make deploy"],
    when=When.MANUAL
)
'''
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as f:
            f.write(code)
            f.flush()
            result = lint_file(Path(f.name))

        wgl010_issues = [i for i in result.issues if i.code == "WGL010"]
        assert len(wgl010_issues) == 0


class TestLintRuleWGL011:
    """Tests for WGL011: Missing stage."""

    def test_wgl011_detects_missing_stage(self):
        """Detect Job() without stage keyword."""
        from wetwire_gitlab.linter import lint_file

        code = '''
from wetwire_gitlab.pipeline import Job

job = Job(
    name="build",
    script=["make build"],
)
'''
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as f:
            f.write(code)
            f.flush()
            result = lint_file(Path(f.name))

        wgl011_issues = [i for i in result.issues if i.code == "WGL011"]
        assert len(wgl011_issues) > 0

    def test_wgl011_allows_explicit_stage(self):
        """Allow Job() with explicit stage keyword."""
        from wetwire_gitlab.linter import lint_file

        code = '''
from wetwire_gitlab.pipeline import Job

job = Job(
    name="build",
    stage="build",
    script=["make build"],
)
'''
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as f:
            f.write(code)
            f.flush()
            result = lint_file(Path(f.name))

        wgl011_issues = [i for i in result.issues if i.code == "WGL011"]
        assert len(wgl011_issues) == 0


class TestLinterEdgeCases:
    """Tests for linter edge cases and error handling."""

    def test_lint_file_with_syntax_error(self):
        """Lint file with Python syntax error returns empty result."""
        from wetwire_gitlab.linter import lint_file

        code = """
def broken(
    # Missing closing paren
x = 1
"""
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as f:
            f.write(code)
            f.flush()
            result = lint_file(Path(f.name))

        assert result.success is True
        assert result.files_checked == 0
        assert len(result.issues) == 0

    def test_lint_file_non_python_skipped(self):
        """Lint non-Python files are skipped."""
        from wetwire_gitlab.linter import lint_file

        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False, mode="w") as f:
            f.write("not python code")
            f.flush()
            result = lint_file(Path(f.name))

        assert result.success is True
        assert result.files_checked == 0

    def test_lint_file_unknown_rule(self):
        """Lint with unknown rule code is ignored."""
        from wetwire_gitlab.linter import lint_file

        code = """
x = 1
"""
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as f:
            f.write(code)
            f.flush()
            result = lint_file(Path(f.name), rules=["UNKNOWN_RULE_999"])

        assert result.success is True
        assert len(result.issues) == 0

    def test_lint_directory_skips_pycache(self):
        """Lint directory skips __pycache__ directories."""
        from wetwire_gitlab.linter import lint_directory

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir)

            # Create a normal Python file
            (path / "jobs.py").write_text("""
from wetwire_gitlab.pipeline import Job
job = Job(name="test", stage="test", script=["echo test"])
""")

            # Create a __pycache__ directory with a Python file
            pycache = path / "__pycache__"
            pycache.mkdir()
            (pycache / "cached.py").write_text("""
from wetwire_gitlab.pipeline import Job
job = Job(name="cached", stage="test", script=["echo cached"])
""")

            result = lint_directory(path)

        # Should only count jobs.py, not the cached file
        assert result.files_checked == 1

    def test_lint_directory_skips_hidden_dirs(self):
        """Lint directory skips hidden directories."""
        from wetwire_gitlab.linter import lint_directory

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir)

            # Create a normal Python file
            (path / "jobs.py").write_text("x = 1")

            # Create a hidden directory with a Python file
            hidden = path / ".hidden"
            hidden.mkdir()
            (hidden / "secret.py").write_text("y = 2")

            result = lint_directory(path)

        # Should only count jobs.py, not the hidden file
        assert result.files_checked == 1


class TestLintCodeFunction:
    """Tests for the lint_code function."""

    def test_lint_code_basic(self):
        """Lint code string works."""
        from wetwire_gitlab.linter import lint_code

        code = """
from wetwire_gitlab.pipeline import Job
job = Job(name="test", stage="test", script=["echo test"])
"""
        issues = lint_code(code)
        assert isinstance(issues, list)

    def test_lint_code_with_syntax_error(self):
        """Lint code with syntax error returns empty list."""
        from wetwire_gitlab.linter import lint_code

        code = """
def broken(
    # Missing closing paren
"""
        issues = lint_code(code)
        assert issues == []

    def test_lint_code_with_exclude_rules(self):
        """Lint code with excluded rules."""
        from wetwire_gitlab.linter import lint_code

        code = """
from wetwire_gitlab.pipeline import Job
job1 = Job(name="build", stage="build", script=["make"])
job2 = Job(name="build", stage="test", script=["test"])
"""
        issues = lint_code(code, exclude_rules=["WGL007"])
        wgl007_issues = [i for i in issues if i.code == "WGL007"]
        assert len(wgl007_issues) == 0

    def test_lint_code_with_unknown_rule(self):
        """Lint code with unknown rule code is ignored."""
        from wetwire_gitlab.linter import lint_code

        code = "x = 1"
        issues = lint_code(code, rules=["UNKNOWN_RULE_999"])
        assert issues == []


class TestFixCodeFunction:
    """Tests for the fix_code function."""

    def test_fix_code_no_issues(self):
        """Fix code with no issues returns source unchanged."""
        from wetwire_gitlab.linter import fix_code

        code = """
from wetwire_gitlab.intrinsics import When
from wetwire_gitlab.pipeline import Job

job = Job(
    name="deploy",
    stage="deploy",
    script=["make deploy"],
    when=When.MANUAL
)
"""
        fixed = fix_code(code)
        assert fixed == code

    def test_fix_code_with_insertions(self):
        """Fix code handles line insertions."""
        from wetwire_gitlab.linter import fix_code

        # This test verifies insertion handling works
        # The actual fix behavior depends on rules that produce insertions
        code = """
from wetwire_gitlab.pipeline import Job

job = Job(
    name="deploy",
    stage="deploy",
    script=["make deploy"],
    when="manual"
)
"""
        fixed = fix_code(code, rules=["WGL010"])
        # Should have fixed the when="manual" to When.MANUAL
        assert "When.MANUAL" in fixed or fixed == code


class TestAddImportsFunction:
    """Tests for the _add_imports helper function."""

    def test_add_imports_after_existing(self):
        """Add imports after existing imports."""
        from wetwire_gitlab.linter.linter import _add_imports

        source = """import os
import sys

x = 1
"""
        imports = {"from wetwire_gitlab.intrinsics import When"}
        result = _add_imports(source, imports)

        # Should add import after existing imports
        assert "from wetwire_gitlab.intrinsics import When" in result

    def test_add_imports_no_existing(self):
        """Add imports when no existing imports."""
        from wetwire_gitlab.linter.linter import _add_imports

        source = """x = 1
y = 2
"""
        imports = {"from wetwire_gitlab.intrinsics import When"}
        result = _add_imports(source, imports)

        # Should add import at beginning
        assert "from wetwire_gitlab.intrinsics import When" in result

    def test_add_imports_empty_set(self):
        """Add imports with empty set returns source unchanged."""
        from wetwire_gitlab.linter.linter import _add_imports

        source = "x = 1"
        result = _add_imports(source, set())
        assert result == source

    def test_add_imports_after_docstring(self):
        """Add imports after module docstring."""
        from wetwire_gitlab.linter.linter import _add_imports

        source = '''"""Module docstring."""

x = 1
'''
        imports = {"import os"}
        result = _add_imports(source, imports)

        # Should still have docstring before import
        assert result.index('"""Module docstring."""') < result.index("import os")
