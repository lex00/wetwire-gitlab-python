"""Tests for GitLab agent implementation."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


class TestGitLabRunnerAgent:
    """Tests for GitLabRunnerAgent class."""

    def test_gitlab_runner_agent_importable(self):
        """GitLabRunnerAgent is importable."""
        from wetwire_gitlab.agent import GitLabRunnerAgent

        assert GitLabRunnerAgent is not None

    def test_gitlab_runner_agent_is_dataclass(self):
        """GitLabRunnerAgent is a dataclass."""
        from dataclasses import is_dataclass

        from wetwire_gitlab.agent import GitLabRunnerAgent

        assert is_dataclass(GitLabRunnerAgent)

    def test_gitlab_runner_agent_has_output_dir(self):
        """GitLabRunnerAgent has output_dir attribute."""
        from wetwire_gitlab.agent import GitLabRunnerAgent

        with tempfile.TemporaryDirectory() as tmp:
            agent = GitLabRunnerAgent(output_dir=Path(tmp))
            assert agent.output_dir == Path(tmp)

    def test_gitlab_runner_agent_has_get_tools(self):
        """GitLabRunnerAgent has get_tools method."""
        from wetwire_gitlab.agent import GitLabRunnerAgent

        with tempfile.TemporaryDirectory() as tmp:
            agent = GitLabRunnerAgent(output_dir=Path(tmp))
            tools = agent.get_tools()
            assert isinstance(tools, list)
            assert len(tools) == 6

    def test_gitlab_runner_agent_tools_include_required(self):
        """GitLabRunnerAgent tools include all required tools."""
        from wetwire_gitlab.agent import GitLabRunnerAgent

        with tempfile.TemporaryDirectory() as tmp:
            agent = GitLabRunnerAgent(output_dir=Path(tmp))
            tools = agent.get_tools()
            tool_names = {t["name"] for t in tools}
            required = {"init_package", "write_file", "read_file", "run_lint", "run_build", "ask_developer"}
            assert tool_names == required

    def test_gitlab_runner_agent_execute_tool(self):
        """GitLabRunnerAgent can execute tools."""
        from wetwire_gitlab.agent import GitLabRunnerAgent

        with tempfile.TemporaryDirectory() as tmp:
            agent = GitLabRunnerAgent(output_dir=Path(tmp))
            # Execute unknown tool should return error
            result = agent.execute_tool("unknown", {})
            assert result.is_error

    def test_gitlab_runner_agent_init_package(self):
        """GitLabRunnerAgent can initialize a package."""
        from wetwire_gitlab.agent import GitLabRunnerAgent

        with tempfile.TemporaryDirectory() as tmp:
            agent = GitLabRunnerAgent(output_dir=Path(tmp))
            result = agent.execute_tool(
                "init_package",
                {"package_name": "test_pipeline", "description": "Test pipeline"},
            )
            assert not result.is_error
            assert agent.package_name == "test_pipeline"
            # Check package directory exists
            assert (Path(tmp) / "test_pipeline").exists()

    def test_gitlab_runner_agent_write_file(self):
        """GitLabRunnerAgent can write files."""
        from wetwire_gitlab.agent import GitLabRunnerAgent

        with tempfile.TemporaryDirectory() as tmp:
            agent = GitLabRunnerAgent(output_dir=Path(tmp))
            # First init package
            agent.execute_tool(
                "init_package",
                {"package_name": "test_pipeline", "description": "Test"},
            )
            # Then write file
            result = agent.execute_tool(
                "write_file",
                {"filename": "jobs.py", "content": "# test"},
            )
            assert not result.is_error
            assert (Path(tmp) / "test_pipeline" / "jobs.py").exists()

    def test_gitlab_runner_agent_read_file(self):
        """GitLabRunnerAgent can read files."""
        from wetwire_gitlab.agent import GitLabRunnerAgent

        with tempfile.TemporaryDirectory() as tmp:
            agent = GitLabRunnerAgent(output_dir=Path(tmp))
            # Init and write
            agent.execute_tool(
                "init_package",
                {"package_name": "test_pipeline", "description": "Test"},
            )
            agent.execute_tool(
                "write_file",
                {"filename": "jobs.py", "content": "# test content"},
            )
            # Read
            result = agent.execute_tool("read_file", {"filename": "jobs.py"})
            assert not result.is_error
            assert "test content" in result.content


class TestGitLabRunnerSystemPrompt:
    """Tests for GitLab-specific system prompt."""

    def test_runner_system_prompt_exists(self):
        """RUNNER_SYSTEM_PROMPT exists and mentions GitLab."""
        from wetwire_gitlab.agent import RUNNER_SYSTEM_PROMPT

        assert "gitlab" in RUNNER_SYSTEM_PROMPT.lower() or "GitLab" in RUNNER_SYSTEM_PROMPT

    def test_runner_system_prompt_mentions_pipeline(self):
        """RUNNER_SYSTEM_PROMPT mentions pipeline."""
        from wetwire_gitlab.agent import RUNNER_SYSTEM_PROMPT

        assert "pipeline" in RUNNER_SYSTEM_PROMPT.lower()

    def test_runner_system_prompt_mentions_job(self):
        """RUNNER_SYSTEM_PROMPT mentions Job."""
        from wetwire_gitlab.agent import RUNNER_SYSTEM_PROMPT

        assert "Job" in RUNNER_SYSTEM_PROMPT or "job" in RUNNER_SYSTEM_PROMPT.lower()


class TestToolResult:
    """Tests for ToolResult dataclass."""

    def test_tool_result_importable(self):
        """ToolResult is importable."""
        from wetwire_gitlab.agent import ToolResult

        assert ToolResult is not None

    def test_tool_result_is_dataclass(self):
        """ToolResult is a dataclass."""
        from dataclasses import is_dataclass

        from wetwire_gitlab.agent import ToolResult

        assert is_dataclass(ToolResult)

    def test_tool_result_creation(self):
        """ToolResult can be created with required fields."""
        from wetwire_gitlab.agent import ToolResult

        result = ToolResult(
            tool_use_id="test_id",
            content="test content",
        )
        assert result.tool_use_id == "test_id"
        assert result.content == "test content"
        assert not result.is_error
