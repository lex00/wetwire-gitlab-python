"""Validate command implementation."""

import argparse
import sys
from pathlib import Path


def run_validate(args: argparse.Namespace) -> int:
    """Execute the validate command.

    Args:
        args: Parsed command-line arguments.

    Returns:
        Exit code (0=valid, 1=invalid, 2=error).
    """
    from wetwire_gitlab.validation import (
        GlabNotFoundError,
        is_glab_installed,
        validate_file,
    )

    path = Path(args.path)

    if not path.exists():
        print(f"Error: File does not exist: {path}", file=sys.stderr)
        return 2

    if not is_glab_installed():
        print(
            "Error: glab CLI not installed. "
            "Install from https://gitlab.com/gitlab-org/cli",
            file=sys.stderr,
        )
        return 2

    try:
        result = validate_file(
            path,
            include_jobs=args.include_jobs,
        )

        if result.valid:
            print(f"Pipeline is valid: {path}")
            if result.merged_yaml:
                print(result.merged_yaml)
            return 0
        else:
            print(f"Pipeline is invalid: {path}", file=sys.stderr)
            if result.errors:
                for error in result.errors:
                    print(f"  - {error}", file=sys.stderr)
            return 1

    except GlabNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2
