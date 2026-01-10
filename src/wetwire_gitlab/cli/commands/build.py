"""Build command implementation."""

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path


def _do_build(args: argparse.Namespace, silent: bool = False) -> int:
    """Perform a single build operation.

    Args:
        args: Parsed command-line arguments.
        silent: If True, suppress normal output messages.

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
        if not silent:
            print(f"Generated {output_path}")
    else:
        print(output)

    # Schema validation if requested
    if hasattr(args, "schema_validate") and args.schema_validate:
        if args.format == "yaml":
            from wetwire_gitlab.validation.schema import validate_yaml

            if not silent:
                print("Validating against GitLab CI schema...")

            validation_result = validate_yaml(output)

            if not validation_result.valid:
                print("Schema validation failed:", file=sys.stderr)
                if validation_result.errors:
                    for error in validation_result.errors:
                        print(f"  - {error}", file=sys.stderr)
                return 1

            if not silent:
                print("Schema validation passed")
        else:
            print(
                "Warning: Schema validation is only supported for YAML format",
                file=sys.stderr,
            )

    # Create build result for tracking
    result = BuildResult(
        success=True,
        output_path=args.output,
        jobs_count=len(jobs),
    )

    return 0 if result.success else 1


def run_build(args: argparse.Namespace) -> int:
    """Execute the build command.

    Args:
        args: Parsed command-line arguments.

    Returns:
        Exit code (0=success, 1=error).
    """
    # Check if watch mode is enabled
    if hasattr(args, "watch") and args.watch:
        return _run_watch_mode(args)

    # Regular single build
    return _do_build(args)


def _run_watch_mode(args: argparse.Namespace) -> int:
    """Run build in watch mode with file monitoring.

    Args:
        args: Parsed command-line arguments.

    Returns:
        Exit code (0=success, 1=error).
    """
    try:
        from watchdog.events import FileSystemEventHandler
        from watchdog.observers import Observer
    except ImportError:
        print(
            "Error: watchdog package is required for watch mode.",
            file=sys.stderr,
        )
        print("Install with: pip install 'wetwire-gitlab[watch]'", file=sys.stderr)
        return 1

    path = Path(args.path)
    if not path.exists():
        print(f"Error: Path does not exist: {path}", file=sys.stderr)
        return 1

    # Determine watch directory
    if path.is_file():
        watch_dir = path.parent
    else:
        # Look for src directory
        src_dir = path / "src"
        if src_dir.exists():
            watch_dir = src_dir
        else:
            watch_dir = path

    print(f"Watching for changes in: {watch_dir}")
    print("Press Ctrl+C to stop")
    print("=" * 60)

    # Perform initial build
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"\n[{timestamp}] Initial build...")
    try:
        _do_build(args, silent=False)
    except Exception as e:
        print(f"Error during build: {e}", file=sys.stderr)

    # Create event handler with debouncing
    class BuildEventHandler(FileSystemEventHandler):
        """File system event handler for rebuilding on changes."""

        def __init__(self):
            super().__init__()
            self.last_modified = 0
            self.debounce_seconds = 0.5

        def on_modified(self, event):
            """Handle file modification events."""
            if event.is_directory:
                return

            # Only watch .py files
            if not event.src_path.endswith(".py"):
                return

            # Debounce rapid changes
            current_time = time.time()
            if current_time - self.last_modified < self.debounce_seconds:
                return

            self.last_modified = current_time

            # Trigger rebuild
            self._rebuild()

        def on_created(self, event):
            """Handle file creation events."""
            if event.is_directory:
                return

            if not event.src_path.endswith(".py"):
                return

            current_time = time.time()
            if current_time - self.last_modified < self.debounce_seconds:
                return

            self.last_modified = current_time
            self._rebuild()

        def _rebuild(self):
            """Perform rebuild with error handling."""
            print("\n" + "=" * 60)
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] Rebuilding...")

            try:
                result = _do_build(args, silent=False)
                if result == 0:
                    print(f"[{timestamp}] Build successful")
                else:
                    print(f"[{timestamp}] Build failed", file=sys.stderr)
            except Exception as e:
                print(f"[{timestamp}] Error during rebuild: {e}", file=sys.stderr)
            finally:
                print("=" * 60)

    # Setup file observer
    event_handler = BuildEventHandler()
    observer = Observer()
    observer.schedule(event_handler, str(watch_dir), recursive=True)
    observer.start()

    try:
        # Keep running until interrupted
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nStopping watch mode...")
        observer.stop()
        observer.join()
        return 0

    return 0
