"""YAML parser for GitLab CI/CD configuration.

This module provides functionality to parse .gitlab-ci.yml files
into intermediate representation.
"""

from pathlib import Path
from typing import Any

import yaml

from .ir import IRInclude, IRJob, IRPipeline, IRRule

# Reserved keys that are not job definitions
RESERVED_KEYS = {
    "stages",
    "include",
    "variables",
    "default",
    "workflow",
    "image",
    "before_script",
    "after_script",
    "services",
    "cache",
    "artifacts",
}


def _parse_rule(rule_data: dict[str, Any]) -> IRRule:
    """Parse a single rule from YAML data.

    Args:
        rule_data: Rule configuration dictionary.

    Returns:
        IRRule instance.
    """
    return IRRule(
        if_=rule_data.get("if"),
        when=rule_data.get("when"),
        allow_failure=rule_data.get("allow_failure"),
        changes=rule_data.get("changes"),
        exists=rule_data.get("exists"),
        variables=rule_data.get("variables"),
    )


def _parse_include(include_data: str | dict[str, Any]) -> IRInclude:
    """Parse a single include from YAML data.

    Args:
        include_data: Include configuration (string or dictionary).

    Returns:
        IRInclude instance.
    """
    if isinstance(include_data, str):
        # Simple string include (assume local)
        return IRInclude(local=include_data)

    return IRInclude(
        local=include_data.get("local"),
        remote=include_data.get("remote"),
        template=include_data.get("template"),
        project=include_data.get("project"),
        file=include_data.get("file"),
        ref=include_data.get("ref"),
        component=include_data.get("component"),
        inputs=include_data.get("inputs"),
    )


def _parse_job(name: str, job_data: dict[str, Any]) -> IRJob:
    """Parse a single job from YAML data.

    Args:
        name: Job name (YAML key).
        job_data: Job configuration dictionary.

    Returns:
        IRJob instance.
    """
    rules = None
    if "rules" in job_data:
        rules = [_parse_rule(r) for r in job_data["rules"]]

    return IRJob(
        name=name,
        stage=job_data.get("stage"),
        script=job_data.get("script"),
        before_script=job_data.get("before_script"),
        after_script=job_data.get("after_script"),
        image=job_data.get("image"),
        rules=rules,
        artifacts=job_data.get("artifacts"),
        cache=job_data.get("cache"),
        needs=job_data.get("needs"),
        variables=job_data.get("variables"),
        tags=job_data.get("tags"),
        when=job_data.get("when"),
        allow_failure=job_data.get("allow_failure"),
        timeout=job_data.get("timeout"),
        retry=job_data.get("retry"),
        extends=job_data.get("extends"),
        dependencies=job_data.get("dependencies"),
        services=job_data.get("services"),
        environment=job_data.get("environment"),
        coverage=job_data.get("coverage"),
        resource_group=job_data.get("resource_group"),
        interruptible=job_data.get("interruptible"),
        parallel=job_data.get("parallel"),
        trigger=job_data.get("trigger"),
        release=job_data.get("release"),
    )


def parse_gitlab_ci(yaml_content: str) -> IRPipeline:
    """Parse GitLab CI YAML content into intermediate representation.

    Args:
        yaml_content: YAML content as string.

    Returns:
        IRPipeline instance.
    """
    data = yaml.safe_load(yaml_content)

    if not data:
        return IRPipeline()

    # Parse stages
    stages = data.get("stages", [])

    # Parse includes
    includes: list[IRInclude] = []
    if "include" in data:
        include_data = data["include"]
        if isinstance(include_data, list):
            includes = [_parse_include(i) for i in include_data]
        else:
            includes = [_parse_include(include_data)]

    # Parse jobs (all keys not in reserved set)
    jobs: list[IRJob] = []
    for key, value in data.items():
        if key not in RESERVED_KEYS and isinstance(value, dict):
            # Skip keys starting with . (hidden jobs/templates)
            if not key.startswith("."):
                jobs.append(_parse_job(key, value))

    # Parse variables
    variables = data.get("variables")

    # Parse default
    default = data.get("default")

    # Parse workflow
    workflow = data.get("workflow")

    return IRPipeline(
        stages=stages,
        jobs=jobs,
        includes=includes,
        variables=variables,
        default=default,
        workflow=workflow,
    )


def parse_gitlab_ci_file(file_path: Path) -> IRPipeline:
    """Parse GitLab CI YAML file into intermediate representation.

    Args:
        file_path: Path to .gitlab-ci.yml file.

    Returns:
        IRPipeline instance.
    """
    content = file_path.read_text()
    return parse_gitlab_ci(content)
