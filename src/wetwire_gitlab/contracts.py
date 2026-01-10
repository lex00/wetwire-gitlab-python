"""Contracts and protocols for wetwire-gitlab."""

from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable


@dataclass
class JobRef:
    """Reference to another job for needs/dependencies.

    Attributes:
        job: The job name to reference.
        artifacts: Whether to download artifacts from this job.
    """

    job: str
    artifacts: bool = False

    def to_dict(self) -> str | dict[str, Any]:
        """Serialize to GitLab CI needs format.

        Returns:
            String job name if no artifacts, otherwise dict with job and artifacts.
        """
        if self.artifacts:
            return {"job": self.job, "artifacts": True}
        return self.job

    def is_empty(self) -> bool:
        """Check if this is an empty reference.

        Returns:
            True if the job name is empty.
        """
        return self.job == ""


@dataclass
class DiscoveredJob:
    """A job discovered through AST analysis.

    Attributes:
        name: The job name (from Job.name field).
        variable_name: The Python variable name.
        file_path: Path to the file containing the job.
        line_number: Line number where the job is defined.
        dependencies: List of variable names this job depends on.
        stage: The job stage (optional).
        variables: Dictionary of job variables (optional).
        when: The when condition (optional).
    """

    name: str
    variable_name: str
    file_path: str
    line_number: int
    dependencies: list[str] | None = None
    stage: str | None = None
    variables: dict[str, str] | None = None
    when: str | None = None


@dataclass
class DiscoveredPipeline:
    """A pipeline discovered through AST analysis.

    Attributes:
        name: The pipeline name.
        file_path: Path to the file containing the pipeline.
        jobs: List of job names in this pipeline.
    """

    name: str
    file_path: str
    jobs: list[str] = field(default_factory=list)


@dataclass
class BuildResult:
    """Result of a build operation.

    Attributes:
        success: Whether the build succeeded.
        output_path: Path to the generated file.
        jobs_count: Number of jobs in the generated pipeline.
        errors: List of error messages if any.
    """

    success: bool
    output_path: str | None
    jobs_count: int
    errors: list[str] | None = None


@dataclass
class LintIssue:
    """A single lint issue.

    Attributes:
        code: The rule code (e.g., "WGL001").
        message: Description of the issue.
        file_path: Path to the file with the issue.
        line_number: Line number of the issue.
        column: Column number of the issue.
        severity: Issue severity (error, warning, info).
        original: Original code to replace (for auto-fix).
        suggestion: Suggested fix code (for auto-fix).
        fix_imports: List of import statements needed for the fix.
        insert_after_line: Line number to insert suggestion after (for insertions).
    """

    code: str
    message: str
    file_path: str
    line_number: int
    column: int | None = None
    severity: str = "error"
    original: str | None = None
    suggestion: str | None = None
    fix_imports: list[str] | None = None
    insert_after_line: int | None = None


@dataclass
class LintResult:
    """Result of a lint operation.

    Attributes:
        success: Whether linting passed (no errors).
        issues: List of lint issues found.
        files_checked: Number of files checked.
    """

    success: bool
    issues: list[LintIssue]
    files_checked: int


@dataclass
class ValidateResult:
    """Result of a validation operation.

    Attributes:
        valid: Whether the pipeline is valid.
        errors: List of validation errors.
        merged_yaml: The merged YAML after processing includes.
    """

    valid: bool
    errors: list[str] | None = None
    merged_yaml: str | None = None


@dataclass
class ListResult:
    """Result of a list operation.

    Attributes:
        jobs: List of discovered jobs.
        pipelines: List of discovered pipelines.
    """

    jobs: list[DiscoveredJob]
    pipelines: list[DiscoveredPipeline]


@runtime_checkable
class Resource(Protocol):
    """Protocol for resources that can be serialized."""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for YAML serialization."""
        ...
