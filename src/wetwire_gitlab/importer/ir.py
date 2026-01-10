"""Intermediate representation types for YAML importing.

These types represent parsed GitLab CI/CD configuration before
conversion to typed Python objects.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from wetwire_gitlab.pipeline import Pipeline


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

    def to_job(self) -> Any:
        """Convert IRJob to typed Job object.

        Most fields can be passed through directly as Job accepts raw dicts.
        Only rules need conversion from IRRule to Rule.

        Returns:
            Job instance.
        """
        from wetwire_gitlab.pipeline import Job, Rule

        # Convert rules from IRRule to Rule
        rules_list = None
        if self.rules:
            rules_list = []
            for ir_rule in self.rules:
                rule_kwargs = {}
                if ir_rule.if_ is not None:
                    rule_kwargs["if_"] = ir_rule.if_
                if ir_rule.when is not None:
                    rule_kwargs["when"] = ir_rule.when
                if ir_rule.allow_failure is not None:
                    rule_kwargs["allow_failure"] = ir_rule.allow_failure
                if ir_rule.changes is not None:
                    rule_kwargs["changes"] = ir_rule.changes
                if ir_rule.exists is not None:
                    rule_kwargs["exists"] = ir_rule.exists
                if ir_rule.variables is not None:
                    rule_kwargs["variables"] = ir_rule.variables
                rules_list.append(Rule(**rule_kwargs))

        return Job(
            name=self.name,
            stage=self.stage,
            script=self.script,
            before_script=self.before_script,
            after_script=self.after_script,
            image=self.image,  # type: ignore
            rules=rules_list,
            artifacts=self.artifacts,  # type: ignore
            cache=self.cache,  # type: ignore
            needs=self.needs,
            variables=self.variables,
            tags=self.tags,
            when=self.when,
            allow_failure=self.allow_failure,
            timeout=self.timeout,
            retry=self.retry,
            extends=self.extends,
            dependencies=self.dependencies,
            services=self.services,
            environment=self.environment,
            coverage=self.coverage,
            resource_group=self.resource_group,
            interruptible=self.interruptible,
            parallel=self.parallel,
            trigger=self.trigger,  # type: ignore
            release=self.release,
        )


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
        cache: Top-level cache configuration.
        services: Top-level services configuration.
    """

    stages: list[str] = field(default_factory=list)
    jobs: list[IRJob] = field(default_factory=list)
    includes: list[IRInclude] = field(default_factory=list)
    variables: dict[str, str | dict[str, Any]] | None = None
    default: dict[str, Any] | None = None
    workflow: dict[str, Any] | None = None
    cache: dict[str, Any] | list[dict[str, Any]] | None = None
    services: list[str | dict[str, Any]] | None = None

    def to_pipeline(self) -> Pipeline:
        """Convert IRPipeline to typed Pipeline object.

        Note: This is a simplified conversion that works for serialization.
        Default and Workflow are kept as raw dicts since they're already
        properly structured from parsing.

        Returns:
            Pipeline instance with converted fields.
        """
        from wetwire_gitlab.pipeline import Include, Pipeline

        # Convert includes
        include_list = None
        if self.includes:
            include_list = []
            for inc in self.includes:
                include_kwargs = {}
                if inc.local is not None:
                    include_kwargs["local"] = inc.local
                if inc.remote is not None:
                    include_kwargs["remote"] = inc.remote
                if inc.template is not None:
                    include_kwargs["template"] = inc.template
                if inc.project is not None:
                    include_kwargs["project"] = inc.project
                if inc.file is not None:
                    include_kwargs["file"] = inc.file
                if inc.ref is not None:
                    include_kwargs["ref"] = inc.ref
                if inc.component is not None:
                    include_kwargs["component"] = inc.component
                if inc.inputs is not None:
                    include_kwargs["inputs"] = inc.inputs
                include_list.append(Include(**include_kwargs))

        # For serialization purposes, we can pass the dicts directly
        # The serializer will handle them correctly
        return Pipeline(
            stages=self.stages if self.stages else None,
            workflow=self.workflow,  # type: ignore
            include=include_list,
            default=self.default,  # type: ignore
            variables=self.variables,  # type: ignore
            cache=self.cache,  # type: ignore
            services=self.services,  # type: ignore
        )
