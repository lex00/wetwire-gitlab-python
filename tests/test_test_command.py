"""Tests for test command implementation."""

import subprocess
import sys


class TestTestCommandIntegration:
    """Integration tests for test command."""

    def test_test_help(self):
        """Test command shows help."""
        result = subprocess.run(
            [sys.executable, "-m", "wetwire_gitlab.cli", "test", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "test" in result.stdout.lower()

    def test_test_persona_flag(self):
        """Test command accepts --persona flag."""
        result = subprocess.run(
            [sys.executable, "-m", "wetwire_gitlab.cli", "test", "--help"],
            capture_output=True,
            text=True,
        )
        assert "--persona" in result.stdout

    def test_test_returns_not_available(self):
        """Test command indicates wetwire-core needed."""
        result = subprocess.run(
            [sys.executable, "-m", "wetwire_gitlab.cli", "test"],
            capture_output=True,
            text=True,
        )
        # Should return error and mention wetwire-core
        assert result.returncode != 0
        assert "wetwire-core" in result.stdout.lower() or "wetwire-core" in result.stderr.lower()


class TestTestCommandUnit:
    """Unit tests for test command logic."""

    def test_run_test_function_exists(self):
        """run_test function is importable."""
        from wetwire_gitlab.cli.main import run_test

        assert callable(run_test)
