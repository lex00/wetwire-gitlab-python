"""Build command implementation."""

import argparse
import hashlib
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from wetwire_gitlab.contracts import BuildManifest, DiscoveredJob


def _compute_file_hash(file_path: Path) -> str:
    """Compute SHA256 hash of a file's contents.

    Args:
        file_path: Path to the file to hash.

    Returns:
        Hex-encoded SHA256 hash string.
    """
    if not file_path.exists():
        return ""
    content = file_path.read_bytes()
    return hashlib.sha256(content).hexdigest()


def create_manifest(
    jobs: list["DiscoveredJob"],
    output_file: str,
    source_directory: Path,
) -> "BuildManifest":
    """Create a build manifest from discovered jobs.

    Args:
        jobs: List of discovered jobs from AST analysis.
        output_file: Path to the generated output file.
        source_directory: Root directory of source files.

    Returns:
        BuildManifest instance with all pipeline tracking information.
    """
    from wetwire_gitlab import __version__
    from wetwire_gitlab.contracts import BuildManifest

    # Collect unique source files and compute hashes
    source_files_set: set[str] = set()
    for job in jobs:
        source_files_set.add(job.file_path)

    source_files = []
    for file_path_str in sorted(source_files_set):
        file_path = Path(file_path_str)
        file_hash = _compute_file_hash(file_path)
        # Use relative path if possible
        try:
            rel_path = file_path.relative_to(source_directory)
            path_str = str(rel_path)
        except ValueError:
            path_str = file_path_str
        source_files.append({"path": path_str, "hash": file_hash})

    # Build discovered jobs list
    discovered_jobs = []
    for job in jobs:
        job_info: dict = {
            "name": job.name,
            "file": job.file_path,
            "line": job.line_number,
        }
        if job.stage:
            job_info["stage"] = job.stage
        discovered_jobs.append(job_info)

    # Build dependencies map
    dependencies: dict[str, list[str]] = {}
    for job in jobs:
        if job.dependencies:
            dependencies[job.name] = list(job.dependencies)

    # Generate ISO timestamp
    generated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    return BuildManifest(
        version=__version__,
        generated_at=generated_at,
        source_files=source_files,
        discovered_jobs=discovered_jobs,
        dependencies=dependencies,
        output_file=output_file,
    )


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

    # Generate manifest if requested
    if hasattr(args, "manifest") and args.manifest:
        from wetwire_gitlab.discover import discover_in_directory

        # Discover jobs to get metadata for manifest
        list_result = discover_in_directory(scan_dir)
        discovered_jobs = list_result.jobs

        # Determine output file path for manifest
        output_file_path = args.output if args.output else ".gitlab-ci.yml"

        # Create manifest
        manifest = create_manifest(
            jobs=discovered_jobs,
            output_file=output_file_path,
            source_directory=scan_dir,
        )

        # Determine manifest output location
        if args.output:
            manifest_path = Path(args.output).parent / "manifest.json"
        else:
            manifest_path = path / "manifest.json"

        manifest_path.write_text(manifest.to_json())
        if not silent:
            print(f"Generated {manifest_path}")

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
