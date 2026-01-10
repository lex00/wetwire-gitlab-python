"""Pipeline configuration for Python application."""

from wetwire_gitlab.pipeline import Pipeline

pipeline = Pipeline(
    stages=["test", "deploy"],
)
