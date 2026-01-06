"""Tests for CLI module."""

import subprocess
import sys


class TestCLIEntry:
    """Tests for CLI entry point."""

    def test_cli_help(self):
        """CLI shows help message."""
        result = subprocess.run(
            [sys.executable, "-m", "wetwire_gitlab.cli", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "wetwire-gitlab" in result.stdout.lower() or "usage" in result.stdout.lower()

    def test_cli_version(self):
        """CLI shows version."""
        result = subprocess.run(
            [sys.executable, "-m", "wetwire_gitlab.cli", "version"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "0.1.0" in result.stdout


class TestBuildCommand:
    """Tests for build command."""

    def test_build_help(self):
        """Build command shows help."""
        result = subprocess.run(
            [sys.executable, "-m", "wetwire_gitlab.cli", "build", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "build" in result.stdout.lower()

    def test_build_type_flag(self):
        """Build command accepts --type flag."""
        result = subprocess.run(
            [sys.executable, "-m", "wetwire_gitlab.cli", "build", "--help"],
            capture_output=True,
            text=True,
        )
        assert "--type" in result.stdout or "-t" in result.stdout


class TestValidateCommand:
    """Tests for validate command."""

    def test_validate_help(self):
        """Validate command shows help."""
        result = subprocess.run(
            [sys.executable, "-m", "wetwire_gitlab.cli", "validate", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0


class TestListCommand:
    """Tests for list command."""

    def test_list_help(self):
        """List command shows help."""
        result = subprocess.run(
            [sys.executable, "-m", "wetwire_gitlab.cli", "list", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0


class TestLintCommand:
    """Tests for lint command."""

    def test_lint_help(self):
        """Lint command shows help."""
        result = subprocess.run(
            [sys.executable, "-m", "wetwire_gitlab.cli", "lint", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0


class TestImportCommand:
    """Tests for import command."""

    def test_import_help(self):
        """Import command shows help."""
        result = subprocess.run(
            [sys.executable, "-m", "wetwire_gitlab.cli", "import", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0


class TestInitCommand:
    """Tests for init command."""

    def test_init_help(self):
        """Init command shows help."""
        result = subprocess.run(
            [sys.executable, "-m", "wetwire_gitlab.cli", "init", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0


class TestDesignCommand:
    """Tests for design command."""

    def test_design_help(self):
        """Design command shows help."""
        result = subprocess.run(
            [sys.executable, "-m", "wetwire_gitlab.cli", "design", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0


class TestTestCommand:
    """Tests for test command."""

    def test_test_help(self):
        """Test command shows help."""
        result = subprocess.run(
            [sys.executable, "-m", "wetwire_gitlab.cli", "test", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0


class TestGraphCommand:
    """Tests for graph command."""

    def test_graph_help(self):
        """Graph command shows help."""
        result = subprocess.run(
            [sys.executable, "-m", "wetwire_gitlab.cli", "graph", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0


class TestExitCodes:
    """Tests for exit code semantics."""

    def test_unknown_command_exits_nonzero(self):
        """Unknown command exits with error code."""
        result = subprocess.run(
            [sys.executable, "-m", "wetwire_gitlab.cli", "unknown_command"],
            capture_output=True,
            text=True,
        )
        assert result.returncode != 0


class TestParserAPI:
    """Tests for CLI parser API (unit tests)."""

    def test_create_parser(self):
        """Parser can be created."""
        from wetwire_gitlab.cli import create_parser

        parser = create_parser()
        assert parser is not None

    def test_parser_has_subcommands(self):
        """Parser has all required subcommands."""
        from wetwire_gitlab.cli import create_parser

        parser = create_parser()
        # Parse help to check subcommands exist
        args = parser.parse_args(["build", "."])
        assert args.command == "build"

    def test_build_command_type_default(self):
        """Build command type defaults to pipeline."""
        from wetwire_gitlab.cli import create_parser

        parser = create_parser()
        args = parser.parse_args(["build", "."])
        assert args.type == "pipeline"

    def test_build_command_type_runner(self):
        """Build command accepts runner type."""
        from wetwire_gitlab.cli import create_parser

        parser = create_parser()
        args = parser.parse_args(["build", "--type", "runner", "."])
        assert args.type == "runner"

    def test_build_command_output_flag(self):
        """Build command accepts output flag."""
        from wetwire_gitlab.cli import create_parser

        parser = create_parser()
        args = parser.parse_args(["build", "--output", "ci.yml", "."])
        assert args.output == "ci.yml"

    def test_build_command_format_flag(self):
        """Build command accepts format flag."""
        from wetwire_gitlab.cli import create_parser

        parser = create_parser()
        args = parser.parse_args(["build", "--format", "json", "."])
        assert args.format == "json"
