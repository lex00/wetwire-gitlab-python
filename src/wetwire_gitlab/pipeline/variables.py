"""Variables configuration for GitLab CI pipelines."""

from dataclasses import dataclass, field


@dataclass
class Variable:
    """A single variable with optional description and options.

    Attributes:
        value: The variable value.
        description: Description for the variable (shown in UI for manual pipelines).
        options: List of allowed values for the variable.
        expand: Whether to expand the variable value.
    """

    value: str
    description: str | None = None
    options: list[str] | None = None
    expand: bool | None = None


@dataclass
class Variables:
    """Variables configuration for a pipeline or job.

    Attributes:
        variables: Dictionary of variable name to value or Variable object.
    """

    variables: dict[str, str | Variable] = field(default_factory=dict)
