"""Tests for CLI utilities module."""

import tempfile
from pathlib import Path


class TestErrorExit:
    """Tests for error_exit utility function."""

    def test_error_exit_importable(self):
        """error_exit function is importable."""
        from wetwire_gitlab.cli.cli_utils import error_exit

        assert callable(error_exit)

    def test_error_exit_returns_exit_code(self, capsys):
        """error_exit returns exit code 1."""
        from wetwire_gitlab.cli.cli_utils import error_exit

        result = error_exit("Test error")
        assert result == 1

    def test_error_exit_prints_error_message(self, capsys):
        """error_exit prints error message to stderr."""
        from wetwire_gitlab.cli.cli_utils import error_exit

        error_exit("Test error message")
        captured = capsys.readouterr()
        assert "Test error message" in captured.err

    def test_error_exit_prints_hint(self, capsys):
        """error_exit prints hint when provided."""
        from wetwire_gitlab.cli.cli_utils import error_exit

        error_exit("Error", hint="Try this fix")
        captured = capsys.readouterr()
        assert "Try this fix" in captured.err


class TestValidatePackagePath:
    """Tests for validate_package_path utility function."""

    def test_validate_package_path_importable(self):
        """validate_package_path function is importable."""
        from wetwire_gitlab.cli.cli_utils import validate_package_path

        assert callable(validate_package_path)

    def test_validate_package_path_resolves_existing(self):
        """validate_package_path resolves existing paths."""
        from wetwire_gitlab.cli.cli_utils import validate_package_path

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)
            result = validate_package_path(path)
            assert result.exists()
            assert result.is_absolute()

    def test_validate_package_path_returns_none_for_nonexistent(self):
        """validate_package_path returns None for nonexistent paths."""
        from wetwire_gitlab.cli.cli_utils import validate_package_path

        result = validate_package_path(Path("/nonexistent/path/xyz123"))
        assert result is None

    def test_validate_package_path_finds_src_directory(self):
        """validate_package_path finds src/ subdirectory."""
        from wetwire_gitlab.cli.cli_utils import validate_package_path

        with tempfile.TemporaryDirectory() as tmp:
            src_dir = Path(tmp) / "src"
            src_dir.mkdir()
            (src_dir / "package").mkdir()
            result = validate_package_path(Path(tmp))
            assert result is not None
            assert "src" in str(result)


class TestRequireOptionalDependency:
    """Tests for require_optional_dependency utility function."""

    def test_require_optional_dependency_importable(self):
        """require_optional_dependency function is importable."""
        from wetwire_gitlab.cli.cli_utils import require_optional_dependency

        assert callable(require_optional_dependency)

    def test_require_optional_dependency_returns_true_for_installed(self):
        """require_optional_dependency returns True for installed packages."""
        from wetwire_gitlab.cli.cli_utils import require_optional_dependency

        # pytest is definitely installed
        result = require_optional_dependency("pytest", "pytest")
        assert result is True

    def test_require_optional_dependency_returns_false_for_missing(self):
        """require_optional_dependency returns False for missing packages."""
        from wetwire_gitlab.cli.cli_utils import require_optional_dependency

        result = require_optional_dependency(
            "nonexistent_package_xyz123", "nonexistent-package"
        )
        assert result is False


class TestResolveOutputDir:
    """Tests for resolve_output_dir utility function."""

    def test_resolve_output_dir_importable(self):
        """resolve_output_dir function is importable."""
        from wetwire_gitlab.cli.cli_utils import resolve_output_dir

        assert callable(resolve_output_dir)

    def test_resolve_output_dir_creates_directory(self):
        """resolve_output_dir creates directory if it doesn't exist."""
        from wetwire_gitlab.cli.cli_utils import resolve_output_dir

        with tempfile.TemporaryDirectory() as tmp:
            new_dir = Path(tmp) / "new_output"
            result = resolve_output_dir(new_dir, create=True)
            assert result.exists()

    def test_resolve_output_dir_returns_absolute(self):
        """resolve_output_dir returns absolute path."""
        from wetwire_gitlab.cli.cli_utils import resolve_output_dir

        with tempfile.TemporaryDirectory() as tmp:
            result = resolve_output_dir(Path(tmp))
            assert result.is_absolute()


class TestAddCommonArgs:
    """Tests for add_common_args utility function."""

    def test_add_common_args_importable(self):
        """add_common_args function is importable."""
        from wetwire_gitlab.cli.cli_utils import add_common_args

        assert callable(add_common_args)

    def test_add_common_args_adds_verbose(self):
        """add_common_args adds --verbose flag."""
        import argparse

        from wetwire_gitlab.cli.cli_utils import add_common_args

        parser = argparse.ArgumentParser()
        add_common_args(parser)
        args = parser.parse_args(["--verbose"])
        assert args.verbose is True

    def test_add_common_args_adds_format(self):
        """add_common_args adds --format flag."""
        import argparse

        from wetwire_gitlab.cli.cli_utils import add_common_args

        parser = argparse.ArgumentParser()
        add_common_args(parser, include_format=True)
        args = parser.parse_args(["--format", "json"])
        assert args.format == "json"


class TestPrintSuccess:
    """Tests for print_success utility function."""

    def test_print_success_importable(self):
        """print_success function is importable."""
        from wetwire_gitlab.cli.cli_utils import print_success

        assert callable(print_success)

    def test_print_success_prints_message(self, capsys):
        """print_success prints success message."""
        from wetwire_gitlab.cli.cli_utils import print_success

        print_success("Operation completed")
        captured = capsys.readouterr()
        assert "Operation completed" in captured.out


class TestPrintWarning:
    """Tests for print_warning utility function."""

    def test_print_warning_importable(self):
        """print_warning function is importable."""
        from wetwire_gitlab.cli.cli_utils import print_warning

        assert callable(print_warning)

    def test_print_warning_prints_message(self, capsys):
        """print_warning prints warning message to stderr."""
        from wetwire_gitlab.cli.cli_utils import print_warning

        print_warning("Something might be wrong")
        captured = capsys.readouterr()
        assert "Something might be wrong" in captured.err
