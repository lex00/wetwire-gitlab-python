"""Tests for runner/value extraction module."""

import tempfile
from pathlib import Path


class TestModuleImport:
    """Tests for importing Python modules."""

    def test_import_module_from_path(self):
        """Import a module from a file path."""
        from wetwire_gitlab.runner import import_module_from_path

        code = '''
x = 42
y = "hello"
'''
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as f:
            f.write(code)
            f.flush()
            module = import_module_from_path(Path(f.name))

        assert module is not None
        assert module.x == 42
        assert module.y == "hello"

    def test_import_module_with_job(self):
        """Import a module containing Job definitions."""
        from wetwire_gitlab.runner import import_module_from_path

        code = '''
from dataclasses import dataclass

@dataclass
class Job:
    name: str
    stage: str = "build"

build_job = Job(name="build")
'''
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as f:
            f.write(code)
            f.flush()
            module = import_module_from_path(Path(f.name))

        assert hasattr(module, "build_job")
        assert module.build_job.name == "build"


class TestValueExtraction:
    """Tests for extracting values from modules."""

    def test_extract_jobs_from_module(self):
        """Extract Job instances from a module."""
        from wetwire_gitlab.runner import (
            extract_jobs_from_module,
            import_module_from_path,
        )

        code = '''
from dataclasses import dataclass

@dataclass
class Job:
    name: str
    stage: str = "build"
    script: list = None

build = Job(name="build", stage="build", script=["make build"])
test = Job(name="test", stage="test", script=["pytest"])
other_var = "not a job"
'''
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as f:
            f.write(code)
            f.flush()
            module = import_module_from_path(Path(f.name))
            jobs = extract_jobs_from_module(module, "Job")

        assert len(jobs) == 2
        job_names = {j.name for j in jobs}
        assert job_names == {"build", "test"}

    def test_extract_pipelines_from_module(self):
        """Extract Pipeline instances from a module."""
        from wetwire_gitlab.runner import (
            extract_pipelines_from_module,
            import_module_from_path,
        )

        code = '''
from dataclasses import dataclass

@dataclass
class Pipeline:
    stages: list

pipeline = Pipeline(stages=["build", "test"])
'''
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as f:
            f.write(code)
            f.flush()
            module = import_module_from_path(Path(f.name))
            pipelines = extract_pipelines_from_module(module, "Pipeline")

        assert len(pipelines) == 1
        assert pipelines[0].stages == ["build", "test"]


class TestModulePathResolution:
    """Tests for resolving module paths."""

    def test_resolve_module_path(self):
        """Resolve a Python file path to module path."""
        from wetwire_gitlab.runner import resolve_module_path

        # Simple case: file in current directory
        path = Path("/project/src/mypackage/jobs.py")
        project_root = Path("/project")
        src_dir = Path("/project/src")

        module_path = resolve_module_path(path, project_root, src_dir)

        assert module_path == "mypackage.jobs"

    def test_resolve_module_path_nested(self):
        """Resolve nested module path."""
        from wetwire_gitlab.runner import resolve_module_path

        path = Path("/project/src/mypackage/ci/jobs.py")
        project_root = Path("/project")
        src_dir = Path("/project/src")

        module_path = resolve_module_path(path, project_root, src_dir)

        assert module_path == "mypackage.ci.jobs"


class TestPyprojectParsing:
    """Tests for pyproject.toml parsing."""

    def test_find_src_directory(self):
        """Find src directory from pyproject.toml."""
        from wetwire_gitlab.runner import find_src_directory

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir)

            pyproject = '''
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/mypackage"]
'''
            (path / "pyproject.toml").write_text(pyproject)
            (path / "src").mkdir()

            src_dir = find_src_directory(path)

        assert src_dir is not None
        assert src_dir.name == "src"

    def test_find_src_directory_default(self):
        """Find src directory with default location."""
        from wetwire_gitlab.runner import find_src_directory

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir)

            # No pyproject.toml, but src/ directory exists
            (path / "src").mkdir()

            src_dir = find_src_directory(path)

        assert src_dir is not None
        assert src_dir.name == "src"

    def test_find_src_directory_none(self):
        """Handle missing src directory."""
        from wetwire_gitlab.runner import find_src_directory

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir)
            src_dir = find_src_directory(path)

        assert src_dir is None


class TestExtractFromDirectory:
    """Tests for extracting values from a directory."""

    def test_extract_all_jobs(self):
        """Extract all jobs from a directory."""
        from wetwire_gitlab.runner import extract_all_jobs

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir)

            code = '''
from dataclasses import dataclass

@dataclass
class Job:
    name: str
    stage: str = "build"
    script: list = None

build = Job(name="build", stage="build", script=["make"])
test = Job(name="test", stage="test", script=["pytest"])
'''
            (path / "jobs.py").write_text(code)

            jobs = extract_all_jobs(path, "Job")

        assert len(jobs) == 2

    def test_extract_all_jobs_multiple_files(self):
        """Extract jobs from multiple files."""
        from wetwire_gitlab.runner import extract_all_jobs

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir)

            code1 = '''
from dataclasses import dataclass

@dataclass
class Job:
    name: str
    stage: str = "build"
    script: list = None

build = Job(name="build", stage="build", script=["make"])
'''
            code2 = '''
from dataclasses import dataclass

@dataclass
class Job:
    name: str
    stage: str = "build"
    script: list = None

test = Job(name="test", stage="test", script=["pytest"])
'''
            (path / "build.py").write_text(code1)
            (path / "test.py").write_text(code2)

            jobs = extract_all_jobs(path, "Job")

        assert len(jobs) == 2


class TestImportErrors:
    """Tests for handling import errors."""

    def test_import_syntax_error(self):
        """Handle syntax errors in imported module."""
        from wetwire_gitlab.runner import import_module_from_path

        code = "def broken syntax {"

        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as f:
            f.write(code)
            f.flush()
            result = import_module_from_path(Path(f.name))

        assert result is None

    def test_import_missing_dependency(self):
        """Handle missing dependencies in imported module."""
        from wetwire_gitlab.runner import import_module_from_path

        code = "from nonexistent_package import something"

        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as f:
            f.write(code)
            f.flush()
            result = import_module_from_path(Path(f.name))

        assert result is None
