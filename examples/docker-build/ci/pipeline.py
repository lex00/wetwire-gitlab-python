"""Pipeline configuration for Docker build."""

from wetwire_gitlab.pipeline import Pipeline

pipeline = Pipeline(
    stages=["build", "test", "push"],
)
