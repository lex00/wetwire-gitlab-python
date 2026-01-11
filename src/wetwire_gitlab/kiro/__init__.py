"""Kiro CLI integration for wetwire-gitlab.

This module provides integration with Kiro CLI for AI-assisted
pipeline design using the wetwire-gitlab toolchain.

Usage:
    from wetwire_gitlab.kiro import GITLAB_KIRO_CONFIG, install_configs, launch_kiro

    # Install configurations
    install_configs(GITLAB_KIRO_CONFIG)

    # Launch Kiro with wetwire-gitlab-runner agent
    launch_kiro(GITLAB_KIRO_CONFIG, prompt="Create a build/test/deploy pipeline")
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

# Re-export from wetwire-core
from wetwire_core.kiro import (
    KIRO_AVAILABLE,
    KiroConfig,
    check_kiro_installed,
    install_configs,
    launch_kiro,
)

# Domain-specific configuration
from wetwire_gitlab.kiro.config import GITLAB_AGENT_PROMPT, GITLAB_KIRO_CONFIG

if TYPE_CHECKING:
    from typing import Any


def install_kiro_configs(
    project_dir: Path | None = None,
    force: bool = False,
    verbose: bool = False,
) -> dict[str, Any]:
    """Install all Kiro configurations (backwards compatibility wrapper).

    Args:
        project_dir: Project directory for MCP config. Defaults to cwd.
        force: Overwrite existing configs if True.
        verbose: Print status messages.

    Returns:
        Dict with 'agent' and 'mcp' keys indicating what was installed.
    """
    import sys

    if project_dir is None:
        project_dir = Path.cwd()

    try:
        mcp_path, agent_path = install_configs(
            GITLAB_KIRO_CONFIG,
            project_dir=project_dir,
        )

        results = {
            "agent": agent_path.exists(),
            "mcp": mcp_path.exists(),
        }

        if verbose:
            if results["agent"]:
                print(f"Installed agent config: {agent_path}", file=sys.stderr)
            if results["mcp"]:
                print(f"Installed MCP config: {mcp_path}", file=sys.stderr)

        return results
    except Exception:
        return {"agent": False, "mcp": False}


def run_kiro_scenario(
    prompt: str,
    project_dir: Path | None = None,
    timeout: int = 300,
    auto_exit: bool = True,
) -> dict[str, Any]:
    """Run a Kiro CLI scenario non-interactively for testing.

    This function runs kiro-cli with a prompt and captures output,
    suitable for automated testing and CI pipelines.

    Args:
        prompt: The pipeline prompt to send to Kiro.
        project_dir: Project directory. Defaults to temp directory.
        timeout: Maximum time in seconds to wait (default: 300).
        auto_exit: If True, append instruction to exit after completion.

    Returns:
        Dict with keys:
            - success: bool - Whether the scenario completed successfully
            - exit_code: int - Process exit code
            - stdout: str - Captured stdout
            - stderr: str - Captured stderr
            - package_path: str | None - Path to created package if any
            - template_valid: bool - Whether build produced valid template
    """
    import subprocess
    import tempfile

    if not check_kiro_installed():
        return {
            "success": False,
            "exit_code": 1,
            "stdout": "",
            "stderr": "Kiro CLI not found",
            "package_path": None,
            "template_valid": False,
        }

    # Use temp directory if not specified
    if project_dir is None:
        temp_dir = tempfile.mkdtemp(prefix="kiro_test_")
        project_dir = Path(temp_dir)
    else:
        project_dir = Path(project_dir)
        project_dir.mkdir(parents=True, exist_ok=True)

    # Ensure configs are installed
    install_kiro_configs(project_dir=project_dir, verbose=False)

    # Build the full prompt with auto-exit instruction
    full_prompt = prompt
    if auto_exit:
        full_prompt = (
            f"{prompt}\n\n"
            "After successfully creating the package and running lint and build, "
            "output 'SCENARIO_COMPLETE' and exit."
        )

    # Run kiro-cli
    result = launch_kiro(
        GITLAB_KIRO_CONFIG,
        prompt=full_prompt,
        project_dir=project_dir,
        non_interactive=True,
    )

    # Find created package (look for directories with __init__.py)
    package_path = None
    for item in project_dir.iterdir():
        if item.is_dir() and (item / "__init__.py").exists():
            # Skip .kiro directory
            if item.name != ".kiro":
                package_path = str(item)
                break

    # Check if template is valid by running build
    template_valid = False
    if package_path:
        try:
            build_result = subprocess.run(
                ["wetwire-gitlab", "build", package_path],
                capture_output=True,
                text=True,
                timeout=30,
            )
            template_valid = build_result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

    return {
        "success": result.returncode == 0 and template_valid,
        "exit_code": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "package_path": package_path,
        "template_valid": template_valid,
    }


__all__ = [
    # From wetwire-core
    "KiroConfig",
    "KIRO_AVAILABLE",
    "check_kiro_installed",
    "install_configs",
    "launch_kiro",
    # Domain-specific
    "GITLAB_AGENT_PROMPT",
    "GITLAB_KIRO_CONFIG",
    # Backwards compatibility
    "install_kiro_configs",
    "run_kiro_scenario",
]
