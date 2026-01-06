"""Image configuration for GitLab CI jobs."""

from dataclasses import dataclass


@dataclass
class Image:
    """Docker image configuration for a job.

    Attributes:
        name: The image name (e.g., "python:3.11").
        entrypoint: Override the image's default entrypoint.
        pull_policy: When to pull the image (always, if-not-present, never).
    """

    name: str
    entrypoint: list[str] | None = None
    pull_policy: str | None = None
