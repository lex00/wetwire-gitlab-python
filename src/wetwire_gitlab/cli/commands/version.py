"""Version command implementation."""

import argparse


def run_version(args: argparse.Namespace) -> int:
    """Execute the version command.

    Args:
        args: Parsed command-line arguments.

    Returns:
        Exit code (0=success).
    """
    from wetwire_gitlab import __version__

    print(f"wetwire-gitlab {__version__}")
    return 0
