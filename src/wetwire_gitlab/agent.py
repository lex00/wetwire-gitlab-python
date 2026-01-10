"""GitLab-specific AI agent for pipeline design.

This module provides:
- GitLabRunnerAgent: AI agent with access to wetwire-gitlab CLI tools
- ToolResult: Result of tool execution
- detect_existing_package: Detect existing wetwire-gitlab packages
"""

from __future__ import annotations

import os
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import anthropic

# GitLab-specific system prompt
RUNNER_SYSTEM_PROMPT = """You are a Runner agent that creates GitLab CI/CD pipelines using wetwire-gitlab.

Your job: Take the user's pipeline request and GENERATE THE CODE for it.

## NEW PACKAGE WORKFLOW

When starting fresh:
1. init_package - Create the package with a descriptive name
2. write_file - Write the COMPLETE pipeline code to jobs.py
3. run_lint - Check for issues (call immediately after write_file)
4. If lint fails: fix and write_file + run_lint again
5. run_build - Generate .gitlab-ci.yml
6. Tell user what you created

IMPORTANT: After init_package, you MUST immediately write_file with the actual pipeline code.

## EXISTING PACKAGE WORKFLOW

When the message starts with [EXISTING PACKAGE: name]:
1. read_file - Read existing files to understand current state
2. write_file - Add or modify jobs as requested
3. run_lint - Check for issues (call immediately after write_file)
4. If lint fails: fix and write_file + run_lint again
5. run_build - Generate .gitlab-ci.yml
6. Tell user what you changed

Do NOT call init_package for existing packages - just read and write files directly.

## FILE ORGANIZATION

Split pipeline into logical files:
- jobs.py - Job definitions
- stages.py - Stage constants
- pipeline.py - Pipeline configuration

## TOOL RULES

- After EVERY write_file, call run_lint in the SAME response
- NEVER say "completed" without lint passing first
- When you see STOP/ERROR, call run_lint immediately

## CODE PATTERNS

Use typed dataclasses from wetwire_gitlab:

```python
from wetwire_gitlab.pipeline import Job, Pipeline, Artifacts, Cache, Rule
from wetwire_gitlab.intrinsics import CI, When, Rules

# Define stages
pipeline = Pipeline(stages=["build", "test", "deploy"])

# Define jobs with typed dataclasses
build = Job(
    name="build",
    stage="build",
    script=["make build"],
    artifacts=Artifacts(paths=["build/"]),
)

test = Job(
    name="test",
    stage="test",
    script=["make test"],
    needs=["build"],
)

deploy = Job(
    name="deploy",
    stage="deploy",
    script=["make deploy"],
    rules=[Rules.ON_DEFAULT_BRANCH],
    needs=["test"],
)
```

## INTRINSICS

Use typed variables:
- CI.COMMIT_SHA for $CI_COMMIT_SHA
- CI.DEFAULT_BRANCH for $CI_DEFAULT_BRANCH
- Rules.ON_DEFAULT_BRANCH for default branch deployment
- Rules.ON_MERGE_REQUEST for MR pipelines
- When.MANUAL for manual jobs

## RULES

- Keep responses brief
- Use typed dataclasses, not raw dicts
- NEVER say "completed" without lint passing first
- When you see STOP/ERROR, call run_lint immediately
"""


@dataclass
class ToolResult:
    """Result of a tool execution."""

    tool_use_id: str
    content: str
    is_error: bool = False
    tool_name: str = ""


@dataclass
class GitLabRunnerAgent:
    """AI agent that creates GitLab CI/CD pipelines using wetwire-gitlab tools."""

    output_dir: Path
    existing_package: str | None = None
    client: anthropic.Anthropic = field(default_factory=anthropic.Anthropic)
    model: str = "claude-sonnet-4-20250514"
    conversation: list[dict[str, Any]] = field(default_factory=list)
    package_name: str = ""
    _package_dir: Path | None = field(default=None, init=False)

    def __post_init__(self):
        """Initialize package directory for existing packages."""
        if self.existing_package:
            self.package_name = self.existing_package
            self._package_dir = self.output_dir

    @property
    def package_dir(self) -> Path | None:
        """Get the package directory."""
        if self._package_dir:
            return self._package_dir
        if self.package_name:
            return self.output_dir / self.package_name
        return None

    def get_tools(self) -> list[dict[str, Any]]:
        """Define the tools available to the Runner."""
        return [
            {
                "name": "init_package",
                "description": "Initialize a new wetwire-gitlab package. Creates __init__.py with imports.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "package_name": {
                            "type": "string",
                            "description": "Name for the package (snake_case, e.g., 'my_pipeline')",
                        },
                        "description": {
                            "type": "string",
                            "description": "Brief description of what this pipeline does",
                        },
                    },
                    "required": ["package_name", "description"],
                },
            },
            {
                "name": "write_file",
                "description": "Write a Python file to the package. Use for job/pipeline definitions.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "filename": {
                            "type": "string",
                            "description": "Filename (e.g., 'jobs.py', 'pipeline.py')",
                        },
                        "content": {
                            "type": "string",
                            "description": "Python code content",
                        },
                    },
                    "required": ["filename", "content"],
                },
            },
            {
                "name": "run_lint",
                "description": "Run wetwire-gitlab lint on the package to check for issues.",
                "input_schema": {
                    "type": "object",
                    "properties": {},
                },
            },
            {
                "name": "run_build",
                "description": "Run wetwire-gitlab build to generate .gitlab-ci.yml.",
                "input_schema": {
                    "type": "object",
                    "properties": {},
                },
            },
            {
                "name": "read_file",
                "description": "Read a file from the package to see its current contents.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "filename": {
                            "type": "string",
                            "description": "Filename to read (e.g., 'jobs.py', 'pipeline.py')",
                        },
                    },
                    "required": ["filename"],
                },
            },
            {
                "name": "ask_developer",
                "description": "Ask the developer a clarifying question. Use sparingly.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "question": {
                            "type": "string",
                            "description": "The question to ask the developer",
                        },
                    },
                    "required": ["question"],
                },
            },
        ]

    def execute_tool(self, tool_name: str, tool_input: dict[str, Any]) -> ToolResult:
        """Execute a tool and return the result."""
        tool_use_id = f"tool_{tool_name}"

        if tool_name == "init_package":
            result = self._init_package(tool_use_id, tool_input)
        elif tool_name == "write_file":
            result = self._write_file(tool_use_id, tool_input)
        elif tool_name == "read_file":
            result = self._read_file(tool_use_id, tool_input)
        elif tool_name == "run_lint":
            result = self._run_lint(tool_use_id)
        elif tool_name == "run_build":
            result = self._run_build(tool_use_id)
        elif tool_name == "ask_developer":
            result = ToolResult(
                tool_use_id=tool_use_id,
                content=f"QUESTION: {tool_input['question']}",
            )
        else:
            result = ToolResult(
                tool_use_id=tool_use_id,
                content=f"Unknown tool: {tool_name}",
                is_error=True,
            )

        result.tool_name = tool_name
        return result

    def _init_package(self, tool_use_id: str, tool_input: dict[str, Any]) -> ToolResult:
        """Initialize a new package using wetwire-gitlab init."""
        self.package_name = tool_input["package_name"]
        description = tool_input.get("description", f"{self.package_name} pipeline")

        # Create package directory
        pkg_dir = self.output_dir / self.package_name
        pkg_dir.mkdir(parents=True, exist_ok=True)

        # Create __init__.py with standard imports
        init_content = f'''"""{description}"""

from wetwire_gitlab.pipeline import (
    Artifacts,
    Cache,
    Job,
    Pipeline,
    Rule,
)
from wetwire_gitlab.intrinsics import CI, GitLab, MR, Rules, When
'''
        (pkg_dir / "__init__.py").write_text(init_content)

        return ToolResult(
            tool_use_id=tool_use_id,
            content=f"Created package '{self.package_name}' at {pkg_dir}",
        )

    def _write_file(self, tool_use_id: str, tool_input: dict[str, Any]) -> ToolResult:
        """Write a file to the package."""
        if not self.package_dir:
            return ToolResult(
                tool_use_id=tool_use_id,
                content="Error: Must init_package first",
                is_error=True,
            )

        file_path = self.package_dir / tool_input["filename"]
        file_path.write_text(tool_input["content"])

        return ToolResult(
            tool_use_id=tool_use_id,
            content=f"Wrote {tool_input['filename']} ({len(tool_input['content'])} bytes)",
        )

    def _read_file(self, tool_use_id: str, tool_input: dict[str, Any]) -> ToolResult:
        """Read a file from the package."""
        if not self.package_dir:
            return ToolResult(
                tool_use_id=tool_use_id,
                content="Error: No package initialized",
                is_error=True,
            )

        file_path = self.package_dir / tool_input["filename"]

        if not file_path.exists():
            return ToolResult(
                tool_use_id=tool_use_id,
                content=f"File not found: {tool_input['filename']}",
                is_error=True,
            )

        content = file_path.read_text()
        return ToolResult(
            tool_use_id=tool_use_id,
            content=f"Contents of {tool_input['filename']}:\n\n{content}",
        )

    def _run_lint(self, tool_use_id: str) -> ToolResult:
        """Run lint on the package."""
        if not self.package_dir:
            return ToolResult(
                tool_use_id=tool_use_id,
                content="Error: Must init_package first",
                is_error=True,
            )

        result = subprocess.run(
            [sys.executable, "-m", "wetwire_gitlab.cli", "lint", str(self.package_dir)],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            return ToolResult(
                tool_use_id=tool_use_id,
                content="Lint passed with no issues",
            )
        else:
            return ToolResult(
                tool_use_id=tool_use_id,
                content=f"Lint found issues:\n{result.stdout}\n{result.stderr}",
            )

    def _run_build(self, tool_use_id: str) -> ToolResult:
        """Run build on the package."""
        if not self.package_dir:
            return ToolResult(
                tool_use_id=tool_use_id,
                content="Error: Must init_package first",
                is_error=True,
            )

        # Set PYTHONPATH to include output_dir so the package can be imported
        pythonpath = (
            str(self.package_dir.parent)
            if self.existing_package
            else str(self.output_dir)
        )

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "wetwire_gitlab.cli",
                "build",
                str(self.package_dir),
            ],
            capture_output=True,
            text=True,
            env={**os.environ, "PYTHONPATH": pythonpath},
        )

        if result.returncode == 0:
            return ToolResult(
                tool_use_id=tool_use_id,
                content=f"Build successful. GitLab CI config:\n{result.stdout}",
            )
        else:
            return ToolResult(
                tool_use_id=tool_use_id,
                content=f"Build failed:\n{result.stderr}",
                is_error=True,
            )

    def run_turn(
        self, developer_message: str | None = None
    ) -> tuple[str, list[ToolResult]]:
        """Run one turn of the Runner agent.

        Returns:
            Tuple of (response_text, tool_results)
        """
        if developer_message:
            self.conversation.append({"role": "user", "content": developer_message})

        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=RUNNER_SYSTEM_PROMPT,
            tools=self.get_tools(),
            messages=self.conversation,
        )

        tool_results: list[ToolResult] = []
        response_text = ""

        for block in response.content:
            if block.type == "text":
                response_text += block.text
            elif block.type == "tool_use":
                result = self.execute_tool(block.name, block.input)
                result.tool_use_id = block.id
                tool_results.append(result)

        self.conversation.append({"role": "assistant", "content": response.content})

        if tool_results:
            tool_result_content = [
                {
                    "type": "tool_result",
                    "tool_use_id": r.tool_use_id,
                    "content": r.content,
                    "is_error": r.is_error,
                }
                for r in tool_results
            ]
            self.conversation.append({"role": "user", "content": tool_result_content})

        return response_text, tool_results


def detect_existing_package(directory: Path) -> tuple[str | None, list[str]]:
    """Detect if directory contains an existing wetwire-gitlab package.

    Returns:
        Tuple of (package_name or None, list of .py files)
    """
    init_file = directory / "__init__.py"
    if not init_file.exists():
        return None, []

    content = init_file.read_text()
    # Check for wetwire-gitlab imports or Pipeline/Job usage
    if (
        "wetwire_gitlab" not in content
        and "Pipeline" not in content
        and "Job" not in content
    ):
        return None, []

    package_name = directory.name
    py_files = [f.name for f in directory.glob("*.py") if f.name != "__init__.py"]

    return package_name, py_files
