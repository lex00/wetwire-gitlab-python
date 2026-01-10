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
    from wetwire_gitlab.discover import discover_in_directory

    path = Path(args.path)

    if not path.exists():
        print(f"Error: Path does not exist: {path}", file=sys.stderr)
        return 1

    # Find source directory
    if path.is_file():
        scan_dir = path.parent
    else:
        src_dir = path / "src"
        if src_dir.exists():
            scan_dir = src_dir
        else:
            scan_dir = path

    # Discover jobs and pipelines
    result = discover_in_directory(scan_dir)

    if args.format == "json":
        import json

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
                deps = f" (needs: {', '.join(job.dependencies)})" if job.dependencies else ""
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
    from wetwire_gitlab.importer import generate_python_code, parse_gitlab_ci_file

    input_path = Path(args.path)

    if not input_path.exists():
        print(f"Error: File does not exist: {input_path}", file=sys.stderr)
        return 1

    # Parse the YAML file
    try:
        pipeline = parse_gitlab_ci_file(input_path)
    except Exception as e:
        print(f"Error parsing YAML: {e}", file=sys.stderr)
        return 1

    # Generate Python code
    code = generate_python_code(pipeline)

    # Determine output location
    output_dir = Path(args.output) if args.output else Path.cwd()

    if args.single_file:
        # Write to a single file
        output_file = output_dir / "pipeline.py"
        output_file.write_text(code)
        print(f"Generated {output_file}")
    else:
        # Create package structure
        if not args.no_scaffold:
            # Create src directory
            src_dir = output_dir / "src" / "pipeline"
            src_dir.mkdir(parents=True, exist_ok=True)

            # Create __init__.py
            (src_dir / "__init__.py").write_text('"""Pipeline package."""\n')

            # Create jobs.py
            (src_dir / "jobs.py").write_text(code)

            # Create pyproject.toml if scaffold is enabled
            pyproject_content = '''[project]
name = "pipeline"
version = "0.1.0"
dependencies = ["wetwire-gitlab"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
'''
            (output_dir / "pyproject.toml").write_text(pyproject_content)
            print(f"Generated pipeline package in {output_dir}")
        else:
            # Just create the jobs.py file
            output_dir.mkdir(parents=True, exist_ok=True)
            output_file = output_dir / "jobs.py"
            output_file.write_text(code)
            print(f"Generated {output_file}")

    return 0


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


def run_design(args: argparse.Namespace) -> int:
    """Execute the design command.

    Args:
        args: Parsed command-line arguments.

    Returns:
        Exit code (0=success, 1=error).
    """
    from wetwire_core.agents import InteractiveConversationHandler

    from wetwire_gitlab.agent import GitLabRunnerAgent, detect_existing_package

    path = Path(args.path)

    # Determine output directory
    if path.is_dir():
        output_dir = path
    else:
        output_dir = Path.cwd()

    # Check for existing package
    existing_package, existing_files = detect_existing_package(output_dir)

    if existing_package:
        print(f"\033[33mFound existing package: {existing_package}\033[0m")
        print(f"\033[90mFiles: {', '.join(existing_files) if existing_files else '(none)'}\033[0m")
        print()

    # Create a custom handler that uses GitLabRunnerAgent
    class GitLabInteractiveHandler(InteractiveConversationHandler):
        """Interactive handler using GitLab-specific runner."""

        def __init__(self, output_dir: Path, existing_package: str | None = None,
                     existing_files: list[str] | None = None, max_turns: int = 20):
            self.output_dir = output_dir
            self.existing_package = existing_package
            self.existing_files = existing_files or []
            self.max_turns = max_turns

        def run(self, initial_prompt: str):
            """Run interactive design session."""
            from wetwire_core.runner import Message

            runner = GitLabRunnerAgent(
                output_dir=self.output_dir,
                existing_package=self.existing_package,
            )
            messages: list[Message] = []

            lint_passed = False
            build_succeeded = False

            # Prefix prompt with context if existing package
            if self.existing_package:
                context = f"[EXISTING PACKAGE: {self.existing_package}]\n"
                context += f"[FILES: {', '.join(self.existing_files)}]\n\n"
                current_message = context + initial_prompt
            else:
                current_message = initial_prompt

            messages.append(Message(role="developer", content=initial_prompt))

            print("\n\033[1mRunner:\033[0m ", end="", flush=True)

            for _turn in range(self.max_turns):
                response_text, tool_results = runner.run_turn(current_message)

                # Display response
                if response_text:
                    print(response_text, flush=True)
                    messages.append(Message(role="runner", content=response_text))

                # Display tool results
                for result in tool_results:
                    if result.tool_name == "run_lint":
                        lint_passed = "passed" in result.content.lower() or "no issues" in result.content.lower()
                        status = "\033[32mPASS\033[0m" if lint_passed else "\033[31mFAIL\033[0m"
                        print(f"\033[90m[lint] {status}: {result.content}\033[0m", flush=True)
                    elif result.tool_name == "run_build":
                        build_succeeded = not result.is_error
                        status = "\033[32mOK\033[0m" if build_succeeded else "\033[31mFAIL\033[0m"
                        content = result.content[:300] + "..." if len(result.content) > 300 else result.content
                        print(f"\033[90m[build] {status}: {content}\033[0m", flush=True)
                    elif result.tool_name in ("init_package", "write_file"):
                        print(f"\033[90m[{result.tool_name}] {result.content}\033[0m", flush=True)
                    elif result.tool_name == "read_file":
                        content = result.content[:200] + "..." if len(result.content) > 200 else result.content
                        print(f"\033[90m[read_file] {content}\033[0m", flush=True)

                # Check for questions
                question = None
                for result in tool_results:
                    if result.content.startswith("QUESTION:"):
                        question = result.content[9:].strip()
                        break

                if question:
                    print(f"\n\n\033[1mRunner asks:\033[0m {question}")
                    print("\033[1mYour answer:\033[0m ", end="")
                    developer_response = input()

                    if developer_response.lower() in ("quit", "exit", "q"):
                        print("\n\033[33mSession ended.\033[0m")
                        break

                    messages.append(Message(role="developer", content=developer_response))
                    current_message = developer_response
                    print("\n\033[1mRunner:\033[0m ", end="", flush=True)
                else:
                    # Check if build succeeded
                    just_built = any(
                        getattr(r, 'tool_name', '') == 'run_build' and not r.is_error
                        for r in tool_results
                    )

                    if just_built and build_succeeded:
                        print("\n\n\033[1mWhat's next?\033[0m (type 'done' to exit): ", end="")
                        developer_response = input()

                        if developer_response.lower() in ("quit", "exit", "q", "done", ""):
                            print("\n\033[33mSession ended.\033[0m")
                            break

                        messages.append(Message(role="developer", content=developer_response))
                        current_message = developer_response
                        print("\n\033[1mRunner:\033[0m ", end="", flush=True)
                    elif tool_results:
                        current_message = None
                        print("\n\033[1mRunner:\033[0m ", end="", flush=True)
                    else:
                        print("\n\n\033[1mYour input:\033[0m ", end="")
                        developer_response = input()

                        if developer_response.lower() in ("quit", "exit", "q", "done", ""):
                            print("\n\033[33mSession ended.\033[0m")
                            break

                        messages.append(Message(role="developer", content=developer_response))
                        current_message = developer_response
                        print("\n\033[1mRunner:\033[0m ", end="", flush=True)

            package_path = None
            if runner.package_dir and build_succeeded:
                package_path = runner.package_dir

            return package_path, messages

    # Get initial prompt
    if existing_package:
        print("\033[1mWhat would you like to add or change?\033[0m")
    else:
        print("\033[1mDescribe what pipeline you need:\033[0m")
    print("\033[1mYour request:\033[0m ", end="")
    initial_prompt = input()

    if not initial_prompt.strip():
        print("No input provided.", file=sys.stderr)
        return 1

    handler = GitLabInteractiveHandler(
        output_dir=output_dir,
        existing_package=existing_package,
        existing_files=existing_files if existing_package else [],
    )

    package_path, messages = handler.run(initial_prompt)

    if package_path:
        print(f"\n\033[32mPackage created at: {package_path}\033[0m")
        return 0
    else:
        print("\n\033[33mNo package was created.\033[0m")
        return 1


def run_test(args: argparse.Namespace) -> int:
    """Execute the test command.

    Args:
        args: Parsed command-line arguments.

    Returns:
        Exit code (0=success, 1=error).
    """
    import tempfile

    from wetwire_core.agent.personas import PERSONAS, load_persona
    from wetwire_core.agent.results import ResultsWriter, SessionResults
    from wetwire_core.agent.scoring import Rating, Score
    from wetwire_core.agents import AIConversationHandler, DeveloperAgent
    from wetwire_core.runner import Message

    from wetwire_gitlab.agent import GitLabRunnerAgent

    path = Path(args.path)

    # Determine output directory
    if path.is_dir():
        output_dir = path
    else:
        output_dir = Path.cwd()

    # Get persona
    persona_name = args.persona
    if not persona_name:
        print("Available personas: " + ", ".join(PERSONAS.keys()))
        print("Select persona (default: intermediate): ", end="")
        persona_name = input().strip() or "intermediate"

    try:
        persona = load_persona(persona_name)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    print(f"\n\033[1mRunning test with persona: {persona.name}\033[0m")
    print(f"\033[90m{persona.description}\033[0m\n")

    # Get test prompt
    print("\033[1mTest prompt:\033[0m ", end="")
    test_prompt = input()

    if not test_prompt.strip():
        print("No prompt provided.", file=sys.stderr)
        return 1

    # Create temporary directory for output
    with tempfile.TemporaryDirectory(prefix="wetwire-test-") as tmp_dir:
        tmp_path = Path(tmp_dir)

        # Create custom AI conversation handler for GitLab
        class GitLabAIHandler(AIConversationHandler):
            """AI conversation handler using GitLab runner."""

            def __init__(self, prompt: str, persona_name: str, persona_instructions: str,
                         output_dir: Path, max_turns: int = 10):
                self.prompt = prompt
                self.persona_name = persona_name
                self.persona_instructions = persona_instructions
                self.output_dir = output_dir
                self.max_turns = max_turns
                self.messages: list[Message] = []

            def run(self):
                """Run AI conversation."""
                developer = DeveloperAgent(
                    persona_name=self.persona_name,
                    persona_instructions=self.persona_instructions,
                )
                runner = GitLabRunnerAgent(output_dir=self.output_dir)

                self.messages.append(Message(role="developer", content=self.prompt))
                current_message = self.prompt

                lint_called = False
                lint_passed = False
                pending_lint = False

                for turn in range(self.max_turns):
                    print(f"\033[90m[Turn {turn + 1}]\033[0m")
                    response_text, tool_results = runner.run_turn(current_message)

                    wrote_file_this_turn = False
                    ran_lint_this_turn = False

                    for result in tool_results:
                        print(f"\033[90m  [{result.tool_name}]\033[0m")
                        if result.tool_name == "run_lint":
                            lint_called = True
                            ran_lint_this_turn = True
                            pending_lint = False
                            lint_passed = "passed" in result.content.lower() or "no issues" in result.content.lower()
                        elif result.tool_name == "write_file":
                            wrote_file_this_turn = True
                            pending_lint = True
                            lint_passed = False

                    # Enforcement: require lint after write
                    if wrote_file_this_turn and not ran_lint_this_turn:
                        current_message = (
                            "STOP: You wrote a file but did not call run_lint. "
                            "Call run_lint now."
                        )
                        self.messages.append(Message(role="system", content=current_message))
                        continue

                    # Check for questions
                    question = None
                    for result in tool_results:
                        if result.content.startswith("QUESTION:"):
                            question = result.content[9:].strip()
                            break

                    if question:
                        self.messages.append(Message(role="runner", content=question))
                        developer_response = developer.respond(question)
                        self.messages.append(Message(role="developer", content=developer_response))

                        if "DONE" in developer_response.upper():
                            break

                        current_message = developer_response
                    else:
                        if response_text:
                            self.messages.append(Message(role="runner", content=response_text))

                        if "completed" in response_text.lower() or "done" in response_text.lower():
                            if not lint_called or pending_lint:
                                current_message = "ERROR: Must call run_lint before done."
                                self.messages.append(Message(role="system", content=current_message))
                                continue
                            elif not lint_passed:
                                current_message = "ERROR: Lint did not pass."
                                self.messages.append(Message(role="system", content=current_message))
                                continue
                            break

                        current_message = None

                    if turn > 5 and not runner.package_name:
                        self.messages.append(
                            Message(role="system", content="Warning: No package after multiple turns")
                        )
                        break

                package_path = None
                if runner.package_name and lint_called and lint_passed:
                    package_path = self.output_dir / runner.package_name

                return package_path, self.messages

        handler = GitLabAIHandler(
            prompt=test_prompt,
            persona_name=persona.name,
            persona_instructions=persona.system_prompt,
            output_dir=tmp_path,
        )

        print("\n\033[1mStarting AI conversation...\033[0m\n")
        package_path, messages = handler.run()

        # Calculate score
        produced_package = package_path is not None
        questions = [m for m in messages if m.role == "runner" and "?" in m.content]

        score = Score(
            completeness=Rating.EXCELLENT if produced_package else Rating.NONE,
            lint_quality=Rating.EXCELLENT if produced_package else Rating.NONE,
            code_quality=Rating.GOOD if produced_package else Rating.NONE,
            output_validity=Rating.GOOD if produced_package else Rating.NONE,
            question_efficiency=Rating.EXCELLENT if len(questions) <= 2 else Rating.GOOD,
        )

        # Write results
        results = SessionResults(
            prompt=test_prompt,
            package_name=package_path.name if package_path else "none",
            domain="gitlab",
            persona=persona.name,
            summary=f"Test with {persona.name} persona",
            score=score,
        )

        results_path = output_dir / "RESULTS.md"
        writer = ResultsWriter()
        writer.write(results, results_path)

        # Display results
        print("\n" + "=" * 60)
        print("\033[1mTest Results\033[0m")
        print("=" * 60)
        print(f"Persona: {persona.name}")
        print(f"Package created: {'Yes' if produced_package else 'No'}")
        print(f"Score: {score.total}/15 ({score.grade})")
        print(f"Results written to: {results_path}")

        return 0 if score.passed else 1


def run_graph(args: argparse.Namespace) -> int:
    """Execute the graph command.

    Args:
        args: Parsed command-line arguments.

    Returns:
        Exit code (0=success, 1=error).
    """
    from wetwire_gitlab.discover import discover_in_directory

    path = Path(args.path)

    if not path.exists():
        print(f"Error: Path does not exist: {path}", file=sys.stderr)
        return 1

    # Find source directory
    if path.is_file():
        scan_dir = path.parent
    else:
        src_dir = path / "src"
        if src_dir.exists():
            scan_dir = src_dir
        else:
            scan_dir = path

    # Discover jobs
    result = discover_in_directory(scan_dir)

    if not result.jobs:
        print("No jobs found.", file=sys.stderr)
        return 1

    # Build dependency graph
    graph_lines = []
    include_params = getattr(args, "params", False)
    use_clusters = getattr(args, "cluster", False)

    if args.format == "dot":
        graph_lines.extend(
            _generate_dot_graph(result.jobs, include_params, use_clusters)
        )
    else:
        # Mermaid format (default)
        graph_lines.extend(
            _generate_mermaid_graph(result.jobs, include_params, use_clusters)
        )

    output = "\n".join(graph_lines)

    if args.output:
        output_path = Path(args.output)
        output_path.write_text(output)
        print(f"Generated {output_path}")
    else:
        print(output)

    return 0


def _generate_mermaid_graph(
    jobs: list, include_params: bool = False, use_clusters: bool = False
) -> list[str]:
    """Generate Mermaid graph output.

    Args:
        jobs: List of DiscoveredJob objects.
        include_params: Whether to include variable nodes.
        use_clusters: Whether to group jobs by stage.

    Returns:
        List of graph lines.
    """
    lines = ["graph LR"]

    if use_clusters:
        # Group jobs by stage
        stages: dict[str, list] = {}
        for job in jobs:
            stage = job.stage or "default"
            if stage not in stages:
                stages[stage] = []
            stages[stage].append(job)

        # Generate subgraphs for each stage
        for stage, stage_jobs in stages.items():
            lines.append(f"  subgraph {stage}")
            for job in stage_jobs:
                node_label = _mermaid_node_label(job)
                lines.append(f"    {job.name}{node_label}")
            lines.append("  end")
    else:
        # Flat graph
        for job in jobs:
            node_label = _mermaid_node_label(job)
            lines.append(f"  {job.name}{node_label}")

    # Add edges for dependencies
    for job in jobs:
        if job.dependencies:
            for dep in job.dependencies:
                lines.append(f"  {dep} --> {job.name}")

    # Add variable nodes if requested
    if include_params:
        all_vars: set[str] = set()
        for job in jobs:
            if job.variables:
                for var_name in job.variables:
                    all_vars.add(var_name)
                    lines.append(f"  {var_name}([{var_name}]) -.-> {job.name}")

    return lines


def _mermaid_node_label(job) -> str:
    """Generate Mermaid node label with annotations.

    Args:
        job: DiscoveredJob object.

    Returns:
        Node label string (empty or with brackets for custom label).
    """
    if job.when:
        return f"[{job.name}<br/>{job.when}]"
    return ""


def _generate_dot_graph(
    jobs: list, include_params: bool = False, use_clusters: bool = False
) -> list[str]:
    """Generate DOT graph output.

    Args:
        jobs: List of DiscoveredJob objects.
        include_params: Whether to include variable nodes.
        use_clusters: Whether to group jobs by stage.

    Returns:
        List of graph lines.
    """
    lines = ["digraph pipeline {", "  rankdir=LR;", "  node [shape=box];"]

    if use_clusters:
        # Group jobs by stage
        stages: dict[str, list] = {}
        for job in jobs:
            stage = job.stage or "default"
            if stage not in stages:
                stages[stage] = []
            stages[stage].append(job)

        # Generate subgraphs for each stage
        for idx, (stage, stage_jobs) in enumerate(stages.items()):
            lines.append(f"  subgraph cluster_{idx} {{")
            lines.append(f'    label="{stage}";')
            for job in stage_jobs:
                node_label = _dot_node_label(job)
                lines.append(f'    "{job.name}"{node_label};')
            lines.append("  }")
    else:
        # Flat graph
        for job in jobs:
            node_label = _dot_node_label(job)
            lines.append(f'  "{job.name}"{node_label};')

    # Add edges for dependencies
    for job in jobs:
        if job.dependencies:
            for dep in job.dependencies:
                lines.append(f'  "{dep}" -> "{job.name}";')

    # Add variable nodes if requested
    if include_params:
        lines.append("  node [shape=ellipse, style=dashed];")
        for job in jobs:
            if job.variables:
                for var_name in job.variables:
                    lines.append(f'  "{var_name}";')
                    lines.append(
                        f'  "{var_name}" -> "{job.name}" [style=dashed];'
                    )

    lines.append("}")
    return lines


def _dot_node_label(job) -> str:
    """Generate DOT node label with annotations.

    Args:
        job: DiscoveredJob object.

    Returns:
        Node label string for DOT format.
    """
    if job.when:
        return f' [label="{job.name}\\n({job.when})"]'
    return ""


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
