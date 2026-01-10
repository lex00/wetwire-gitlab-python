"""Tests for example projects."""

import importlib
import sys
from pathlib import Path

import pytest

# Add examples to path for import
EXAMPLES_DIR = Path(__file__).parent.parent.parent / "examples"


def import_example_ci(example_name: str):
    """Import the ci module from an example, handling sys.path correctly."""
    example_path = str(EXAMPLES_DIR / example_name)

    # Remove any existing ci module and example paths
    if "ci" in sys.modules:
        del sys.modules["ci"]
    for key in list(sys.modules.keys()):
        if key.startswith("ci."):
            del sys.modules[key]

    # Remove old example paths from sys.path
    sys.path = [p for p in sys.path if "examples" not in p]

    # Add new example path and import
    sys.path.insert(0, example_path)
    return importlib.import_module("ci")


@pytest.mark.slow
class TestPythonAppExample:
    """Tests for python-app example."""

    def test_imports(self):
        """Example modules can be imported."""
        ci = import_example_ci("python-app")

        assert ci.pipeline is not None
        assert ci.test_py311.name == "test-py311"
        assert ci.test_py312.name == "test-py312"
        assert ci.test_py313.name == "test-py313"
        assert ci.lint.name == "lint"
        assert ci.deploy.name == "deploy"

    def test_pipeline_stages(self):
        """Pipeline has correct stages."""
        ci = import_example_ci("python-app")

        assert ci.pipeline.stages == ["test", "deploy"]

    def test_job_stages(self):
        """Jobs have correct stages."""
        ci = import_example_ci("python-app")

        assert ci.test_py311.stage == "test"
        assert ci.lint.stage == "test"
        assert ci.deploy.stage == "deploy"


@pytest.mark.slow
class TestDockerBuildExample:
    """Tests for docker-build example."""

    def test_imports(self):
        """Example modules can be imported."""
        ci = import_example_ci("docker-build")

        assert ci.pipeline is not None
        assert ci.build.name == "build"
        assert ci.test.name == "test"
        assert ci.push.name == "push"

    def test_pipeline_stages(self):
        """Pipeline has correct stages."""
        ci = import_example_ci("docker-build")

        assert ci.pipeline.stages == ["build", "test", "push"]


@pytest.mark.slow
class TestMultiStageExample:
    """Tests for multi-stage example."""

    def test_imports(self):
        """Example modules can be imported."""
        ci = import_example_ci("multi-stage")

        assert ci.pipeline is not None
        assert ci.prepare.name == "prepare"
        assert ci.build_frontend.name == "build-frontend"
        assert ci.deploy_production.name == "deploy-production"

    def test_pipeline_stages(self):
        """Pipeline has correct stages."""
        ci = import_example_ci("multi-stage")

        assert ci.pipeline.stages == ["prepare", "build", "test", "quality", "deploy"]

    def test_job_dependencies(self):
        """Jobs have correct dependencies."""
        ci = import_example_ci("multi-stage")

        assert ci.build_frontend.needs == ["prepare"]
        assert "build-frontend" in ci.test_unit.needs
        assert "test-unit" in ci.deploy_staging.needs


@pytest.mark.slow
class TestKubernetesDeployExample:
    """Tests for kubernetes-deploy example."""

    def test_imports(self):
        """Example modules can be imported."""
        ci = import_example_ci("kubernetes-deploy")

        assert ci.pipeline is not None
        assert ci.build.name == "build"
        assert ci.deploy_dev.name == "deploy-dev"
        assert ci.deploy_staging.name == "deploy-staging"
        assert ci.deploy_production.name == "deploy-production"

    def test_environments(self):
        """Jobs have correct environments."""
        ci = import_example_ci("kubernetes-deploy")

        assert ci.deploy_dev.environment["name"] == "development"
        assert ci.deploy_staging.environment["name"] == "staging"
        assert ci.deploy_production.environment["name"] == "production"


@pytest.mark.slow
class TestMonorepoExample:
    """Tests for monorepo example."""

    def test_imports(self):
        """Example modules can be imported."""
        ci = import_example_ci("monorepo")

        assert ci.pipeline is not None
        assert ci.detect_changes.name == "detect-changes"
        assert ci.trigger_frontend.name == "trigger-frontend"

    def test_pipeline_stages(self):
        """Pipeline has correct stages."""
        ci = import_example_ci("monorepo")

        assert ci.pipeline.stages == ["detect", "trigger"]

    def test_trigger_jobs(self):
        """Trigger jobs have correct configuration."""
        ci = import_example_ci("monorepo")

        assert ci.trigger_frontend.trigger is not None
        assert ci.trigger_frontend.needs == ["detect-changes"]
