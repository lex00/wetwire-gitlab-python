"""Main CLI entry point for wetwire-gitlab."""

import argparse
import sys

from wetwire_gitlab.cli.commands import (
    run_build,
    run_design,
    run_diff,
    run_graph,
    run_import,
    run_init,
    run_lint,
    run_list,
    run_test,
    run_validate,
    run_version,
)


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
    build_parser.add_argument(
        "-w",
        "--watch",
        action="store_true",
        help="Watch for file changes and auto-rebuild (requires watchdog)",
    )
    build_parser.add_argument(
        "--schema-validate",
        action="store_true",
        help="Validate generated YAML against GitLab CI JSON schema (requires jsonschema)",
    )
    build_parser.add_argument(
        "--manifest",
        action="store_true",
        help="Generate manifest.json tracking build pipeline stages",
    )

    # diff command
    diff_parser = subparsers.add_parser(
        "diff", help="Compare generated YAML with existing .gitlab-ci.yml"
    )
    diff_parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to Python package (default: current directory)",
    )
    diff_parser.add_argument(
        "--original",
        help="Path to original .gitlab-ci.yml (default: .gitlab-ci.yml in path)",
    )
    diff_parser.add_argument(
        "-f",
        "--format",
        choices=["unified", "context"],
        default="unified",
        help="Diff format (default: unified)",
    )
    diff_parser.add_argument(
        "--semantic",
        action="store_true",
        help="Compare YAML structure semantically instead of text-based",
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
        required=True,
        help="Package name (snake_case, e.g., 'my_pipeline')",
    )
    init_parser.add_argument(
        "-d",
        "--description",
        help="Package description",
    )
    init_parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Overwrite existing package",
    )
    init_parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="List created files",
    )
    init_parser.add_argument(
        "--no-scaffold",
        action="store_true",
        help="Skip generating README.md, CLAUDE.md, .gitignore",
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
    design_parser.add_argument(
        "-p",
        "--provider",
        choices=["anthropic", "kiro"],
        default="anthropic",
        help="AI provider to use (default: anthropic)",
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
    test_parser.add_argument(
        "--all-personas",
        action="store_true",
        help="Run test with all available personas",
    )
    test_parser.add_argument(
        "--scenario",
        help="Predefined test scenario name (e.g., 'basic-pipeline', 'multi-stage')",
    )
    test_parser.add_argument(
        "-p",
        "--provider",
        choices=["anthropic", "kiro"],
        default="anthropic",
        help="AI provider to use (default: anthropic)",
    )
    test_parser.add_argument(
        "-t",
        "--timeout",
        type=int,
        default=300,
        help="Timeout in seconds for kiro provider (default: 300)",
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
    graph_parser.add_argument(
        "-p",
        "--params",
        action="store_true",
        help="Include pipeline variables as nodes",
    )
    graph_parser.add_argument(
        "-c",
        "--cluster",
        action="store_true",
        help="Group jobs by stage in subgraphs",
    )

    return parser


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

    # Dispatch to command handlers
    handlers = {
        "version": run_version,
        "build": run_build,
        "diff": run_diff,
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
