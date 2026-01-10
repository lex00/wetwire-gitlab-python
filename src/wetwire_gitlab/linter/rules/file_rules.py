"""File-level lint rules.

These rules check for issues at the file level, such as duplicate job names
or too many jobs in a single file.
"""

import ast
from pathlib import Path

from ...contracts import LintIssue


class WGL007DuplicateJobNames:
    """WGL007: Detect duplicate job names in the same file."""

    code = "WGL007"
    message = "Duplicate job name detected"

    def check(self, tree: ast.AST, file_path: Path) -> list[LintIssue]:
        """Check for duplicate job names."""
        issues: list[LintIssue] = []
        job_names: dict[str, int] = {}  # name -> first line number

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == "Job":
                    for kw in node.keywords:
                        if kw.arg == "name" and isinstance(kw.value, ast.Constant):
                            name = kw.value.value
                            if isinstance(name, str):
                                if name in job_names:
                                    issues.append(
                                        LintIssue(
                                            code=self.code,
                                            message=f"{self.message}: '{name}'",
                                            file_path=str(file_path),
                                            line_number=node.lineno,
                                            column=node.col_offset,
                                        )
                                    )
                                else:
                                    job_names[name] = node.lineno

        return issues


class WGL008FileTooLarge:
    """WGL008: File contains too many jobs."""

    code = "WGL008"
    message = "File contains too many jobs"

    def __init__(self, max_jobs: int = 10):
        """Initialize with maximum job count.

        Args:
            max_jobs: Maximum number of jobs allowed per file.
        """
        self.max_jobs = max_jobs

    def check(self, tree: ast.AST, file_path: Path) -> list[LintIssue]:
        """Check for too many jobs in a file."""
        issues: list[LintIssue] = []
        job_count = 0

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == "Job":
                    job_count += 1

        if job_count > self.max_jobs:
            issues.append(
                LintIssue(
                    code=self.code,
                    message=f"{self.message}: {job_count} jobs (max {self.max_jobs})",
                    file_path=str(file_path),
                    line_number=1,
                    column=0,
                )
            )

        return issues
