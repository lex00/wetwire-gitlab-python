"""Include configuration for GitLab CI pipelines."""

from dataclasses import dataclass
from typing import Any


@dataclass
class Include:
    """Include configuration for external CI configurations.

    GitLab supports 6 types of includes:
    - local: Include a file from the same repository
    - remote: Include a file from a URL
    - template: Include a GitLab-provided template
    - project: Include a file from another project
    - component: Include a CI/CD component

    Attributes:
        local: Path to local file in the repository.
        remote: URL to remote file.
        template: Name of GitLab template.
        project: Project path for project includes.
        file: File path within the project (for project includes).
        ref: Git ref for project includes.
        component: Component reference (e.g., "gitlab.com/components/sast@1.0.0").
        inputs: Inputs for component includes.
        rules: Rules for conditional includes.
    """

    local: str | None = None
    remote: str | None = None
    template: str | None = None
    project: str | None = None
    file: str | None = None
    ref: str | None = None
    component: str | None = None
    inputs: dict[str, Any] | None = None
    rules: list[Any] | None = None
