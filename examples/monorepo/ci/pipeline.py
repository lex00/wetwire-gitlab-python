"""Pipeline configuration for monorepo."""

from wetwire_gitlab.pipeline import Pipeline

pipeline = Pipeline(
    stages=["detect", "trigger"],
)
