"""Intermediate representation types for YAML importing.

These types represent parsed GitLab CI/CD configuration before
conversion to typed Python objects.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class IRRule:
    """Intermediate representation for a rule.

    Attributes:
        if_: Conditional expression.
        when: When to run (always, manual, never, etc.).
        allow_failure: Allow job to fail.
        changes: Files that must change for rule to match.
        exists: Files that must exist for rule to match.
        variables: Variables to set when rule matches.
    """

    if_: str | None = None
    when: str | None = None
    allow_failure: bool | None = None
    changes: list[str] | None = None
    exists: list[str] | None = None
    variables: dict[str, str] | None = None


@dataclass
class IRInclude:
    """Intermediate representation for an include.

    Attributes:
        local: Local file path.
        remote: Remote URL.
        template: GitLab template name.
        project: Project path for project includes.
        file: File path for project includes.
        ref: Git ref for project includes.
        component: Component reference.
        inputs: Component inputs.
    """

    local: str | None = None
    remote: str | None = None
    template: str | None = None
    project: str | None = None
    file: str | list[str] | None = None
    ref: str | None = None
    component: str | None = None
    inputs: dict[str, Any] | None = None


@dataclass
class IRJob:
    """Intermediate representation for a job.

    Attributes:
        name: Job name (YAML key).
        stage: Stage name.
        script: List of commands.
        before_script: Commands before script.
        after_script: Commands after script.
        image: Docker image.
        rules: List of rules.
        artifacts: Artifacts configuration.
        cache: Cache configuration.
        needs: Job dependencies.
        variables: Job variables.
        tags: Runner tags.
        when: When to run.
        allow_failure: Allow failure.
        timeout: Job timeout.
        retry: Retry configuration.
        extends: Jobs to extend.
        dependencies: Artifact dependencies.
        services: Service containers.
        environment: Environment configuration.
        coverage: Coverage regex.
        resource_group: Resource group name.
        interruptible: Can be cancelled.
        parallel: Parallel job count.
        trigger: Trigger configuration.
        release: Release configuration.
    """

    name: str
    stage: str | None = None
    script: list[str] | None = None
    before_script: list[str] | None = None
    after_script: list[str] | None = None
    image: str | dict[str, Any] | None = None
    rules: list[IRRule] | None = None
    artifacts: dict[str, Any] | None = None
    cache: dict[str, Any] | None = None
    needs: list[str | dict[str, Any]] | None = None
    variables: dict[str, str] | None = None
    tags: list[str] | None = None
    when: str | None = None
    allow_failure: bool | dict[str, Any] | None = None
    timeout: str | None = None
    retry: int | dict[str, Any] | None = None
    extends: str | list[str] | None = None
    dependencies: list[str] | None = None
    services: list[str | dict[str, Any]] | None = None
    environment: str | dict[str, Any] | None = None
    coverage: str | None = None
    resource_group: str | None = None
    interruptible: bool | None = None
    parallel: int | dict[str, Any] | None = None
    trigger: dict[str, Any] | None = None
    release: dict[str, Any] | None = None


@dataclass
class IRPipeline:
    """Intermediate representation for a pipeline.

    Attributes:
        stages: List of stage names.
        jobs: List of jobs.
        includes: List of includes.
        variables: Pipeline variables.
        default: Default job configuration.
        workflow: Workflow configuration.
    """

    stages: list[str] = field(default_factory=list)
    jobs: list[IRJob] = field(default_factory=list)
    includes: list[IRInclude] = field(default_factory=list)
    variables: dict[str, str | dict[str, Any]] | None = None
    default: dict[str, Any] | None = None
    workflow: dict[str, Any] | None = None
