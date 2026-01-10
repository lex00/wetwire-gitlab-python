"""Tests for test command implementation."""

import subprocess
import sys
import tempfile
from pathlib import Path

import pytest


class TestTestCommandIntegration:
    """Integration tests for test command."""

    def test_test_help(self):
        """Test command shows help."""
        result = subprocess.run(
            [sys.executable, "-m", "wetwire_gitlab.cli", "test", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "test" in result.stdout.lower()

    def test_test_persona_flag(self):
        """Test command accepts --persona flag."""
        result = subprocess.run(
            [sys.executable, "-m", "wetwire_gitlab.cli", "test", "--help"],
            capture_output=True,
            text=True,
        )
        assert "--persona" in result.stdout


class TestTestCommandUnit:
    """Unit tests for test command logic."""

    def test_run_test_function_exists(self):
        """run_test function is importable."""
        from wetwire_gitlab.cli.main import run_test

        assert callable(run_test)

    def test_personas_importable(self):
        """Personas are importable from wetwire-core."""
        from wetwire_core.agent.personas import PERSONAS

        assert "beginner" in PERSONAS
        assert "intermediate" in PERSONAS
        assert "expert" in PERSONAS
        assert "terse" in PERSONAS
        assert "verbose" in PERSONAS

    def test_scoring_importable(self):
        """Scoring module is importable from wetwire-core."""
        from wetwire_core.agent.scoring import Score, calculate_score

        assert Score is not None
        assert callable(calculate_score)

    def test_results_writer_importable(self):
        """ResultsWriter is importable from wetwire-core."""
        from wetwire_core.agent.results import ResultsWriter, SessionResults

        assert ResultsWriter is not None
        assert SessionResults is not None


class TestPersonaLoading:
    """Tests for persona loading."""

    def test_load_beginner_persona(self):
        """Beginner persona loads correctly."""
        from wetwire_core.agent.personas import load_persona

        persona = load_persona("beginner")
        assert persona.name == "beginner"
        assert "vague" in persona.traits

    def test_load_expert_persona(self):
        """Expert persona loads correctly."""
        from wetwire_core.agent.personas import load_persona

        persona = load_persona("expert")
        assert persona.name == "expert"
        assert "precise" in persona.traits

    def test_load_invalid_persona_raises(self):
        """Loading invalid persona raises ValueError."""
        from wetwire_core.agent.personas import load_persona

        with pytest.raises(ValueError):
            load_persona("invalid_persona")


class TestScoring:
    """Tests for scoring integration."""

    def test_score_calculation(self):
        """Score calculation works correctly."""
        from wetwire_core.agent.scoring import calculate_score

        score = calculate_score(
            produced_package=True,
            missing_resources=0,
            total_resources=3,
            lint_cycles=0,
            lint_passed=True,
            syntax_valid=True,
            pattern_issues=0,
            output_valid=True,
            validation_errors=0,
            validation_warnings=0,
            questions_asked=0,
            appropriate_questions=0,
        )
        assert score.total == 15
        assert score.grade == "Excellent"

    def test_score_failed_case(self):
        """Score calculation handles failure case."""
        from wetwire_core.agent.scoring import calculate_score

        score = calculate_score(
            produced_package=False,
            missing_resources=3,
            total_resources=3,
            lint_cycles=5,
            lint_passed=False,
            syntax_valid=False,
            pattern_issues=10,
            output_valid=False,
            validation_errors=5,
            validation_warnings=5,
            questions_asked=10,
            appropriate_questions=0,
        )
        assert score.total == 0
        assert score.grade == "Failure"


class TestResultsWriter:
    """Tests for results writing."""

    def test_results_format(self):
        """ResultsWriter formats results as markdown."""
        from wetwire_core.agent.results import ResultsWriter, SessionResults
        from wetwire_core.agent.scoring import Rating, Score

        results = SessionResults(
            prompt="Create a CI pipeline",
            package_name="my_pipeline",
            domain="gitlab",
            persona="beginner",
            summary="Created a simple pipeline",
            score=Score(
                completeness=Rating.EXCELLENT,
                lint_quality=Rating.EXCELLENT,
                code_quality=Rating.EXCELLENT,
                output_validity=Rating.EXCELLENT,
                question_efficiency=Rating.EXCELLENT,
            ),
        )

        writer = ResultsWriter()
        markdown = writer.format(results)

        assert "# Package Generation Results" in markdown
        assert "my_pipeline" in markdown
        assert "gitlab" in markdown
        assert "beginner" in markdown

    def test_results_write_to_file(self):
        """ResultsWriter writes to file."""
        from wetwire_core.agent.results import ResultsWriter, SessionResults

        results = SessionResults(
            prompt="Test prompt",
            package_name="test_pkg",
            domain="gitlab",
        )

        writer = ResultsWriter()

        with tempfile.TemporaryDirectory() as tmp:
            output_path = Path(tmp) / "RESULTS.md"
            writer.write(results, output_path)
            assert output_path.exists()
            content = output_path.read_text()
            assert "test_pkg" in content


class TestAIConversationHandler:
    """Tests for AI conversation orchestration."""

    def test_ai_conversation_handler_importable(self):
        """AIConversationHandler is importable."""
        from wetwire_core.agents import AIConversationHandler

        assert AIConversationHandler is not None

    def test_developer_agent_importable(self):
        """DeveloperAgent is importable."""
        from wetwire_core.agents import DeveloperAgent

        assert DeveloperAgent is not None
