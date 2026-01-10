"""Pipeline configuration for GitLab CI."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .default import Default
    from .include import Include
    from .variables import Variable
    from .workflow import Workflow


@dataclass
class Pipeline:
    """Top-level pipeline configuration.

    Attributes:
        stages: List of stage names in execution order.
        workflow: Workflow configuration for pipeline-level rules.
        include: List of include configurations.
        default: Default job configuration.
        variables: Pipeline-level variables.
        cache: Top-level cache configuration (applied to all jobs).
        services: Top-level services configuration (applied to all jobs).
    """

    stages: list[str] | None = None
    workflow: Workflow | None = None
    include: list[Include] | None = None
    default: Default | None = None
    variables: dict[str, str | Variable] | None = None
    cache: dict | list[dict] | None = None
    services: list[str | dict] | None = None
