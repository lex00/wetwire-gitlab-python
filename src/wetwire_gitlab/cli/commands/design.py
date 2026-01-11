"""Design command implementation."""

import argparse
import sys
from pathlib import Path


def run_design(args: argparse.Namespace) -> int:
    """Execute the design command.

    Args:
        args: Parsed command-line arguments.

    Returns:
        Exit code (0=success, 1=error).
    """
    path = Path(args.path)
    provider = getattr(args, "provider", "anthropic")

    # Determine output directory
    if path.is_dir():
        output_dir = path
    else:
        output_dir = Path.cwd()

    if provider == "kiro":
        # Use Kiro CLI provider
        try:
            from wetwire_gitlab.kiro import GITLAB_KIRO_CONFIG, launch_kiro
        except ImportError:
            print(
                "Error: Kiro integration requires mcp package.\n"
                "Install with: pip install wetwire-gitlab[kiro]",
                file=sys.stderr,
            )
            return 1

        result = launch_kiro(
            GITLAB_KIRO_CONFIG,
            prompt="Hello! I'm ready to design GitLab CI/CD pipelines.",
            project_dir=output_dir,
        )
        return result.returncode

    # Use Anthropic API via wetwire-core (default)
    try:
        from wetwire_core.agents import InteractiveConversationHandler
    except ImportError:
        print(
            "Error: Design command with anthropic provider requires wetwire-core package.\n"
            "Install with: pip install wetwire-gitlab[agent]",
            file=sys.stderr,
        )
        return 1

    from wetwire_gitlab.agent import GitLabRunnerAgent, detect_existing_package

    # Check for existing package
    existing_package, existing_files = detect_existing_package(output_dir)

    if existing_package:
        print(f"\033[33mFound existing package: {existing_package}\033[0m")
        print(
            f"\033[90mFiles: {', '.join(existing_files) if existing_files else '(none)'}\033[0m"
        )
        print()

    # Create a custom handler that uses GitLabRunnerAgent
    class GitLabInteractiveHandler(InteractiveConversationHandler):
        """Interactive handler using GitLab-specific runner."""

        def __init__(
            self,
            output_dir: Path,
            existing_package: str | None = None,
            existing_files: list[str] | None = None,
            max_turns: int = 20,
        ):
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
                        lint_passed = (
                            "passed" in result.content.lower()
                            or "no issues" in result.content.lower()
                        )
                        status = (
                            "\033[32mPASS\033[0m"
                            if lint_passed
                            else "\033[31mFAIL\033[0m"
                        )
                        print(
                            f"\033[90m[lint] {status}: {result.content}\033[0m",
                            flush=True,
                        )
                    elif result.tool_name == "run_build":
                        build_succeeded = not result.is_error
                        status = (
                            "\033[32mOK\033[0m"
                            if build_succeeded
                            else "\033[31mFAIL\033[0m"
                        )
                        content = (
                            result.content[:300] + "..."
                            if len(result.content) > 300
                            else result.content
                        )
                        print(f"\033[90m[build] {status}: {content}\033[0m", flush=True)
                    elif result.tool_name in ("init_package", "write_file"):
                        print(
                            f"\033[90m[{result.tool_name}] {result.content}\033[0m",
                            flush=True,
                        )
                    elif result.tool_name == "read_file":
                        content = (
                            result.content[:200] + "..."
                            if len(result.content) > 200
                            else result.content
                        )
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

                    messages.append(
                        Message(role="developer", content=developer_response)
                    )
                    current_message = developer_response
                    print("\n\033[1mRunner:\033[0m ", end="", flush=True)
                else:
                    # Check if build succeeded
                    just_built = any(
                        getattr(r, "tool_name", "") == "run_build" and not r.is_error
                        for r in tool_results
                    )

                    if just_built and build_succeeded:
                        print(
                            "\n\n\033[1mWhat's next?\033[0m (type 'done' to exit): ",
                            end="",
                        )
                        developer_response = input()

                        if developer_response.lower() in (
                            "quit",
                            "exit",
                            "q",
                            "done",
                            "",
                        ):
                            print("\n\033[33mSession ended.\033[0m")
                            break

                        messages.append(
                            Message(role="developer", content=developer_response)
                        )
                        current_message = developer_response
                        print("\n\033[1mRunner:\033[0m ", end="", flush=True)
                    elif tool_results:
                        current_message = None
                        print("\n\033[1mRunner:\033[0m ", end="", flush=True)
                    else:
                        print("\n\n\033[1mYour input:\033[0m ", end="")
                        developer_response = input()

                        if developer_response.lower() in (
                            "quit",
                            "exit",
                            "q",
                            "done",
                            "",
                        ):
                            print("\n\033[33mSession ended.\033[0m")
                            break

                        messages.append(
                            Message(role="developer", content=developer_response)
                        )
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
