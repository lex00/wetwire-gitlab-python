"""Workflow configuration for GitLab CI pipelines."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .rules import Rule


@dataclass
class Workflow:
    """Workflow configuration for pipeline-level rules.

    Attributes:
        rules: List of rules for the workflow.
        name: Name of the pipeline (visible in UI).
        auto_cancel: Auto-cancel configuration for redundant pipelines.
    """

    rules: list[Rule] | None = None
    name: str | None = None
    auto_cancel: dict[str, Any] | None = None
