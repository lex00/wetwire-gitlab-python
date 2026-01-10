"""Tests for design command implementation."""

import subprocess
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch


class TestDesignCommandIntegration:
    """Integration tests for design command."""

    def test_design_help(self):
        """Design command shows help."""
        result = subprocess.run(
            [sys.executable, "-m", "wetwire_gitlab.cli", "design", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "design" in result.stdout.lower()

    def test_design_stream_flag(self):
        """Design command accepts --stream flag."""
        result = subprocess.run(
            [sys.executable, "-m", "wetwire_gitlab.cli", "design", "--help"],
            capture_output=True,
            text=True,
        )
        assert "--stream" in result.stdout

    def test_design_max_lint_cycles_flag(self):
        """Design command accepts --max-lint-cycles flag."""
        result = subprocess.run(
            [sys.executable, "-m", "wetwire_gitlab.cli", "design", "--help"],
            capture_output=True,
            text=True,
        )
        assert "--max-lint-cycles" in result.stdout


class TestDesignCommandUnit:
    """Unit tests for design command logic."""

    def test_run_design_function_exists(self):
        """run_design function is importable."""
        from wetwire_gitlab.cli.main import run_design

        assert callable(run_design)

    def test_run_design_imports_from_wetwire_core(self):
        """Design command uses wetwire-core components."""
        # Should be able to import the conversation handler
        from wetwire_core.agents import InteractiveConversationHandler

        assert InteractiveConversationHandler is not None

    def test_run_design_imports_gitlab_agent(self):
        """Design command uses GitLabRunnerAgent."""
        from wetwire_gitlab.agent import GitLabRunnerAgent

        assert GitLabRunnerAgent is not None

    @patch("wetwire_gitlab.agent.anthropic")
    def test_detect_existing_package(self, mock_anthropic):
        """detect_existing_package finds wetwire-gitlab packages."""
        from wetwire_gitlab.agent import detect_existing_package

        with tempfile.TemporaryDirectory() as tmp:
            pkg_dir = Path(tmp) / "my_pipeline"
            pkg_dir.mkdir()
            # Create an __init__.py with Pipeline/Job imports
            (pkg_dir / "__init__.py").write_text(
                '"""Pipeline package."""\n'
                "from wetwire_gitlab.pipeline import Pipeline, Job\n"
            )
            (pkg_dir / "jobs.py").write_text("# jobs")

            name, files = detect_existing_package(pkg_dir)
            assert name == "my_pipeline"
            assert "jobs.py" in files

    def test_detect_existing_package_not_found(self):
        """detect_existing_package returns None for non-packages."""
        from wetwire_gitlab.agent import detect_existing_package

        with tempfile.TemporaryDirectory() as tmp:
            name, files = detect_existing_package(Path(tmp))
            assert name is None
            assert files == []


class TestDesignCommandWithMockedAPI:
    """Tests that mock the Anthropic API."""

    @patch("wetwire_gitlab.agent.anthropic")
    def test_design_with_mocked_api(self, mock_anthropic):
        """Design command works with mocked API."""
        from wetwire_gitlab.agent import GitLabRunnerAgent

        # Setup mock client
        mock_client = MagicMock()
        mock_anthropic.Anthropic.return_value = mock_client

        with tempfile.TemporaryDirectory() as tmp:
            agent = GitLabRunnerAgent(output_dir=Path(tmp))
            # Just verify agent is created correctly
            assert agent.output_dir == Path(tmp)


class TestDesignCommandOptionalDependency:
    """Tests for optional wetwire-core dependency."""

    def test_design_command_shows_error_without_wetwire_core(self):
        """Design command shows helpful error when wetwire-core is not installed."""
        # This test simulates missing wetwire-core by patching the import
        with patch.dict(
            "sys.modules",
            {
                "wetwire_core": None,
                "wetwire_core.agents": None,
                "wetwire_core.runner": None,
            },
        ):
            # Mock argparse namespace
            args = MagicMock()
            args.path = Path.cwd()
            args.provider = "anthropic"  # Default provider that uses wetwire-core

            # Import after patching to get the error handling
            import importlib

            from wetwire_gitlab.cli.commands import design

            importlib.reload(design)

            # Mock input to avoid hanging
            with patch("builtins.input", return_value="test prompt"):
                result = design.run_design(args)

            # Should return error code
            assert result == 1

    def test_design_command_error_message_mentions_installation(self, capsys):
        """Error message suggests how to install wetwire-core."""
        with patch.dict(
            "sys.modules", {"wetwire_core": None, "wetwire_core.agents": None}
        ):
            args = MagicMock()
            args.path = Path.cwd()
            args.provider = "anthropic"

            import importlib

            from wetwire_gitlab.cli.commands import design

            importlib.reload(design)

            with patch("builtins.input", return_value="test"):
                design.run_design(args)

            captured = capsys.readouterr()
            # Should mention wetwire-core and how to install
            assert (
                "wetwire-core" in captured.err.lower()
                or "wetwire-core" in captured.out.lower()
            )
            assert (
                "install" in captured.err.lower() or "install" in captured.out.lower()
            )
