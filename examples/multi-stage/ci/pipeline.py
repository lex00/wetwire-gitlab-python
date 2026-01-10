"""Pipeline configuration for multi-stage pipeline."""

from wetwire_gitlab.pipeline import Pipeline

pipeline = Pipeline(
    stages=["prepare", "build", "test", "quality", "deploy"],
)
