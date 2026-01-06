"""Trigger configuration for child/multi-project pipelines."""

from dataclasses import dataclass
from typing import Any


@dataclass
class Trigger:
    """Trigger configuration for child or multi-project pipelines.

    Attributes:
        include: Path to child pipeline configuration file.
        project: Project path for multi-project pipelines.
        branch: Branch to use for multi-project pipelines.
        strategy: Strategy for pipeline dependencies (depend).
        forward: Configuration for variable forwarding.
    """

    include: str | None = None
    project: str | None = None
    branch: str | None = None
    strategy: str | None = None
    forward: dict[str, Any] | None = None
