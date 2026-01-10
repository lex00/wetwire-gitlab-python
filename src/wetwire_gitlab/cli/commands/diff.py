"""Diff command implementation."""

import argparse
import difflib
import sys
from pathlib import Path


def run_diff(args: argparse.Namespace) -> int:
    """Execute the diff command.

    Args:
        args: Parsed command-line arguments.

    Returns:
        Exit code (0=identical, 1=different, 2=error).
    """
    import yaml

    from wetwire_gitlab.pipeline import Pipeline
    from wetwire_gitlab.runner import extract_all_jobs, extract_all_pipelines
    from wetwire_gitlab.serialize import build_pipeline_yaml

    path = Path(args.path)

    # Check if path exists
    if not path.exists():
        print(f"Error: Path does not exist: {path}", file=sys.stderr)
        return 2

    # Determine original file path
    if hasattr(args, "original") and args.original:
        original_path = Path(args.original)
    else:
        # Default to .gitlab-ci.yml in the path directory
        if path.is_file():
            original_path = path.parent / ".gitlab-ci.yml"
        else:
            original_path = path / ".gitlab-ci.yml"

    # Check if original file exists
    if not original_path.exists():
        print(f"Error: Original file does not exist: {original_path}", file=sys.stderr)
        return 2

    # Read original file
    try:
        original_content = original_path.read_text()
    except Exception as e:
        print(f"Error reading original file: {e}", file=sys.stderr)
        return 2

    # Check if path points to a generated YAML file directly
    # This allows comparing two YAML files directly for testing
    if path.is_file() and path.suffix in [".yml", ".yaml"]:
        try:
            generated_content = path.read_text()
        except Exception as e:
            print(f"Error reading generated file: {e}", file=sys.stderr)
            return 2
    else:
        # Find the source directory
        if path.is_file():
            scan_dir = path.parent
        else:
            # Look for src directory
            src_dir = path / "src"
            if src_dir.exists():
                scan_dir = src_dir
            else:
                scan_dir = path

        # Extract jobs and pipelines
        try:
            jobs = extract_all_jobs(scan_dir)
            pipelines = extract_all_pipelines(scan_dir)
        except Exception as e:
            print(f"Error extracting jobs and pipelines: {e}", file=sys.stderr)
            return 2

        if not jobs:
            print("Error: No jobs found in package", file=sys.stderr)
            return 2

        # Use the first pipeline found, or create a default one
        if pipelines:
            pipeline = pipelines[0]
        else:
            # Infer stages from jobs
            stages_set: set[str] = set()
            for job in jobs:
                if hasattr(job, "stage") and job.stage:
                    stages_set.add(job.stage)
            stages = sorted(stages_set) if stages_set else ["build", "test", "deploy"]
            pipeline = Pipeline(stages=stages)

        # Generate YAML
        try:
            generated_content = build_pipeline_yaml(pipeline, jobs)
        except Exception as e:
            print(f"Error generating YAML: {e}", file=sys.stderr)
            return 2

    # Perform comparison
    semantic = getattr(args, "semantic", False)
    diff_format = getattr(args, "format", "unified")

    if semantic:
        # Semantic comparison: parse YAML and compare structures
        try:
            original_data = yaml.safe_load(original_content)
            generated_data = yaml.safe_load(generated_content)

            if original_data == generated_data:
                print("Files are semantically identical (same structure)")
                return 0
            else:
                # Still show text diff even with semantic comparison
                print("Files are semantically different:")
                _show_diff(
                    original_content,
                    generated_content,
                    str(original_path),
                    "generated",
                    diff_format,
                )
                return 1
        except yaml.YAMLError as e:
            print(f"Error parsing YAML for semantic comparison: {e}", file=sys.stderr)
            return 2
    else:
        # Text-based comparison
        if original_content.strip() == generated_content.strip():
            print("Files are identical (byte-for-byte)")
            return 0
        else:
            _show_diff(
                original_content,
                generated_content,
                str(original_path),
                "generated",
                diff_format,
            )
            return 1


def _show_diff(
    original: str,
    generated: str,
    original_name: str,
    generated_name: str,
    format_type: str,
) -> None:
    """Show diff between two strings.

    Args:
        original: Original content.
        generated: Generated content.
        original_name: Name/path of original file.
        generated_name: Name/path of generated file.
        format_type: Diff format ('unified' or 'context').
    """
    original_lines = original.splitlines(keepends=True)
    generated_lines = generated.splitlines(keepends=True)

    if format_type == "context":
        diff = difflib.context_diff(
            original_lines,
            generated_lines,
            fromfile=original_name,
            tofile=generated_name,
        )
    else:  # unified (default)
        diff = difflib.unified_diff(
            original_lines,
            generated_lines,
            fromfile=original_name,
            tofile=generated_name,
        )

    # Print diff with color support
    for line in diff:
        if line.startswith("+") and not line.startswith("+++"):
            # Green for additions
            print(f"\033[32m{line}\033[0m", end="")
        elif line.startswith("-") and not line.startswith("---"):
            # Red for deletions
            print(f"\033[31m{line}\033[0m", end="")
        elif line.startswith("@@") or line.startswith("***"):
            # Cyan for markers
            print(f"\033[36m{line}\033[0m", end="")
        else:
            print(line, end="")
