"""YAML serialization functions."""

from typing import Any

import yaml

from wetwire_gitlab.pipeline import Job, Pipeline

from .converter import to_dict


def to_yaml(obj: Any) -> str:
    """Convert a dataclass to YAML string.

    Args:
        obj: A dataclass instance.

    Returns:
        YAML string representation.
    """
    data = to_dict(obj)
    return yaml.dump(data, default_flow_style=False, sort_keys=False, allow_unicode=True)


def build_pipeline_yaml(pipeline: Pipeline, jobs: list[Job]) -> str:
    """Build a complete GitLab CI pipeline YAML.

    Creates a properly structured .gitlab-ci.yml with:
    - Pipeline-level configuration (stages, workflow, includes, default, variables)
    - All jobs with their names as YAML keys

    Args:
        pipeline: Pipeline configuration.
        jobs: List of Job instances.

    Returns:
        Complete YAML string for .gitlab-ci.yml.
    """
    result: dict[str, Any] = {}

    # Add pipeline-level configuration
    pipeline_dict = to_dict(pipeline)

    # Add stages first if present
    if "stages" in pipeline_dict:
        result["stages"] = pipeline_dict["stages"]

    # Add workflow if present
    if "workflow" in pipeline_dict:
        result["workflow"] = pipeline_dict["workflow"]

    # Add include if present
    if "include" in pipeline_dict:
        result["include"] = pipeline_dict["include"]

    # Add default if present
    if "default" in pipeline_dict:
        result["default"] = pipeline_dict["default"]

    # Add variables if present
    if "variables" in pipeline_dict:
        result["variables"] = pipeline_dict["variables"]

    # Add cache if present
    if "cache" in pipeline_dict:
        result["cache"] = pipeline_dict["cache"]

    # Add services if present
    if "services" in pipeline_dict:
        result["services"] = pipeline_dict["services"]

    # Add jobs
    for job in jobs:
        job_dict = to_dict(job)
        result[job.name] = job_dict

    return yaml.dump(result, default_flow_style=False, sort_keys=False, allow_unicode=True)
