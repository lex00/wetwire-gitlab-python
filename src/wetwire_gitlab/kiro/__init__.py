"""Kiro CLI integration for wetwire-gitlab.

This module provides integration with Kiro CLI for AI-assisted
pipeline design using the wetwire-gitlab toolchain.

Usage:
    from wetwire_gitlab.kiro import install_kiro_configs, launch_kiro

    # Install configurations (first run)
    install_kiro_configs()

    # Launch Kiro with wetwire-runner agent
    launch_kiro(prompt="Create a build/test/deploy pipeline")
"""

from wetwire_gitlab.kiro.installer import (
    check_kiro_installed,
    install_kiro_configs,
    launch_kiro,
    run_kiro_scenario,
)

__all__ = [
    "check_kiro_installed",
    "install_kiro_configs",
    "launch_kiro",
    "run_kiro_scenario",
]
