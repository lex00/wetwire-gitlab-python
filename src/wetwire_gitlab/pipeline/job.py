"""Job configuration for GitLab CI pipelines."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .artifacts import Artifacts
    from .cache import Cache
    from .image import Image
    from .rules import Rule
    from .trigger import Trigger


@dataclass
class Job:
    """Job configuration for a GitLab CI pipeline.

    Attributes:
        name: The job name (used as the YAML key).
        stage: The stage this job belongs to.
        image: Docker image for the job.
        script: List of shell commands to run.
        before_script: Commands to run before script.
        after_script: Commands to run after script (always runs).
        rules: List of rules for conditional execution.
        artifacts: Artifacts configuration.
        cache: Cache configuration.
        needs: List of job dependencies.
        variables: Job-specific variables.
        allow_failure: Allow job to fail without failing pipeline.
        when: When to run the job (on_success, manual, always, etc.).
        timeout: Job timeout (e.g., "1h", "30m").
        retry: Number of retries or retry configuration.
        tags: Runner tags for job selection.
        services: List of service containers.
        coverage: Regex for extracting coverage from output.
        environment: Environment name or configuration.
        resource_group: Resource group for job concurrency control.
        interruptible: Whether job can be cancelled.
        parallel: Number of parallel job instances.
        trigger: Trigger configuration for child/multi-project pipelines.
        extends: Jobs to extend from.
        dependencies: Jobs to download artifacts from.
        release: Release configuration.
        secrets: Secrets configuration.
        id_tokens: ID tokens configuration.
    """

    name: str = ""
    stage: str | None = None
    image: Image | None = None
    script: list[str] | None = None
    before_script: list[str] | None = None
    after_script: list[str] | None = None
    rules: list[Rule] | None = None
    artifacts: Artifacts | None = None
    cache: Cache | list[Cache] | None = None
    needs: list[str | Any] | None = None
    variables: dict[str, str] | None = None
    allow_failure: bool | dict[str, Any] | None = None
    when: str | None = None
    timeout: str | None = None
    retry: int | dict[str, Any] | None = None
    tags: list[str] | None = None
    services: list[str | dict[str, Any]] | None = None
    coverage: str | None = None
    environment: str | dict[str, Any] | None = None
    resource_group: str | None = None
    interruptible: bool | None = None
    parallel: int | dict[str, Any] | None = None
    trigger: Trigger | None = None
    extends: str | list[str] | None = None
    dependencies: list[str] | None = None
    release: dict[str, Any] | None = None
    secrets: dict[str, Any] | None = None
    id_tokens: dict[str, Any] | None = None
