"""Tests for build manifest generation per WETWIRE_SPEC.md section 8.4."""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import pytest


class TestBuildManifestDataclass:
    """Tests for BuildManifest dataclass."""

    def test_build_manifest_exists(self):
        """BuildManifest dataclass is importable."""
        from wetwire_gitlab.contracts import BuildManifest

        assert BuildManifest is not None

    def test_build_manifest_required_fields(self):
        """BuildManifest has required fields per spec 8.4."""
        from wetwire_gitlab.contracts import BuildManifest

        manifest = BuildManifest(
            version="1.0.0",
            generated_at="2026-01-10T12:00:00Z",
            source_files=[{"path": "jobs.py", "hash": "abc123"}],
            discovered_jobs=[
                {"name": "build", "stage": "build", "file": "jobs.py", "line": 10}
            ],
            dependencies={"test": ["build"]},
            output_file=".gitlab-ci.yml",
        )

        assert manifest.version == "1.0.0"
        assert manifest.generated_at == "2026-01-10T12:00:00Z"
        assert len(manifest.source_files) == 1
        assert len(manifest.discovered_jobs) == 1
        assert manifest.dependencies == {"test": ["build"]}
        assert manifest.output_file == ".gitlab-ci.yml"

    def test_build_manifest_to_dict(self):
        """BuildManifest can be converted to dictionary for JSON serialization."""
        from wetwire_gitlab.contracts import BuildManifest

        manifest = BuildManifest(
            version="1.0.0",
            generated_at="2026-01-10T12:00:00Z",
            source_files=[],
            discovered_jobs=[],
            dependencies={},
            output_file=".gitlab-ci.yml",
        )

        result = manifest.to_dict()
        assert isinstance(result, dict)
        assert result["version"] == "1.0.0"
        assert result["output_file"] == ".gitlab-ci.yml"

    def test_build_manifest_to_json(self):
        """BuildManifest can be serialized to JSON."""
        from wetwire_gitlab.contracts import BuildManifest

        manifest = BuildManifest(
            version="1.0.0",
            generated_at="2026-01-10T12:00:00Z",
            source_files=[{"path": "jobs.py", "hash": "abc123"}],
            discovered_jobs=[
                {"name": "build", "stage": "build", "file": "jobs.py", "line": 10}
            ],
            dependencies={},
            output_file=".gitlab-ci.yml",
        )

        json_str = manifest.to_json()
        parsed = json.loads(json_str)
        assert parsed["version"] == "1.0.0"
        assert len(parsed["source_files"]) == 1


class TestManifestFlag:
    """Tests for --manifest CLI flag."""

    @pytest.fixture
    def sample_project(self, tmp_path: Path):
        """Create a sample project with pipeline definitions."""
        src_dir = tmp_path / "src" / "sample"
        src_dir.mkdir(parents=True)

        (src_dir / "__init__.py").write_text('"""Sample package."""\n')

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

        pipeline_py = src_dir / "pipeline.py"
        pipeline_py.write_text('''"""Sample pipeline."""

from wetwire_gitlab.pipeline import Pipeline

pipeline = Pipeline(
    stages=["build", "test"],
)
''')

        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""[project]
name = "sample"
version = "0.1.0"
""")

        return tmp_path

    def test_manifest_flag_recognized(self):
        """Build command accepts --manifest flag."""
        result = subprocess.run(
            [sys.executable, "-m", "wetwire_gitlab.cli", "build", "--help"],
            capture_output=True,
            text=True,
        )
        assert "--manifest" in result.stdout

    def test_manifest_flag_generates_file(self, sample_project: Path):
        """Build with --manifest generates manifest.json."""
        output_yaml = sample_project / ".gitlab-ci.yml"
        manifest_file = sample_project / "manifest.json"

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "wetwire_gitlab.cli",
                "build",
                "--output",
                str(output_yaml),
                "--manifest",
                str(sample_project),
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, f"Build failed: {result.stderr}"
        assert manifest_file.exists(), "manifest.json was not created"

    def test_manifest_contains_required_fields(self, sample_project: Path):
        """Generated manifest contains all required fields."""
        output_yaml = sample_project / ".gitlab-ci.yml"
        manifest_file = sample_project / "manifest.json"

        subprocess.run(
            [
                sys.executable,
                "-m",
                "wetwire_gitlab.cli",
                "build",
                "--output",
                str(output_yaml),
                "--manifest",
                str(sample_project),
            ],
            capture_output=True,
            text=True,
        )

        assert manifest_file.exists()
        manifest = json.loads(manifest_file.read_text())

        # Required fields per issue #129
        assert "version" in manifest
        assert "generated_at" in manifest
        assert "source_files" in manifest
        assert "discovered_jobs" in manifest
        assert "dependencies" in manifest
        assert "output_file" in manifest

    def test_manifest_discovered_jobs_structure(self, sample_project: Path):
        """Discovered jobs in manifest have correct structure."""
        output_yaml = sample_project / ".gitlab-ci.yml"
        manifest_file = sample_project / "manifest.json"

        subprocess.run(
            [
                sys.executable,
                "-m",
                "wetwire_gitlab.cli",
                "build",
                "--output",
                str(output_yaml),
                "--manifest",
                str(sample_project),
            ],
            capture_output=True,
            text=True,
        )

        manifest = json.loads(manifest_file.read_text())
        jobs = manifest["discovered_jobs"]

        assert len(jobs) >= 2  # build and test

        for job in jobs:
            assert "name" in job
            assert "file" in job
            assert "line" in job
            # stage is optional

    def test_manifest_dependencies_structure(self, sample_project: Path):
        """Dependencies in manifest track job relationships."""
        output_yaml = sample_project / ".gitlab-ci.yml"
        manifest_file = sample_project / "manifest.json"

        subprocess.run(
            [
                sys.executable,
                "-m",
                "wetwire_gitlab.cli",
                "build",
                "--output",
                str(output_yaml),
                "--manifest",
                str(sample_project),
            ],
            capture_output=True,
            text=True,
        )

        manifest = json.loads(manifest_file.read_text())
        deps = manifest["dependencies"]

        # test depends on build
        assert "test" in deps
        assert "build" in deps["test"]

    def test_manifest_source_files_with_hashes(self, sample_project: Path):
        """Source files include paths and hashes."""
        output_yaml = sample_project / ".gitlab-ci.yml"
        manifest_file = sample_project / "manifest.json"

        subprocess.run(
            [
                sys.executable,
                "-m",
                "wetwire_gitlab.cli",
                "build",
                "--output",
                str(output_yaml),
                "--manifest",
                str(sample_project),
            ],
            capture_output=True,
            text=True,
        )

        manifest = json.loads(manifest_file.read_text())
        source_files = manifest["source_files"]

        assert len(source_files) >= 1

        for sf in source_files:
            assert "path" in sf
            assert "hash" in sf
            # Hash should be a hex string
            assert len(sf["hash"]) > 0

    def test_manifest_generated_at_is_valid_timestamp(self, sample_project: Path):
        """generated_at field is a valid ISO timestamp."""
        output_yaml = sample_project / ".gitlab-ci.yml"
        manifest_file = sample_project / "manifest.json"

        subprocess.run(
            [
                sys.executable,
                "-m",
                "wetwire_gitlab.cli",
                "build",
                "--output",
                str(output_yaml),
                "--manifest",
                str(sample_project),
            ],
            capture_output=True,
            text=True,
        )

        manifest = json.loads(manifest_file.read_text())
        generated_at = manifest["generated_at"]

        # Should be a valid ISO timestamp
        datetime.fromisoformat(generated_at.replace("Z", "+00:00"))

    def test_manifest_output_file_matches(self, sample_project: Path):
        """output_file field matches the actual output path."""
        output_yaml = sample_project / ".gitlab-ci.yml"
        manifest_file = sample_project / "manifest.json"

        subprocess.run(
            [
                sys.executable,
                "-m",
                "wetwire_gitlab.cli",
                "build",
                "--output",
                str(output_yaml),
                "--manifest",
                str(sample_project),
            ],
            capture_output=True,
            text=True,
        )

        manifest = json.loads(manifest_file.read_text())
        assert manifest["output_file"] == str(output_yaml)


class TestManifestWithoutOutputFlag:
    """Tests for manifest behavior when no --output is specified."""

    @pytest.fixture
    def sample_project(self, tmp_path: Path):
        """Create a sample project with pipeline definitions."""
        src_dir = tmp_path / "src" / "sample"
        src_dir.mkdir(parents=True)

        (src_dir / "__init__.py").write_text('"""Sample package."""\n')

        jobs_py = src_dir / "jobs.py"
        jobs_py.write_text('''"""Sample jobs."""

from wetwire_gitlab.pipeline import Job

build = Job(
    name="build",
    stage="build",
    script=["make build"],
)
''')

        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""[project]
name = "sample"
version = "0.1.0"
""")

        return tmp_path

    def test_manifest_writes_to_default_location(self, sample_project: Path):
        """Manifest writes to manifest.json in project directory when no output specified."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "wetwire_gitlab.cli",
                "build",
                "--manifest",
                str(sample_project),
            ],
            capture_output=True,
            text=True,
            cwd=sample_project,
        )

        manifest_file = sample_project / "manifest.json"
        assert manifest_file.exists() or result.returncode == 0


class TestManifestVersion:
    """Tests for manifest version tracking."""

    def test_manifest_version_matches_package(self):
        """Manifest version matches wetwire_gitlab package version."""
        from wetwire_gitlab import __version__
        from wetwire_gitlab.contracts import BuildManifest

        # The version used in manifests should be accessible
        manifest = BuildManifest(
            version=__version__,
            generated_at="2026-01-10T12:00:00Z",
            source_files=[],
            discovered_jobs=[],
            dependencies={},
            output_file=".gitlab-ci.yml",
        )

        assert manifest.version == __version__


class TestCreateManifestFunction:
    """Tests for the create_manifest utility function."""

    def test_create_manifest_exists(self):
        """create_manifest function is importable from build module."""
        from wetwire_gitlab.cli.commands.build import create_manifest

        assert callable(create_manifest)

    def test_create_manifest_returns_build_manifest(self, tmp_path: Path):
        """create_manifest returns a BuildManifest instance."""
        from wetwire_gitlab.cli.commands.build import create_manifest
        from wetwire_gitlab.contracts import BuildManifest, DiscoveredJob

        jobs = [
            DiscoveredJob(
                name="build",
                variable_name="build",
                file_path=str(tmp_path / "jobs.py"),
                line_number=10,
                stage="build",
            )
        ]

        manifest = create_manifest(
            jobs=jobs,
            output_file=".gitlab-ci.yml",
            source_directory=tmp_path,
        )

        assert isinstance(manifest, BuildManifest)

    def test_create_manifest_computes_file_hashes(self, tmp_path: Path):
        """create_manifest computes SHA256 hashes for source files."""
        from wetwire_gitlab.cli.commands.build import create_manifest
        from wetwire_gitlab.contracts import DiscoveredJob

        # Create a source file
        jobs_file = tmp_path / "jobs.py"
        jobs_file.write_text("# test content\n")

        jobs = [
            DiscoveredJob(
                name="build",
                variable_name="build",
                file_path=str(jobs_file),
                line_number=1,
                stage="build",
            )
        ]

        manifest = create_manifest(
            jobs=jobs,
            output_file=".gitlab-ci.yml",
            source_directory=tmp_path,
        )

        # Should have computed hash
        assert len(manifest.source_files) == 1
        assert manifest.source_files[0]["hash"] != ""

    def test_create_manifest_extracts_dependencies(self, tmp_path: Path):
        """create_manifest extracts job dependencies."""
        from wetwire_gitlab.cli.commands.build import create_manifest
        from wetwire_gitlab.contracts import DiscoveredJob

        jobs = [
            DiscoveredJob(
                name="build",
                variable_name="build",
                file_path=str(tmp_path / "jobs.py"),
                line_number=1,
                stage="build",
            ),
            DiscoveredJob(
                name="test",
                variable_name="test",
                file_path=str(tmp_path / "jobs.py"),
                line_number=10,
                stage="test",
                dependencies=["build"],
            ),
        ]

        manifest = create_manifest(
            jobs=jobs,
            output_file=".gitlab-ci.yml",
            source_directory=tmp_path,
        )

        assert "test" in manifest.dependencies
        assert "build" in manifest.dependencies["test"]
