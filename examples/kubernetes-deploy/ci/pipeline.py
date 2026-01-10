"""Pipeline configuration for Kubernetes deployment."""

from wetwire_gitlab.pipeline import Pipeline

pipeline = Pipeline(
    stages=["build", "deploy"],
)
