"""Tests for init command implementation."""

import subprocess
import sys
import tempfile
from pathlib import Path


class TestInitCommandIntegration:
    """Integration tests for init command."""

    def test_init_help(self):
        """Init command shows help."""
        result = subprocess.run(
            [sys.executable, "-m", "wetwire_gitlab.cli", "init", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "init" in result.stdout.lower()

    def test_init_output_flag(self):
        """Init command accepts --output flag."""
        result = subprocess.run(
            [sys.executable, "-m", "wetwire_gitlab.cli", "init", "--help"],
            capture_output=True,
            text=True,
        )
        assert "--output" in result.stdout or "-o" in result.stdout

    def test_init_name_flag(self):
        """Init command accepts --name flag."""
        result = subprocess.run(
            [sys.executable, "-m", "wetwire_gitlab.cli", "init", "--help"],
            capture_output=True,
            text=True,
        )
        assert "--name" in result.stdout

    def test_init_force_flag(self):
        """Init command accepts --force flag."""
        result = subprocess.run(
            [sys.executable, "-m", "wetwire_gitlab.cli", "init", "--help"],
            capture_output=True,
            text=True,
        )
        assert "--force" in result.stdout or "-f" in result.stdout

    def test_init_creates_package(self):
        """Init command creates a package directory."""
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                [sys.executable, "-m", "wetwire_gitlab.cli", "init", "--name", "test_pipeline", "-o", tmp],
                capture_output=True,
                text=True,
            )
            assert result.returncode == 0
            pkg_dir = Path(tmp) / "test_pipeline"
            assert pkg_dir.exists()
            assert (pkg_dir / "__init__.py").exists()
            assert (pkg_dir / "jobs.py").exists()
            assert (pkg_dir / "pipeline.py").exists()

    def test_init_creates_buildable_package(self):
        """Init creates a package that can be built."""
        with tempfile.TemporaryDirectory() as tmp:
            # Create package
            subprocess.run(
                [sys.executable, "-m", "wetwire_gitlab.cli", "init", "--name", "build_test", "-o", tmp],
                capture_output=True,
                text=True,
            )
            # Build package
            pkg_dir = Path(tmp) / "build_test"
            result = subprocess.run(
                [sys.executable, "-m", "wetwire_gitlab.cli", "build", str(pkg_dir)],
                capture_output=True,
                text=True,
            )
            assert result.returncode == 0
            assert "stages:" in result.stdout

    def test_init_force_overwrites(self):
        """Init --force overwrites existing package."""
        with tempfile.TemporaryDirectory() as tmp:
            pkg_dir = Path(tmp) / "my_pipeline"
            pkg_dir.mkdir()
            (pkg_dir / "existing.txt").write_text("existing")

            result = subprocess.run(
                [sys.executable, "-m", "wetwire_gitlab.cli", "init", "--name", "my_pipeline", "-o", tmp, "--force"],
                capture_output=True,
                text=True,
            )
            assert result.returncode == 0
            assert (pkg_dir / "__init__.py").exists()

    def test_init_without_force_fails_on_existing(self):
        """Init without --force fails on existing package."""
        with tempfile.TemporaryDirectory() as tmp:
            pkg_dir = Path(tmp) / "my_pipeline"
            pkg_dir.mkdir()
            (pkg_dir / "__init__.py").write_text("# existing")

            result = subprocess.run(
                [sys.executable, "-m", "wetwire_gitlab.cli", "init", "--name", "my_pipeline", "-o", tmp],
                capture_output=True,
                text=True,
            )
            assert result.returncode != 0

    def test_init_no_scaffold_skips_extras(self):
        """Init --no-scaffold skips README and CLAUDE.md."""
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                [sys.executable, "-m", "wetwire_gitlab.cli", "init", "--name", "no_scaffold_test", "-o", tmp, "--no-scaffold"],
                capture_output=True,
                text=True,
            )
            assert result.returncode == 0
            pkg_dir = Path(tmp) / "no_scaffold_test"
            assert (pkg_dir / "__init__.py").exists()
            # Scaffolding files should not exist
            assert not (Path(tmp) / "README.md").exists()
            assert not (Path(tmp) / "CLAUDE.md").exists()

    def test_init_verbose_lists_files(self):
        """Init --verbose lists created files."""
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                [sys.executable, "-m", "wetwire_gitlab.cli", "init", "--name", "verbose_test", "-o", tmp, "--verbose"],
                capture_output=True,
                text=True,
            )
            assert result.returncode == 0
            # Should mention files created
            assert "__init__.py" in result.stdout or "jobs.py" in result.stdout


class TestInitCommandUnit:
    """Unit tests for init command logic."""

    def test_run_init_function_exists(self):
        """run_init function is importable."""
        from wetwire_gitlab.cli.main import run_init

        assert callable(run_init)

    def test_create_package_importable(self):
        """create_package function is importable from init module."""
        from wetwire_gitlab.cli.init import create_package

        assert callable(create_package)

    def test_create_package_returns_result(self):
        """create_package returns result dict."""
        from wetwire_gitlab.cli.init import create_package

        with tempfile.TemporaryDirectory() as tmp:
            result = create_package(
                output_dir=Path(tmp),
                name="test_pkg",
                description="Test package",
            )
            assert "success" in result
            assert result["success"] is True

    def test_create_package_creates_init_py(self):
        """create_package creates __init__.py."""
        from wetwire_gitlab.cli.init import create_package

        with tempfile.TemporaryDirectory() as tmp:
            create_package(
                output_dir=Path(tmp),
                name="test_pkg",
            )
            init_file = Path(tmp) / "test_pkg" / "__init__.py"
            assert init_file.exists()
            content = init_file.read_text()
            # Uses relative imports
            assert "from .jobs import" in content
            assert "from .pipeline import" in content

    def test_create_package_creates_jobs_py(self):
        """create_package creates jobs.py."""
        from wetwire_gitlab.cli.init import create_package

        with tempfile.TemporaryDirectory() as tmp:
            create_package(
                output_dir=Path(tmp),
                name="test_pkg",
            )
            jobs_file = Path(tmp) / "test_pkg" / "jobs.py"
            assert jobs_file.exists()
            content = jobs_file.read_text()
            assert "Job" in content

    def test_create_package_creates_pipeline_py(self):
        """create_package creates pipeline.py."""
        from wetwire_gitlab.cli.init import create_package

        with tempfile.TemporaryDirectory() as tmp:
            create_package(
                output_dir=Path(tmp),
                name="test_pkg",
            )
            pipeline_file = Path(tmp) / "test_pkg" / "pipeline.py"
            assert pipeline_file.exists()
            content = pipeline_file.read_text()
            assert "Pipeline" in content

    def test_create_package_invalid_name(self):
        """create_package rejects invalid names."""
        from wetwire_gitlab.cli.init import create_package

        with tempfile.TemporaryDirectory() as tmp:
            result = create_package(
                output_dir=Path(tmp),
                name="invalid-name",  # Dashes not allowed
            )
            assert result["success"] is False
            assert "error" in result


class TestScaffoldFiles:
    """Tests for scaffold file generation."""

    def test_readme_generated_by_default(self):
        """README.md is generated by default."""
        from wetwire_gitlab.cli.init import create_package

        with tempfile.TemporaryDirectory() as tmp:
            create_package(
                output_dir=Path(tmp),
                name="scaffold_test",
            )
            readme = Path(tmp) / "README.md"
            assert readme.exists()
            content = readme.read_text()
            assert "scaffold_test" in content

    def test_claude_md_generated_by_default(self):
        """CLAUDE.md is generated by default."""
        from wetwire_gitlab.cli.init import create_package

        with tempfile.TemporaryDirectory() as tmp:
            create_package(
                output_dir=Path(tmp),
                name="scaffold_test",
            )
            claude_md = Path(tmp) / "CLAUDE.md"
            assert claude_md.exists()
            content = claude_md.read_text()
            assert "wetwire-gitlab" in content.lower() or "GitLab" in content

    def test_gitignore_generated_by_default(self):
        """gitignore is generated by default."""
        from wetwire_gitlab.cli.init import create_package

        with tempfile.TemporaryDirectory() as tmp:
            create_package(
                output_dir=Path(tmp),
                name="scaffold_test",
            )
            gitignore = Path(tmp) / ".gitignore"
            assert gitignore.exists()
            content = gitignore.read_text()
            assert "__pycache__" in content

    def test_no_scaffold_skips_files(self):
        """no_scaffold=True skips README, CLAUDE.md, .gitignore."""
        from wetwire_gitlab.cli.init import create_package

        with tempfile.TemporaryDirectory() as tmp:
            create_package(
                output_dir=Path(tmp),
                name="no_scaffold",
                no_scaffold=True,
            )
            assert not (Path(tmp) / "README.md").exists()
            assert not (Path(tmp) / "CLAUDE.md").exists()
            assert not (Path(tmp) / ".gitignore").exists()
            # But package files should still exist
            assert (Path(tmp) / "no_scaffold" / "__init__.py").exists()
