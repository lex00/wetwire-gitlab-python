"""Rules configuration for GitLab CI jobs."""

from dataclasses import dataclass


@dataclass
class Rule:
    """Rule configuration for conditional job execution.

    Attributes:
        if_: Condition expression (uses if_ to avoid Python keyword conflict).
        changes: List of file patterns that trigger the rule.
        exists: List of file patterns that must exist.
        when: What to do when rule matches (on_success, manual, delayed, never).
        allow_failure: Allow the job to fail without failing the pipeline.
        variables: Variables to set when rule matches.
        start_in: Delay before running (for delayed jobs).
        needs: Job dependencies when rule matches.
    """

    if_: str | None = None
    changes: list[str] | None = None
    exists: list[str] | None = None
    when: str | None = None
    allow_failure: bool | None = None
    variables: dict[str, str] | None = None
    start_in: str | None = None
    needs: list[str] | None = None
