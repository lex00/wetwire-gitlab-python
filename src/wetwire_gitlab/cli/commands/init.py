"""Init command implementation."""

import argparse
import sys
from pathlib import Path


def run_init(args: argparse.Namespace) -> int:
    """Execute the init command.

    Args:
        args: Parsed command-line arguments.

    Returns:
        Exit code (0=success, 1=error).
    """
    from wetwire_gitlab.cli.init import create_package

    output_dir = Path(args.output)

    result = create_package(
        output_dir=output_dir,
        name=args.name,
        description=args.description,
        no_scaffold=args.no_scaffold,
        force=args.force,
    )

    if not result["success"]:
        print(f"Error: {result['error']}", file=sys.stderr)
        return 1

    print(result["message"])

    if args.verbose and "files" in result:
        print("\nCreated files:")
        for filepath in result["files"]:
            print(f"  - {filepath}")

    return 0
