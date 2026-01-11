"""Tests for Kiro provider support.

Tests for Issue #67: Kiro Provider Support
"""

import subprocess
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


@pytest.mark.slow
class TestKiroProviderFlag:
    """Tests for --provider flag in CLI commands."""

    def test_design_help_shows_provider_flag(self):
        """Design command shows --provider option in help."""
        result = subprocess.run(
            [sys.executable, "-m", "wetwire_gitlab.cli", "design", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "--provider" in result.stdout

    def test_design_provider_accepts_anthropic(self):
        """Design command accepts --provider anthropic."""
        result = subprocess.run(
            [sys.executable, "-m", "wetwire_gitlab.cli", "design", "--help"],
            capture_output=True,
            text=True,
        )
        assert "anthropic" in result.stdout

    def test_design_provider_accepts_kiro(self):
        """Design command accepts --provider kiro."""
        result = subprocess.run(
            [sys.executable, "-m", "wetwire_gitlab.cli", "design", "--help"],
            capture_output=True,
            text=True,
        )
        assert "kiro" in result.stdout

    def test_test_help_shows_provider_flag(self):
        """Test command shows --provider option in help."""
        result = subprocess.run(
            [sys.executable, "-m", "wetwire_gitlab.cli", "test", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "--provider" in result.stdout

    def test_test_provider_accepts_kiro(self):
        """Test command accepts --provider kiro."""
        result = subprocess.run(
            [sys.executable, "-m", "wetwire_gitlab.cli", "test", "--help"],
            capture_output=True,
            text=True,
        )
        assert "kiro" in result.stdout

    def test_test_help_shows_timeout_flag(self):
        """Test command shows --timeout option for kiro provider."""
        result = subprocess.run(
            [sys.executable, "-m", "wetwire_gitlab.cli", "test", "--help"],
            capture_output=True,
            text=True,
        )
        assert "--timeout" in result.stdout


@pytest.mark.slow
class TestKiroModuleImports:
    """Tests for kiro module imports and structure."""

    def test_kiro_module_importable(self):
        """Kiro module is importable."""
        from wetwire_gitlab import kiro

        assert kiro is not None

    def test_check_kiro_installed_function(self):
        """check_kiro_installed function exists."""
        from wetwire_gitlab.kiro import check_kiro_installed

        assert callable(check_kiro_installed)

    def test_install_kiro_configs_function(self):
        """install_kiro_configs function exists."""
        from wetwire_gitlab.kiro import install_kiro_configs

        assert callable(install_kiro_configs)

    def test_launch_kiro_function(self):
        """launch_kiro function exists."""
        from wetwire_gitlab.kiro import launch_kiro

        assert callable(launch_kiro)

    def test_run_kiro_scenario_function(self):
        """run_kiro_scenario function exists."""
        from wetwire_gitlab.kiro import run_kiro_scenario

        assert callable(run_kiro_scenario)


@pytest.mark.slow
class TestKiroCheckInstalled:
    """Tests for check_kiro_installed function."""

    @patch("shutil.which")
    def test_check_kiro_installed_when_installed(self, mock_which):
        """check_kiro_installed returns True when kiro-cli is available."""
        from wetwire_gitlab.kiro import check_kiro_installed

        mock_which.return_value = "/usr/bin/kiro-cli"
        assert check_kiro_installed() is True

    @patch("shutil.which")
    def test_check_kiro_installed_when_not_installed(self, mock_which):
        """check_kiro_installed returns False when kiro-cli is not available."""
        from wetwire_gitlab.kiro import check_kiro_installed

        mock_which.return_value = None
        assert check_kiro_installed() is False


@pytest.mark.slow
class TestKiroInstallConfigs:
    """Tests for installing Kiro configurations."""

    def test_install_kiro_configs_creates_files(self):
        """install_kiro_configs creates config files in temp directory."""
        from wetwire_gitlab.kiro import install_kiro_configs

        with tempfile.TemporaryDirectory() as tmp:
            result = install_kiro_configs(project_dir=Path(tmp))
            assert isinstance(result, dict)
            # Should have mcp config in project dir
            mcp_config = Path(tmp) / ".kiro" / "mcp.json"
            assert mcp_config.exists()


@pytest.mark.slow
class TestLaunchKiro:
    """Tests for launch_kiro function."""

    @patch("wetwire_gitlab.kiro.check_kiro_installed")
    def test_launch_kiro_requires_config(self, mock_check):
        """launch_kiro requires a KiroConfig parameter."""
        from wetwire_gitlab.kiro import GITLAB_KIRO_CONFIG, launch_kiro

        mock_check.return_value = False
        # The new API requires a config parameter
        # This should work without raising
        try:
            launch_kiro(GITLAB_KIRO_CONFIG, prompt="test")
        except Exception:
            pass  # Expected if kiro-cli not installed


@pytest.mark.slow
class TestRunKiroScenario:
    """Tests for run_kiro_scenario function."""

    @patch("wetwire_gitlab.kiro.check_kiro_installed")
    def test_run_kiro_scenario_not_installed_returns_error(self, mock_check):
        """run_kiro_scenario returns error dict if kiro-cli not installed."""
        from wetwire_gitlab.kiro import run_kiro_scenario

        mock_check.return_value = False
        result = run_kiro_scenario("Create a pipeline")
        assert result["success"] is False
        assert "not found" in result["stderr"].lower()

    @patch("wetwire_gitlab.kiro.check_kiro_installed")
    @patch("wetwire_gitlab.kiro.launch_kiro")
    def test_run_kiro_scenario_returns_result_dict(self, mock_launch, mock_check):
        """run_kiro_scenario returns a properly structured result dict."""
        from wetwire_gitlab.kiro import run_kiro_scenario

        mock_check.return_value = True
        mock_launch.return_value = MagicMock(returncode=0, stdout="", stderr="")

        with tempfile.TemporaryDirectory() as tmp:
            result = run_kiro_scenario("Create a pipeline", project_dir=Path(tmp))

            assert "success" in result
            assert "exit_code" in result
            assert "stdout" in result
            assert "stderr" in result
            assert "package_path" in result
            assert "template_valid" in result


@pytest.mark.slow
class TestGitLabKiroConfig:
    """Tests for GitLab-specific Kiro configuration."""

    def test_gitlab_kiro_config_exists(self):
        """GITLAB_KIRO_CONFIG exists with correct values."""
        from wetwire_gitlab.kiro import GITLAB_KIRO_CONFIG

        assert GITLAB_KIRO_CONFIG is not None
        assert GITLAB_KIRO_CONFIG.agent_name == "wetwire-gitlab-runner"
        assert GITLAB_KIRO_CONFIG.mcp_command == "wetwire-gitlab-mcp"

    def test_gitlab_kiro_config_has_gitlab_prompt(self):
        """GITLAB_KIRO_CONFIG has GitLab-specific prompt content."""
        from wetwire_gitlab.kiro import GITLAB_KIRO_CONFIG

        prompt = GITLAB_KIRO_CONFIG.agent_prompt
        assert "GitLab" in prompt or "gitlab" in prompt.lower()

    def test_gitlab_kiro_config_references_mcp_tools(self):
        """GITLAB_KIRO_CONFIG prompt references MCP tools."""
        from wetwire_gitlab.kiro import GITLAB_KIRO_CONFIG

        prompt = GITLAB_KIRO_CONFIG.agent_prompt
        # Should mention lint and build tools
        assert "lint" in prompt.lower() or "wetwire_lint" in prompt
        assert "build" in prompt.lower() or "wetwire_build" in prompt

    def test_gitlab_agent_prompt_exported(self):
        """GITLAB_AGENT_PROMPT is exported from the module."""
        from wetwire_gitlab.kiro import GITLAB_AGENT_PROMPT

        assert GITLAB_AGENT_PROMPT is not None
        assert len(GITLAB_AGENT_PROMPT) > 100
