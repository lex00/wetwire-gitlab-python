"""Python code generation from GitLab CI intermediate representation.

This module provides functionality to generate Python code from
the intermediate representation of GitLab CI/CD configuration.
"""

import re
from typing import Any

from .ir import IRJob, IRPipeline, IRRule


def _sanitize_identifier(name: str) -> str:
    """Convert a string to a valid Python identifier.

    Args:
        name: The original name.

    Returns:
        A valid Python identifier.
    """
    # Replace dashes with underscores
    result = name.replace("-", "_").replace(".", "_")
    # Remove any other invalid characters
    result = re.sub(r"[^a-zA-Z0-9_]", "", result)
    # Ensure it doesn't start with a number
    if result and result[0].isdigit():
        result = "_" + result
    return result


def _format_value(value: Any, indent: int = 0) -> str:
    """Format a value for Python code generation.

    Args:
        value: The value to format.
        indent: Current indentation level.

    Returns:
        Formatted Python code string.
    """
    indent_str = "    " * indent

    if value is None:
        return "None"
    elif isinstance(value, bool):
        return "True" if value else "False"
    elif isinstance(value, str):
        # Use repr for proper escaping
        return repr(value)
    elif isinstance(value, int | float):
        return str(value)
    elif isinstance(value, list):
        if not value:
            return "[]"
        if len(value) == 1:
            return f"[{_format_value(value[0])}]"
        items = ",\n".join(f"{indent_str}    {_format_value(v)}" for v in value)
        return f"[\n{items},\n{indent_str}]"
    elif isinstance(value, dict):
        if not value:
            return "{}"
        items = ",\n".join(
            f"{indent_str}    {repr(k)}: {_format_value(v)}" for k, v in value.items()
        )
        return f"{{\n{items},\n{indent_str}}}"
    else:
        return repr(value)


def _generate_rule(rule: IRRule, indent: int = 0) -> str:
    """Generate Python code for a Rule.

    Args:
        rule: The IRRule to generate code for.
        indent: Current indentation level.

    Returns:
        Python code string for the rule.
    """
    indent_str = "    " * indent
    parts = []

    if rule.if_ is not None:
        parts.append(f"if_={repr(rule.if_)}")
    if rule.when is not None:
        parts.append(f"when={repr(rule.when)}")
    if rule.allow_failure is not None:
        parts.append(f"allow_failure={rule.allow_failure}")
    if rule.changes is not None:
        parts.append(f"changes={_format_value(rule.changes)}")
    if rule.exists is not None:
        parts.append(f"exists={_format_value(rule.exists)}")
    if rule.variables is not None:
        parts.append(f"variables={_format_value(rule.variables)}")

    if len(parts) <= 2:
        return f"Rule({', '.join(parts)})"
    else:
        formatted_parts = f",\n{indent_str}        ".join(parts)
        return f"Rule(\n{indent_str}        {formatted_parts},\n{indent_str}    )"


def _generate_job(job: IRJob, indent: int = 0) -> str:  # noqa: ARG001
    """Generate Python code for a Job.

    Args:
        job: The IRJob to generate code for.
        indent: Current indentation level (reserved for future use).

    Returns:
        Python code string for the job.
    """
    var_name = _sanitize_identifier(job.name)

    lines = [f"{var_name} = Job("]
    lines.append(f'    name="{job.name}",')

    if job.stage:
        lines.append(f'    stage="{job.stage}",')

    if job.script:
        lines.append(f"    script={_format_value(job.script, 1)},")

    if job.before_script:
        lines.append(f"    before_script={_format_value(job.before_script, 1)},")

    if job.after_script:
        lines.append(f"    after_script={_format_value(job.after_script, 1)},")

    if job.image:
        if isinstance(job.image, str):
            lines.append(f'    image="{job.image}",')
        else:
            lines.append(f"    image={_format_value(job.image, 1)},")

    if job.rules:
        if len(job.rules) == 1:
            lines.append(f"    rules=[{_generate_rule(job.rules[0], 1)}],")
        else:
            rule_strs = [_generate_rule(r, 2) for r in job.rules]
            rules_formatted = ",\n        ".join(rule_strs)
            lines.append(f"    rules=[\n        {rules_formatted},\n    ],")

    if job.artifacts:
        lines.append(f"    artifacts={_format_value(job.artifacts, 1)},")

    if job.cache:
        lines.append(f"    cache={_format_value(job.cache, 1)},")

    if job.needs:
        lines.append(f"    needs={_format_value(job.needs, 1)},")

    if job.variables:
        lines.append(f"    variables={_format_value(job.variables, 1)},")

    if job.tags:
        lines.append(f"    tags={_format_value(job.tags, 1)},")

    if job.when:
        lines.append(f'    when="{job.when}",')

    if job.allow_failure is not None:
        lines.append(f"    allow_failure={job.allow_failure},")

    if job.timeout:
        lines.append(f'    timeout="{job.timeout}",')

    if job.retry:
        lines.append(f"    retry={_format_value(job.retry, 1)},")

    if job.extends:
        if isinstance(job.extends, str):
            lines.append(f'    extends="{job.extends}",')
        else:
            lines.append(f"    extends={_format_value(job.extends, 1)},")

    if job.dependencies:
        lines.append(f"    dependencies={_format_value(job.dependencies, 1)},")

    if job.services:
        lines.append(f"    services={_format_value(job.services, 1)},")

    if job.environment:
        if isinstance(job.environment, str):
            lines.append(f'    environment="{job.environment}",')
        else:
            lines.append(f"    environment={_format_value(job.environment, 1)},")

    if job.coverage:
        lines.append(f'    coverage="{job.coverage}",')

    if job.resource_group:
        lines.append(f'    resource_group="{job.resource_group}",')

    if job.interruptible is not None:
        lines.append(f"    interruptible={job.interruptible},")

    if job.parallel:
        lines.append(f"    parallel={_format_value(job.parallel, 1)},")

    if job.trigger:
        lines.append(f"    trigger={_format_value(job.trigger, 1)},")

    if job.release:
        lines.append(f"    release={_format_value(job.release, 1)},")

    lines.append(")")

    return "\n".join(lines)


def generate_python_code(pipeline: IRPipeline) -> str:
    """Generate Python code from a pipeline IR.

    Args:
        pipeline: The IRPipeline to generate code for.

    Returns:
        Complete Python code string.
    """
    lines = ['"""Generated GitLab CI pipeline."""', ""]

    # Determine imports
    imports = ["Job"]
    if pipeline.stages:
        imports.append("Pipeline")
    if any(job.rules for job in pipeline.jobs):
        imports.append("Rule")
    if any(job.artifacts for job in pipeline.jobs):
        imports.append("Artifacts")
    if any(job.cache for job in pipeline.jobs):
        imports.append("Cache")

    lines.append(f"from wetwire_gitlab.pipeline import {', '.join(sorted(imports))}")
    lines.append("")
    lines.append("")

    # Generate pipeline if stages exist
    if pipeline.stages:
        stages_str = ", ".join(f'"{s}"' for s in pipeline.stages)
        lines.append("pipeline = Pipeline(")
        lines.append(f"    stages=[{stages_str}],")
        lines.append(")")
        lines.append("")
        lines.append("")

    # Generate jobs
    for job in pipeline.jobs:
        lines.append(_generate_job(job))
        lines.append("")
        lines.append("")

    # Remove trailing empty lines
    while lines and lines[-1] == "":
        lines.pop()
    lines.append("")

    return "\n".join(lines)
