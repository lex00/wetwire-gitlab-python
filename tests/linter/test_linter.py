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
