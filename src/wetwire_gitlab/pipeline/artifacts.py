"""Artifacts configuration for GitLab CI jobs."""

from dataclasses import dataclass
from typing import Any


@dataclass
class Artifacts:
    """Artifacts configuration for a job.

    Attributes:
        paths: List of paths to include in artifacts.
        exclude: List of paths to exclude from artifacts.
        expire_in: When artifacts expire (e.g., "1 week", "30 days").
        expose_as: Name to display in merge request UI.
        name: Custom name for the artifacts archive.
        untracked: Include git-untracked files.
        when: When to upload artifacts (on_success, on_failure, always).
        reports: Reports configuration (junit, coverage_report, etc.).
    """

    paths: list[str] | None = None
    exclude: list[str] | None = None
    expire_in: str | None = None
    expose_as: str | None = None
    name: str | None = None
    untracked: bool | None = None
    when: str | None = None
    reports: dict[str, Any] | None = None
