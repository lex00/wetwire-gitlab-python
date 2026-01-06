"""Main CLI entry point for wetwire-gitlab."""

import argparse
import json
import sys
from pathlib import Path

from wetwire_gitlab import __version__


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser with all subcommands.

    Returns:
        Configured ArgumentParser instance.
    """
    parser = argparse.ArgumentParser(
        prog="wetwire-gitlab",
        description="Generate GitLab CI/CD configuration from typed Python declarations.",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # version command
    subparsers.add_parser("version", help="Show version information")

    # build command
    build_parser = subparsers.add_parser(
        "build", help="Build .gitlab-ci.yml from Python declarations"
    )
    build_parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to Python package (default: current directory)",
    )
    build_parser.add_argument(
        "-t",
        "--type",
        choices=["pipeline", "runner"],
        default="pipeline",
        help="Output type: pipeline (.gitlab-ci.yml) or runner (config.toml)",
    )
    build_parser.add_argument(
        "-o",
        "--output",
        help="Output file path (default: .gitlab-ci.yml or config.toml)",
    )
    build_parser.add_argument(
        "-f",
        "--format",
        choices=["yaml", "json"],
        default="yaml",
        help="Output format (default: yaml)",
    )

    # validate command
    validate_parser = subparsers.add_parser(
        "validate", help="Validate pipeline using glab ci lint"
    )
    validate_parser.add_argument(
        "path",
        nargs="?",
        default=".gitlab-ci.yml",
        help="Path to .gitlab-ci.yml (default: .gitlab-ci.yml)",
    )
    validate_parser.add_argument(
        "--include-jobs",
        action="store_true",
        help="Include job details in validation output",
    )

    # list command
    list_parser = subparsers.add_parser(
        "list", help="List discovered pipelines and jobs"
    )
    list_parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to Python package (default: current directory)",
    )
    list_parser.add_argument(
        "-f",
        "--format",
        choices=["table", "json"],
        default="table",
        help="Output format (default: table)",
    )

    # lint command
    lint_parser = subparsers.add_parser(
        "lint", help="Run Python code quality rules on pipeline definitions"
    )
    lint_parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to Python package (default: current directory)",
    )
    lint_parser.add_argument(
        "--fix",
        action="store_true",
        help="Automatically fix issues where possible",
    )
    lint_parser.add_argument(
        "-f",
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )

    # import command
    import_parser = subparsers.add_parser(
        "import", help="Convert .gitlab-ci.yml to Python code"
    )
    import_parser.add_argument(
        "path",
        help="Path to .gitlab-ci.yml to import",
    )
    import_parser.add_argument(
        "-o",
        "--output",
        help="Output directory (default: current directory)",
    )
    import_parser.add_argument(
        "--single-file",
        action="store_true",
        help="Generate a single Python file instead of package structure",
    )
    import_parser.add_argument(
        "--no-scaffold",
        action="store_true",
        help="Skip generating pyproject.toml and package structure",
    )

    # init command
    init_parser = subparsers.add_parser(
        "init", help="Create a new pipeline project with example"
    )
    init_parser.add_argument(
        "-o",
        "--output",
        default=".",
        help="Output directory (default: current directory)",
    )
    init_parser.add_argument(
        "--name",
        help="Project name (default: directory name)",
    )

    # design command
    design_parser = subparsers.add_parser(
        "design", help="AI-assisted pipeline design via wetwire-core"
    )
    design_parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to Python package (default: current directory)",
    )
    design_parser.add_argument(
        "--stream",
        action="store_true",
        help="Stream output in real-time",
    )
    design_parser.add_argument(
        "--max-lint-cycles",
        type=int,
        default=3,
        help="Maximum lint/fix cycles (default: 3)",
    )

    # test command
    test_parser = subparsers.add_parser(
        "test", help="Run persona-based evaluation via wetwire-core"
    )
    test_parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to Python package (default: current directory)",
    )
    test_parser.add_argument(
        "--persona",
        help="Persona name for testing",
    )

    # graph command
    graph_parser = subparsers.add_parser(
        "graph", help="Generate DAG visualization of pipeline jobs"
    )
    graph_parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to Python package (default: current directory)",
    )
    graph_parser.add_argument(
        "-f",
        "--format",
        choices=["dot", "mermaid"],
        default="mermaid",
        help="Output format (default: mermaid)",
    )
    graph_parser.add_argument(
        "-o",
        "--output",
        help="Output file path",
    )

    return parser


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


def run_list(args: argparse.Namespace) -> int:
    """Execute the list command.

    Args:
        args: Parsed command-line arguments.

    Returns:
        Exit code (0=success, 1=error).
    """
    print(f"List command not yet implemented. Path: {args.path}")
    return 1


def run_lint(args: argparse.Namespace) -> int:
    """Execute the lint command.

    Args:
        args: Parsed command-line arguments.

    Returns:
        Exit code (0=no issues, 1=issues found, 2=error).
    """
    from wetwire_gitlab.linter import lint_directory, lint_file

    path = Path(args.path)

    if not path.exists():
        print(f"Error: Path does not exist: {path}", file=sys.stderr)
        return 2

    # Lint the path
    if path.is_file():
        result = lint_file(path)
    else:
        result = lint_directory(path)

    # Output results
    if args.format == "json":
        import json

        output = {
            "success": result.success,
            "files_checked": result.files_checked,
            "issues": [
                {
                    "code": issue.code,
                    "message": issue.message,
                    "file": issue.file_path,
                    "line": issue.line_number,
                }
                for issue in result.issues
            ],
        }
        print(json.dumps(output, indent=2))
    else:
        if result.issues:
            for issue in result.issues:
                print(f"{issue.file_path}:{issue.line_number}: {issue.code} {issue.message}")
            print(f"\nFound {len(result.issues)} issue(s) in {result.files_checked} file(s)")
        else:
            print(f"No issues found in {result.files_checked} file(s)")

    return 0 if result.success else 1


def run_import(args: argparse.Namespace) -> int:
    """Execute the import command.

    Args:
        args: Parsed command-line arguments.

    Returns:
        Exit code (0=success, 1=error).
    """
    print(f"Import command not yet implemented. Path: {args.path}")
    return 1


def run_init(args: argparse.Namespace) -> int:
    """Execute the init command.

    Args:
        args: Parsed command-line arguments.

    Returns:
        Exit code (0=success, 1=error).
    """
    print(f"Init command not yet implemented. Output: {args.output}")
    return 1


def run_design(args: argparse.Namespace) -> int:
    """Execute the design command.

    Args:
        args: Parsed command-line arguments.

    Returns:
        Exit code (0=success, 1=error).
    """
    print(f"Design command not yet implemented. Path: {args.path}")
    return 1


def run_test(args: argparse.Namespace) -> int:
    """Execute the test command.

    Args:
        args: Parsed command-line arguments.

    Returns:
        Exit code (0=success, 1=error).
    """
    print(f"Test command not yet implemented. Path: {args.path}")
    return 1


def run_graph(args: argparse.Namespace) -> int:
    """Execute the graph command.

    Args:
        args: Parsed command-line arguments.

    Returns:
        Exit code (0=success, 1=error).
    """
    print(f"Graph command not yet implemented. Path: {args.path}")
    return 1


def main(argv: list[str] | None = None) -> int:
    """Main entry point for the CLI.

    Args:
        argv: Command-line arguments (default: sys.argv[1:]).

    Returns:
        Exit code.
    """
    parser = create_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 0

    if args.command == "version":
        print(f"wetwire-gitlab {__version__}")
        return 0

    # Dispatch to command handlers
    handlers = {
        "build": run_build,
        "validate": run_validate,
        "list": run_list,
        "lint": run_lint,
        "import": run_import,
        "init": run_init,
        "design": run_design,
        "test": run_test,
        "graph": run_graph,
    }

    handler = handlers.get(args.command)
    if handler:
        return handler(args)

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
