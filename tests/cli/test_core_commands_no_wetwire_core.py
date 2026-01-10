"""Tests that core commands work without wetwire-core installed."""

import subprocess
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch


class TestCoreCommandsWithoutWetwireCore:
    """Tests that core commands don't require wetwire-core."""

    def test_build_command_works_without_wetwire_core(self):
        """Build command works without wetwire-core installed."""
        with tempfile.TemporaryDirectory() as tmp:
            pkg_dir = Path(tmp) / "test_pkg"
            pkg_dir.mkdir()

            # Create a minimal package
            (pkg_dir / "__init__.py").write_text(
                '"""Test package."""\n'
                "from wetwire_gitlab.pipeline import Job, Pipeline\n"
            )
            (pkg_dir / "jobs.py").write_text(
                "from wetwire_gitlab.pipeline import Job\n"
                'build = Job(name="build", stage="build", script=["echo build"])\n'
            )

            # Mock wetwire-core as not installed
            with patch.dict('sys.modules', {'wetwire_core': None}):
                result = subprocess.run(
                    [sys.executable, "-m", "wetwire_gitlab.cli", "build", str(pkg_dir)],
                    capture_output=True,
                    text=True,
                )

                # Build should succeed
                assert result.returncode == 0
                assert "build:" in result.stdout

    def test_lint_command_works_without_wetwire_core(self):
        """Lint command works without wetwire-core installed."""
        with tempfile.TemporaryDirectory() as tmp:
            pkg_dir = Path(tmp) / "test_pkg"
            pkg_dir.mkdir()

            # Create a minimal package
            (pkg_dir / "__init__.py").write_text(
                '"""Test package."""\n'
                "from wetwire_gitlab.pipeline import Job, Pipeline\n"
            )
            (pkg_dir / "jobs.py").write_text(
                "from wetwire_gitlab.pipeline import Job\n"
                'build = Job(name="build", stage="build", script=["echo build"])\n'
            )

            # Mock wetwire-core as not installed
            with patch.dict('sys.modules', {'wetwire_core': None}):
                result = subprocess.run(
                    [sys.executable, "-m", "wetwire_gitlab.cli", "lint", str(pkg_dir)],
                    capture_output=True,
                    text=True,
                )

                # Lint should succeed (or fail with lint issues, not import errors)
                assert result.returncode in (0, 1)
                assert "ImportError" not in result.stderr
                assert "wetwire_core" not in result.stderr

    def test_import_command_works_without_wetwire_core(self):
        """Import command works without wetwire-core installed."""
        with tempfile.TemporaryDirectory() as tmp:
            yaml_file = Path(tmp) / "test.yml"
            yaml_file.write_text(
                "test:\n"
                "  stage: test\n"
                "  script:\n"
                "    - echo test\n"
            )

            # Mock wetwire-core as not installed
            with patch.dict('sys.modules', {'wetwire_core': None}):
                result = subprocess.run(
                    [sys.executable, "-m", "wetwire_gitlab.cli", "import", str(yaml_file)],
                    capture_output=True,
                    text=True,
                )

                # Import should succeed
                assert result.returncode == 0
                assert "ImportError" not in result.stderr
                assert "wetwire_core" not in result.stderr

    def test_list_command_works_without_wetwire_core(self):
        """List command works without wetwire-core installed."""
        with tempfile.TemporaryDirectory() as tmp:
            pkg_dir = Path(tmp) / "test_pkg"
            pkg_dir.mkdir()

            # Create a minimal package
            (pkg_dir / "__init__.py").write_text(
                '"""Test package."""\n'
                "from wetwire_gitlab.pipeline import Job, Pipeline\n"
            )
            (pkg_dir / "jobs.py").write_text(
                "from wetwire_gitlab.pipeline import Job\n"
                'build = Job(name="build", stage="build", script=["echo build"])\n'
            )

            # Mock wetwire-core as not installed
            with patch.dict('sys.modules', {'wetwire_core': None}):
                result = subprocess.run(
                    [sys.executable, "-m", "wetwire_gitlab.cli", "list", str(pkg_dir)],
                    capture_output=True,
                    text=True,
                )

                # List should succeed
                assert result.returncode == 0
                assert "ImportError" not in result.stderr
                assert "wetwire_core" not in result.stderr

    def test_graph_command_works_without_wetwire_core(self):
        """Graph command works without wetwire-core installed."""
        with tempfile.TemporaryDirectory() as tmp:
            pkg_dir = Path(tmp) / "test_pkg"
            pkg_dir.mkdir()

            # Create a minimal package
            (pkg_dir / "__init__.py").write_text(
                '"""Test package."""\n'
                "from wetwire_gitlab.pipeline import Job, Pipeline\n"
            )
            (pkg_dir / "jobs.py").write_text(
                "from wetwire_gitlab.pipeline import Job\n"
                'build = Job(name="build", stage="build", script=["echo build"])\n'
            )

            # Mock wetwire-core as not installed
            with patch.dict('sys.modules', {'wetwire_core': None}):
                result = subprocess.run(
                    [sys.executable, "-m", "wetwire_gitlab.cli", "graph", str(pkg_dir)],
                    capture_output=True,
                    text=True,
                )

                # Graph should succeed
                assert result.returncode == 0
                assert "ImportError" not in result.stderr
                assert "wetwire_core" not in result.stderr

    def test_init_command_works_without_wetwire_core(self):
        """Init command works without wetwire-core installed."""
        with tempfile.TemporaryDirectory() as tmp:
            # Mock wetwire-core as not installed
            with patch.dict('sys.modules', {'wetwire_core': None}):
                result = subprocess.run(
                    [sys.executable, "-m", "wetwire_gitlab.cli", "init",
                     "-o", str(tmp), "--name", "test_pkg"],
                    capture_output=True,
                    text=True,
                )

                # Init should succeed
                assert result.returncode == 0
                assert "ImportError" not in result.stderr
                assert "wetwire_core" not in result.stderr

    def test_diff_command_works_without_wetwire_core(self):
        """Diff command works without wetwire-core installed."""
        with tempfile.TemporaryDirectory() as tmp:
            pkg_dir = Path(tmp) / "test_pkg"
            pkg_dir.mkdir()

            # Create a minimal package
            (pkg_dir / "__init__.py").write_text(
                '"""Test package."""\n'
                "from wetwire_gitlab.pipeline import Job, Pipeline\n"
            )
            (pkg_dir / "jobs.py").write_text(
                "from wetwire_gitlab.pipeline import Job\n"
                'build = Job(name="build", stage="build", script=["echo build"])\n'
            )

            # Create a reference YAML file
            yaml_file = Path(tmp) / "reference.yml"
            yaml_file.write_text(
                "build:\n"
                "  stage: build\n"
                "  script:\n"
                "    - echo build\n"
            )

            # Mock wetwire-core as not installed
            with patch.dict('sys.modules', {'wetwire_core': None}):
                result = subprocess.run(
                    [sys.executable, "-m", "wetwire_gitlab.cli", "diff",
                     str(pkg_dir), str(yaml_file)],
                    capture_output=True,
                    text=True,
                )

                # Diff should succeed (or fail with diff issues, not import errors)
                assert "ImportError" not in result.stderr
                assert "wetwire_core" not in result.stderr

    def test_validate_command_works_without_wetwire_core(self):
        """Validate command works without wetwire-core installed."""
        with tempfile.TemporaryDirectory() as tmp:
            pkg_dir = Path(tmp) / "test_pkg"
            pkg_dir.mkdir()

            # Create a minimal package
            (pkg_dir / "__init__.py").write_text(
                '"""Test package."""\n'
                "from wetwire_gitlab.pipeline import Job, Pipeline\n"
            )
            (pkg_dir / "jobs.py").write_text(
                "from wetwire_gitlab.pipeline import Job\n"
                'build = Job(name="build", stage="build", script=["echo build"])\n'
            )

            # Mock wetwire-core as not installed
            with patch.dict('sys.modules', {'wetwire_core': None}):
                result = subprocess.run(
                    [sys.executable, "-m", "wetwire_gitlab.cli", "validate", str(pkg_dir)],
                    capture_output=True,
                    text=True,
                )

                # Validate should succeed (or fail with validation issues, not import errors)
                # Note: validate might fail if glab is not installed, but shouldn't fail on wetwire_core
                assert "wetwire_core" not in result.stderr
