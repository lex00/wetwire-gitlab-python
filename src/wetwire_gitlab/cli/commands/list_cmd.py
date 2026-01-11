"""List command implementation."""

import argparse
import json
from pathlib import Path

from wetwire_gitlab.cli.utils import resolve_source_dir, validate_path_exists


def run_list(args: argparse.Namespace) -> int:
    """Execute the list command.

    Args:
        args: Parsed command-line arguments.

    Returns:
        Exit code (0=success, 1=error).
    """
    from wetwire_gitlab.discover import discover_in_directory

    path = Path(args.path)

    if validate_path_exists(path):
        return 1

    scan_dir = resolve_source_dir(path)

    # Discover jobs and pipelines
    result = discover_in_directory(scan_dir)

    if args.format == "json":
        output = {
            "jobs": [
                {
                    "name": job.name,
                    "variable_name": job.variable_name,
                    "file_path": job.file_path,
                    "line_number": job.line_number,
                    "dependencies": job.dependencies,
                }
                for job in result.jobs
            ],
            "pipelines": [
                {
                    "name": pipeline.name,
                    "file_path": pipeline.file_path,
                    "jobs": pipeline.jobs,
                }
                for pipeline in result.pipelines
            ],
        }
        print(json.dumps(output, indent=2))
    else:
        # Table format
        print("Jobs:")
        print("-" * 60)
        if result.jobs:
            for job in result.jobs:
                deps = (
                    f" (needs: {', '.join(job.dependencies)})"
                    if job.dependencies
                    else ""
                )
                print(f"  {job.name:<20} {job.file_path}:{job.line_number}{deps}")
        else:
            print("  No jobs found")

        print()
        print("Pipelines:")
        print("-" * 60)
        if result.pipelines:
            for pipeline in result.pipelines:
                print(f"  {pipeline.name:<20} {pipeline.file_path}")
        else:
            print("  No pipelines found")

    return 0
