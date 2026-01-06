"""Tests for AST-based pipeline and job discovery."""

import tempfile
from pathlib import Path


class TestDiscoverJobs:
    """Tests for discovering Job declarations in Python files."""

    def test_discover_simple_job(self):
        """Discover a simple Job declaration."""
        from wetwire_gitlab.discover import discover_jobs

        code = '''
from wetwire_gitlab.pipeline import Job

build_job = Job(name="build", stage="build", script=["make build"])
'''
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as f:
            f.write(code)
            f.flush()
            jobs = discover_jobs(Path(f.name))

        assert len(jobs) == 1
        assert jobs[0].name == "build"
        assert jobs[0].variable_name == "build_job"
        assert jobs[0].line_number >= 1

    def test_discover_multiple_jobs(self):
        """Discover multiple Job declarations in a file."""
        from wetwire_gitlab.discover import discover_jobs

        code = '''
from wetwire_gitlab.pipeline import Job

build = Job(name="build", stage="build", script=["make"])
test = Job(name="test", stage="test", script=["pytest"])
deploy = Job(name="deploy", stage="deploy", script=["deploy"])
'''
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as f:
            f.write(code)
            f.flush()
            jobs = discover_jobs(Path(f.name))

        assert len(jobs) == 3
        names = {j.name for j in jobs}
        assert names == {"build", "test", "deploy"}

    def test_discover_job_with_needs(self):
        """Discover a Job with needs dependencies."""
        from wetwire_gitlab.discover import discover_jobs

        code = '''
from wetwire_gitlab.pipeline import Job

build = Job(name="build", stage="build", script=["make"])
test = Job(name="test", stage="test", script=["pytest"], needs=["build"])
'''
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as f:
            f.write(code)
            f.flush()
            jobs = discover_jobs(Path(f.name))

        test_job = next(j for j in jobs if j.name == "test")
        assert test_job.dependencies is not None
        assert "build" in test_job.dependencies

    def test_discover_job_without_name(self):
        """Job without explicit name uses variable name."""
        from wetwire_gitlab.discover import discover_jobs

        code = '''
from wetwire_gitlab.pipeline import Job

my_job = Job(stage="build", script=["make"])
'''
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as f:
            f.write(code)
            f.flush()
            jobs = discover_jobs(Path(f.name))

        assert len(jobs) == 1
        # Job name might be empty or derived from variable
        assert jobs[0].variable_name == "my_job"


class TestDiscoverPipelines:
    """Tests for discovering Pipeline declarations in Python files."""

    def test_discover_simple_pipeline(self):
        """Discover a simple Pipeline declaration."""
        from wetwire_gitlab.discover import discover_pipelines

        code = '''
from wetwire_gitlab.pipeline import Pipeline

ci_pipeline = Pipeline(stages=["build", "test", "deploy"])
'''
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as f:
            f.write(code)
            f.flush()
            pipelines = discover_pipelines(Path(f.name))

        assert len(pipelines) == 1
        assert pipelines[0].name == "ci_pipeline"

    def test_discover_pipeline_with_jobs(self):
        """Discover Pipeline with associated jobs."""
        from wetwire_gitlab.discover import discover_pipelines

        code = '''
from wetwire_gitlab.pipeline import Pipeline, Job

build = Job(name="build", stage="build", script=["make"])
test = Job(name="test", stage="test", script=["pytest"])
pipeline = Pipeline(stages=["build", "test"])
'''
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as f:
            f.write(code)
            f.flush()
            pipelines = discover_pipelines(Path(f.name))

        assert len(pipelines) == 1
        assert pipelines[0].name == "pipeline"


class TestDiscoverDirectory:
    """Tests for recursive directory discovery."""

    def test_discover_in_directory(self):
        """Discover jobs across multiple files in a directory."""
        from wetwire_gitlab.discover import discover_in_directory

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir)

            # Create first file
            (path / "jobs.py").write_text('''
from wetwire_gitlab.pipeline import Job
build = Job(name="build", stage="build", script=["make"])
''')

            # Create second file
            (path / "tests.py").write_text('''
from wetwire_gitlab.pipeline import Job
test = Job(name="test", stage="test", script=["pytest"])
''')

            result = discover_in_directory(path)

        assert len(result.jobs) == 2
        job_names = {j.name for j in result.jobs}
        assert job_names == {"build", "test"}

    def test_discover_excludes_pycache(self):
        """Discovery excludes __pycache__ directories."""
        from wetwire_gitlab.discover import discover_in_directory

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir)

            # Create valid file
            (path / "jobs.py").write_text('''
from wetwire_gitlab.pipeline import Job
build = Job(name="build", stage="build", script=["make"])
''')

            # Create __pycache__ directory with file
            pycache = path / "__pycache__"
            pycache.mkdir()
            (pycache / "cached.py").write_text('''
from wetwire_gitlab.pipeline import Job
cached_job = Job(name="cached", stage="test", script=["echo cached"])
''')

            result = discover_in_directory(path)

        assert len(result.jobs) == 1
        assert result.jobs[0].name == "build"

    def test_discover_excludes_hidden_dirs(self):
        """Discovery excludes hidden directories."""
        from wetwire_gitlab.discover import discover_in_directory

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir)

            # Create valid file
            (path / "jobs.py").write_text('''
from wetwire_gitlab.pipeline import Job
build = Job(name="build", stage="build", script=["make"])
''')

            # Create .hidden directory with file
            hidden = path / ".hidden"
            hidden.mkdir()
            (hidden / "hidden.py").write_text('''
from wetwire_gitlab.pipeline import Job
hidden_job = Job(name="hidden", stage="test", script=["echo"])
''')

            result = discover_in_directory(path)

        assert len(result.jobs) == 1
        assert result.jobs[0].name == "build"

    def test_discover_recursive(self):
        """Discovery is recursive into subdirectories."""
        from wetwire_gitlab.discover import discover_in_directory

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir)

            # Create file in root
            (path / "root_jobs.py").write_text('''
from wetwire_gitlab.pipeline import Job
root = Job(name="root", stage="build", script=["make"])
''')

            # Create subdirectory with file
            subdir = path / "subdir"
            subdir.mkdir()
            (subdir / "sub_jobs.py").write_text('''
from wetwire_gitlab.pipeline import Job
sub = Job(name="sub", stage="test", script=["pytest"])
''')

            result = discover_in_directory(path)

        assert len(result.jobs) == 2
        job_names = {j.name for j in result.jobs}
        assert job_names == {"root", "sub"}


class TestDependencyGraph:
    """Tests for building dependency graphs."""

    def test_build_dependency_graph(self):
        """Build dependency graph from discovered jobs."""
        from wetwire_gitlab.contracts import DiscoveredJob
        from wetwire_gitlab.discover import build_dependency_graph

        jobs = [
            DiscoveredJob(
                name="build",
                variable_name="build",
                file_path="jobs.py",
                line_number=1,
            ),
            DiscoveredJob(
                name="test",
                variable_name="test",
                file_path="jobs.py",
                line_number=2,
                dependencies=["build"],
            ),
            DiscoveredJob(
                name="deploy",
                variable_name="deploy",
                file_path="jobs.py",
                line_number=3,
                dependencies=["test"],
            ),
        ]

        graph = build_dependency_graph(jobs)

        assert "build" in graph
        assert "test" in graph
        assert "deploy" in graph
        assert graph["test"] == ["build"]
        assert graph["deploy"] == ["test"]

    def test_validate_references(self):
        """Validate that all job references exist."""
        from wetwire_gitlab.contracts import DiscoveredJob
        from wetwire_gitlab.discover import validate_references

        jobs = [
            DiscoveredJob(
                name="build",
                variable_name="build",
                file_path="jobs.py",
                line_number=1,
            ),
            DiscoveredJob(
                name="test",
                variable_name="test",
                file_path="jobs.py",
                line_number=2,
                dependencies=["build"],
            ),
        ]

        errors = validate_references(jobs)
        assert len(errors) == 0

    def test_validate_references_missing(self):
        """Detect missing job references."""
        from wetwire_gitlab.contracts import DiscoveredJob
        from wetwire_gitlab.discover import validate_references

        jobs = [
            DiscoveredJob(
                name="test",
                variable_name="test",
                file_path="jobs.py",
                line_number=1,
                dependencies=["nonexistent"],
            ),
        ]

        errors = validate_references(jobs)
        assert len(errors) == 1
        assert "nonexistent" in errors[0]


class TestDiscoverSingleFile:
    """Tests for discovering from a single file."""

    def test_discover_file(self):
        """Discover both jobs and pipelines from a single file."""
        from wetwire_gitlab.discover import discover_file

        code = '''
from wetwire_gitlab.pipeline import Job, Pipeline

build = Job(name="build", stage="build", script=["make"])
test = Job(name="test", stage="test", script=["pytest"])
pipeline = Pipeline(stages=["build", "test"])
'''
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as f:
            f.write(code)
            f.flush()
            result = discover_file(Path(f.name))

        assert len(result.jobs) == 2
        assert len(result.pipelines) == 1

    def test_discover_non_python_file(self):
        """Non-Python files are skipped."""
        from wetwire_gitlab.discover import discover_file

        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False, mode="w") as f:
            f.write("not python")
            f.flush()
            result = discover_file(Path(f.name))

        assert len(result.jobs) == 0
        assert len(result.pipelines) == 0

    def test_discover_syntax_error_file(self):
        """Files with syntax errors are handled gracefully."""
        from wetwire_gitlab.discover import discover_file

        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as f:
            f.write("def broken syntax {")
            f.flush()
            result = discover_file(Path(f.name))

        assert len(result.jobs) == 0
        assert len(result.pipelines) == 0
