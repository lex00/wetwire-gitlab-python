"""Tests for refactored Kiro module using wetwire-core.

Tests for Issue #143: Remove duplicated Kiro code and unused agent_config.json
"""

import pytest


class TestKiroConfigFromCore:
    """Tests for KiroConfig import from wetwire-core."""

    def test_kiro_config_imported_from_core(self):
        """KiroConfig should be imported from wetwire_core."""
        from wetwire_core.kiro import KiroConfig as CoreKiroConfig

        from wetwire_gitlab.kiro import KiroConfig

        assert KiroConfig is CoreKiroConfig

    def test_gitlab_kiro_config_exists(self):
        """GITLAB_KIRO_CONFIG should exist with domain-specific values."""
        from wetwire_gitlab.kiro import GITLAB_KIRO_CONFIG

        assert GITLAB_KIRO_CONFIG is not None
        assert GITLAB_KIRO_CONFIG.agent_name == "wetwire-gitlab-runner"
        assert GITLAB_KIRO_CONFIG.mcp_command == "wetwire-gitlab-mcp"

    def test_gitlab_kiro_config_has_prompt(self):
        """GITLAB_KIRO_CONFIG should have a GitLab-specific prompt."""
        from wetwire_gitlab.kiro import GITLAB_KIRO_CONFIG

        assert GITLAB_KIRO_CONFIG.agent_prompt is not None
        assert len(GITLAB_KIRO_CONFIG.agent_prompt) > 100
        # Should mention GitLab-specific content
        prompt_lower = GITLAB_KIRO_CONFIG.agent_prompt.lower()
        assert "gitlab" in prompt_lower or "ci/cd" in prompt_lower


class TestKiroCoreFunctions:
    """Tests for functions re-exported from wetwire-core."""

    def test_check_kiro_installed_from_core(self):
        """check_kiro_installed should be from wetwire_core."""
        from wetwire_core.kiro import check_kiro_installed as core_check

        from wetwire_gitlab.kiro import check_kiro_installed

        assert check_kiro_installed is core_check

    def test_install_configs_from_core(self):
        """install_configs should be from wetwire_core."""
        from wetwire_core.kiro import install_configs as core_install

        from wetwire_gitlab.kiro import install_configs

        assert install_configs is core_install

    def test_launch_kiro_from_core(self):
        """launch_kiro should be from wetwire_core."""
        from wetwire_core.kiro import launch_kiro as core_launch

        from wetwire_gitlab.kiro import launch_kiro

        assert launch_kiro is core_launch

    def test_kiro_available_from_core(self):
        """KIRO_AVAILABLE should be from wetwire_core."""
        from wetwire_core.kiro import KIRO_AVAILABLE as CORE_KIRO_AVAILABLE

        from wetwire_gitlab.kiro import KIRO_AVAILABLE

        assert KIRO_AVAILABLE is CORE_KIRO_AVAILABLE


class TestInstallerRemoved:
    """Tests verifying installer.py is removed."""

    def test_installer_module_not_importable(self):
        """installer.py should not exist."""
        with pytest.raises(ImportError):
            from wetwire_gitlab.kiro import installer  # noqa: F401

    def test_agent_config_json_not_exists(self):
        """agent_config.json should not exist."""
        from pathlib import Path

        from wetwire_gitlab import kiro

        kiro_dir = Path(kiro.__file__).parent
        config_path = kiro_dir / "agent_config.json"
        assert not config_path.exists(), f"agent_config.json should be removed: {config_path}"


class TestBackwardsCompatibility:
    """Tests for backwards compatibility wrappers."""

    def test_install_kiro_configs_wrapper_exists(self):
        """install_kiro_configs wrapper should exist for backwards compatibility."""
        from wetwire_gitlab.kiro import install_kiro_configs

        assert callable(install_kiro_configs)

    def test_install_kiro_configs_accepts_old_args(self):
        """install_kiro_configs should accept old argument signature."""
        import tempfile
        from pathlib import Path

        from wetwire_gitlab.kiro import install_kiro_configs

        with tempfile.TemporaryDirectory() as tmp:
            # Old signature: install_kiro_configs(project_dir=None, force=False, verbose=False)
            result = install_kiro_configs(project_dir=Path(tmp), force=True, verbose=False)
            # Should return dict with 'agent' and 'mcp' keys
            assert isinstance(result, dict)
            assert "agent" in result or "mcp" in result
