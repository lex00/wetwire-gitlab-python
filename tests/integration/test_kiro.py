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
class TestKiroInstaller:
    """Tests for Kiro configuration installer."""

    def test_agent_config_path(self):
        """get_agent_config_path returns correct path."""
        from wetwire_gitlab.kiro.installer import get_agent_config_path

        path = get_agent_config_path()
        assert path.name == "wetwire-runner.json"
        assert "agents" in str(path)

    def test_mcp_config_path_default(self):
        """get_mcp_config_path returns correct path."""
        from wetwire_gitlab.kiro.installer import get_mcp_config_path

        path = get_mcp_config_path()
        assert path.name == "mcp.json"
        assert ".kiro" in str(path)

    def test_mcp_config_path_with_project_dir(self):
        """get_mcp_config_path uses project directory."""
        from wetwire_gitlab.kiro.installer import get_mcp_config_path

        with tempfile.TemporaryDirectory() as tmp:
            path = get_mcp_config_path(Path(tmp))
            assert str(tmp) in str(path)
            assert path.name == "mcp.json"

    @patch("shutil.which")
    def test_check_kiro_installed_when_installed(self, mock_which):
        """check_kiro_installed returns True when kiro-cli is available."""
        from wetwire_gitlab.kiro import check_kiro_installed

        mock_which.return_value = "/usr/bin/kiro-cli"
        assert check_kiro_installed() is True
        mock_which.assert_called_once_with("kiro-cli")

    @patch("shutil.which")
    def test_check_kiro_installed_when_not_installed(self, mock_which):
        """check_kiro_installed returns False when kiro-cli is not available."""
        from wetwire_gitlab.kiro import check_kiro_installed

        mock_which.return_value = None
        assert check_kiro_installed() is False


@pytest.mark.slow
class TestKiroInstallConfigs:
    """Tests for installing Kiro configurations."""

    def test_install_agent_config_creates_file(self):
        """install_agent_config creates the agent config file."""
        from wetwire_gitlab.kiro.installer import install_agent_config

        with tempfile.TemporaryDirectory() as tmp:
            with patch(
                "wetwire_gitlab.kiro.installer.get_agent_config_path"
            ) as mock_path:
                config_path = Path(tmp) / ".kiro" / "agents" / "wetwire-runner.json"
                mock_path.return_value = config_path

                result = install_agent_config()
                assert result is True
                assert config_path.exists()

    def test_install_agent_config_skips_existing(self):
        """install_agent_config skips if config exists."""
        from wetwire_gitlab.kiro.installer import install_agent_config

        with tempfile.TemporaryDirectory() as tmp:
            with patch(
                "wetwire_gitlab.kiro.installer.get_agent_config_path"
            ) as mock_path:
                config_path = Path(tmp) / ".kiro" / "agents" / "wetwire-runner.json"
                config_path.parent.mkdir(parents=True, exist_ok=True)
                config_path.write_text('{"existing": true}')
                mock_path.return_value = config_path

                result = install_agent_config(force=False)
                assert result is False

    def test_install_mcp_config_creates_file(self):
        """install_mcp_config creates the MCP config file."""
        from wetwire_gitlab.kiro.installer import install_mcp_config

        with tempfile.TemporaryDirectory() as tmp:
            result = install_mcp_config(project_dir=Path(tmp))
            assert result is True
            config_path = Path(tmp) / ".kiro" / "mcp.json"
            assert config_path.exists()


@pytest.mark.slow
class TestLaunchKiro:
    """Tests for launch_kiro function."""

    @patch("wetwire_gitlab.kiro.installer.check_kiro_installed")
    def test_launch_kiro_not_installed_returns_error(self, mock_check):
        """launch_kiro returns 1 if kiro-cli not installed."""
        from wetwire_gitlab.kiro import launch_kiro

        mock_check.return_value = False
        result = launch_kiro()
        assert result == 1

    @patch("wetwire_gitlab.kiro.installer.check_kiro_installed")
    @patch("wetwire_gitlab.kiro.installer.install_kiro_configs")
    @patch("subprocess.run")
    def test_launch_kiro_calls_kiro_cli(self, mock_run, mock_install, mock_check):
        """launch_kiro calls kiro-cli with correct arguments."""
        from wetwire_gitlab.kiro import launch_kiro

        mock_check.return_value = True
        mock_run.return_value = MagicMock(returncode=0)

        result = launch_kiro(prompt="Create a pipeline")
        assert result == 0
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert "kiro-cli" in call_args
        assert "chat" in call_args
        assert "--agent" in call_args
        assert "wetwire-runner" in call_args


@pytest.mark.slow
class TestRunKiroScenario:
    """Tests for run_kiro_scenario function."""

    @patch("wetwire_gitlab.kiro.installer.check_kiro_installed")
    def test_run_kiro_scenario_not_installed_returns_error(self, mock_check):
        """run_kiro_scenario returns error dict if kiro-cli not installed."""
        from wetwire_gitlab.kiro import run_kiro_scenario

        mock_check.return_value = False
        result = run_kiro_scenario("Create a pipeline")
        assert result["success"] is False
        assert "not found" in result["stderr"].lower()

    @patch("wetwire_gitlab.kiro.installer.check_kiro_installed")
    @patch("wetwire_gitlab.kiro.installer.install_kiro_configs")
    @patch("wetwire_gitlab.kiro.installer._run_with_script")
    def test_run_kiro_scenario_returns_result_dict(
        self, mock_run, mock_install, mock_check
    ):
        """run_kiro_scenario returns a properly structured result dict."""
        from wetwire_gitlab.kiro import run_kiro_scenario

        mock_check.return_value = True
        mock_run.return_value = (0, "output", "")

        with tempfile.TemporaryDirectory() as tmp:
            result = run_kiro_scenario("Create a pipeline", project_dir=Path(tmp))

            assert "success" in result
            assert "exit_code" in result
            assert "stdout" in result
            assert "stderr" in result
            assert "package_path" in result
            assert "template_valid" in result


@pytest.mark.slow
class TestKiroAgentConfig:
    """Tests for Kiro agent configuration content."""

    def test_agent_config_has_gitlab_prompt(self):
        """Agent config has GitLab-specific prompt content."""
        from wetwire_gitlab.kiro.installer import AGENT_CONFIG

        assert "name" in AGENT_CONFIG
        assert AGENT_CONFIG["name"] == "wetwire-runner"
        assert "prompt" in AGENT_CONFIG
        assert (
            "GitLab" in AGENT_CONFIG["prompt"]
            or "gitlab" in AGENT_CONFIG["prompt"].lower()
        )

    def test_agent_config_references_mcp_tools(self):
        """Agent config references MCP tools."""
        from wetwire_gitlab.kiro.installer import AGENT_CONFIG

        prompt = AGENT_CONFIG["prompt"]
        # Should mention lint and build tools
        assert "lint" in prompt.lower() or "wetwire_lint" in prompt
        assert "build" in prompt.lower() or "wetwire_build" in prompt
