"""Test command implementation."""

import argparse
import sys
import tempfile
from pathlib import Path


def run_test(args: argparse.Namespace) -> int:
    """Execute the test command.

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
            from wetwire_gitlab.kiro import run_kiro_scenario
        except ImportError:
            print(
                "Error: Kiro integration requires mcp package.\n"
                "Install with: pip install wetwire-gitlab[kiro]",
                file=sys.stderr,
            )
            return 1

        # For Kiro, we need a prompt from the user
        print("\033[1mTest prompt:\033[0m ", end="")
        test_prompt = input()

        if not test_prompt.strip():
            print("No prompt provided.", file=sys.stderr)
            return 1

        print(f"Running Kiro scenario: {test_prompt}")
        print()

        result = run_kiro_scenario(
            prompt=test_prompt,
            project_dir=output_dir,
            timeout=getattr(args, "timeout", 300),
        )

        # Print results
        print("\n--- Scenario Results ---")
        print(f"Success: {result['success']}")
        print(f"Exit code: {result['exit_code']}")
        print(f"Package: {result['package_path'] or 'None'}")
        print(f"Template valid: {result['template_valid']}")

        if result["stdout"]:
            print("\n--- Stdout ---")
            print(result["stdout"][:2000])

        if result["stderr"]:
            print("\n--- Stderr ---")
            print(result["stderr"][:1000])

        return 0 if result["success"] else 1

    # Use Anthropic API via wetwire-core (default)
    from wetwire_core.agent.personas import PERSONAS, load_persona
    from wetwire_core.agent.results import ResultsWriter, SessionResults
    from wetwire_core.agent.scoring import Rating, Score
    from wetwire_core.agents import AIConversationHandler, DeveloperAgent
    from wetwire_core.runner import Message

    from wetwire_gitlab.agent import GitLabRunnerAgent

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
