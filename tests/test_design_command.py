"""Tests for design command implementation."""

import subprocess
import sys


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

    def test_design_returns_not_available(self):
        """Design command indicates wetwire-core needed."""
        result = subprocess.run(
            [sys.executable, "-m", "wetwire_gitlab.cli", "design"],
            capture_output=True,
            text=True,
        )
        # Should return error and mention wetwire-core
        assert result.returncode != 0
        assert "wetwire-core" in result.stdout.lower() or "wetwire-core" in result.stderr.lower()


class TestDesignCommandUnit:
    """Unit tests for design command logic."""

    def test_run_design_function_exists(self):
        """run_design function is importable."""
        from wetwire_gitlab.cli.main import run_design

        assert callable(run_design)
