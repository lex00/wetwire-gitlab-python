"""Job definitions for Python application pipeline."""

from wetwire_gitlab.intrinsics import CI, When
from wetwire_gitlab.pipeline import Artifacts, Cache, Job, Rule

# Cache configuration for pip
pip_cache = Cache(
    key="${CI_JOB_NAME}",
    paths=[".cache/pip"],
)

# Test jobs for each Python version
test_py311 = Job(
    name="test-py311",
    stage="test",
    image="python:3.11",
    script=[
        "pip install -e .[dev]",
        "pytest --cov=src --cov-report=xml",
    ],
    cache=pip_cache,
    artifacts=Artifacts(
        paths=["coverage.xml"],
        reports={
            "coverage_report": {"coverage_format": "cobertura", "path": "coverage.xml"}
        },
    ),
)

test_py312 = Job(
    name="test-py312",
    stage="test",
    image="python:3.12",
    script=[
        "pip install -e .[dev]",
        "pytest --cov=src --cov-report=xml",
    ],
    cache=pip_cache,
)

test_py313 = Job(
    name="test-py313",
    stage="test",
    image="python:3.13",
    script=[
        "pip install -e .[dev]",
        "pytest --cov=src --cov-report=xml",
    ],
    cache=pip_cache,
)

# Lint job
lint = Job(
    name="lint",
    stage="test",
    image="python:3.11",
    script=[
        "pip install ruff",
        "ruff check src tests",
    ],
)

# Deploy job (manual, default branch only)
deploy = Job(
    name="deploy",
    stage="deploy",
    image="python:3.11",
    script=[
        "pip install build twine",
        "python -m build",
        "twine upload dist/*",
    ],
    rules=[
        Rule(
            if_=f"{CI.COMMIT_BRANCH} == {CI.DEFAULT_BRANCH}",
            when=When.MANUAL,
        ),
    ],
    needs=["test-py311", "test-py312", "test-py313", "lint"],
)
