"""Tests for CLI utilities from wetwire-core.

These tests verify that wetwire_core.cli utilities are available and work correctly.
The original wetwire_gitlab.cli.cli_utils module was removed as dead code per Issue #145.
"""

import tempfile
from pathlib import Path


class TestErrorExit:
    """Tests for error_exit utility function from wetwire-core."""

    def test_error_exit_importable(self):
        """error_exit function is importable from wetwire_core.cli."""
        from wetwire_core.cli import error_exit

        assert callable(error_exit)


class TestValidatePackagePath:
    """Tests for validate_package_path utility function from wetwire-core."""

    def test_validate_package_path_importable(self):
        """validate_package_path function is importable from wetwire_core.cli."""
        from wetwire_core.cli import validate_package_path

        assert callable(validate_package_path)

    def test_validate_package_path_resolves_existing(self):
        """validate_package_path resolves existing paths."""
        from wetwire_core.cli import validate_package_path

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)
            result = validate_package_path(path)
            assert result.exists()
            assert result.is_absolute()


class TestRequireOptionalDependency:
    """Tests for require_optional_dependency utility function from wetwire-core."""

    def test_require_optional_dependency_importable(self):
        """require_optional_dependency function is importable from wetwire_core.cli."""
        from wetwire_core.cli import require_optional_dependency

        assert callable(require_optional_dependency)


class TestResolveOutputDir:
    """Tests for resolve_output_dir utility function from wetwire-core."""

    def test_resolve_output_dir_importable(self):
        """resolve_output_dir function is importable from wetwire_core.cli."""
        from wetwire_core.cli import resolve_output_dir

        assert callable(resolve_output_dir)

    def test_resolve_output_dir_returns_path(self):
        """resolve_output_dir returns Path for existing directory."""
        from wetwire_core.cli import resolve_output_dir

        with tempfile.TemporaryDirectory() as tmp:
            result = resolve_output_dir(Path(tmp))
            assert result.is_absolute()
