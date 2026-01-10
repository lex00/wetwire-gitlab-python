"""Build command implementation."""

import argparse
import json
import sys
from pathlib import Path


def run_build(args: argparse.Namespace) -> int:
    """Execute the build command.

    Args:
        args: Parsed command-line arguments.

    Returns:
        Exit code (0=success, 1=error).
    """
    from wetwire_gitlab.contracts import BuildResult
    from wetwire_gitlab.pipeline import Pipeline
    from wetwire_gitlab.runner import extract_all_jobs, extract_all_pipelines
    from wetwire_gitlab.serialize import build_pipeline_yaml, to_dict

    path = Path(args.path)

    if not path.exists():
        print(f"Error: Path does not exist: {path}", file=sys.stderr)
        return 1

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
    jobs = extract_all_jobs(scan_dir)
    pipelines = extract_all_pipelines(scan_dir)

    if not jobs:
        print("No jobs found.", file=sys.stderr)
        return 1

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

    # Generate output
    if args.format == "json":
        output_dict: dict = {"stages": pipeline.stages}
        for job in jobs:
            output_dict[job.name] = to_dict(job)
        output = json.dumps(output_dict, indent=2)
    else:
        output = build_pipeline_yaml(pipeline, jobs)

    # Write output
    if args.output:
        output_path = Path(args.output)
        output_path.write_text(output)
        print(f"Generated {output_path}")
    else:
        print(output)

    # Create build result for tracking
    result = BuildResult(
        success=True,
        output_path=args.output,
        jobs_count=len(jobs),
    )

    return 0 if result.success else 1
