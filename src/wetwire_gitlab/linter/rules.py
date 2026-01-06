"""Lint rules for pipeline definitions.

This module defines individual lint rules that check for common
issues in pipeline definitions.
"""

import ast
import re
from pathlib import Path
from typing import Protocol

from ..contracts import LintIssue


class LintRule(Protocol):
    """Protocol for lint rules."""

    code: str
    message: str

    def check(self, tree: ast.AST, file_path: Path) -> list[LintIssue]:
        """Check the AST for violations.

        Args:
            tree: Parsed AST of the Python file.
            file_path: Path to the file being checked.

        Returns:
            List of lint issues found.
        """
        ...


class WGL001TypedComponentWrappers:
    """WGL001: Use typed component wrappers instead of raw Include(component=...)."""

    code = "WGL001"
    message = "Use typed component wrappers instead of raw Include(component=...)"

    def check(self, tree: ast.AST, file_path: Path) -> list[LintIssue]:
        """Check for raw Include(component=...) usage."""
        issues: list[LintIssue] = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                # Check for Include(...) call with component keyword
                if isinstance(node.func, ast.Name) and node.func.id == "Include":
                    for kw in node.keywords:
                        if kw.arg == "component":
                            issues.append(
                                LintIssue(
                                    code=self.code,
                                    message=self.message,
                                    file_path=str(file_path),
                                    line_number=node.lineno,
                                    column=node.col_offset,
                                )
                            )
                            break

        return issues


class WGL002UseRuleDataclass:
    """WGL002: Use Rule dataclass instead of raw dict for rules."""

    code = "WGL002"
    message = "Use Rule dataclass instead of raw dict for rules"

    def check(self, tree: ast.AST, file_path: Path) -> list[LintIssue]:
        """Check for raw dict usage in rules keyword."""
        issues: list[LintIssue] = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                # Check for Job(...) call with rules keyword containing dicts
                if isinstance(node.func, ast.Name) and node.func.id == "Job":
                    for kw in node.keywords:
                        if kw.arg == "rules" and isinstance(kw.value, ast.List):
                            for elt in kw.value.elts:
                                if isinstance(elt, ast.Dict):
                                    issues.append(
                                        LintIssue(
                                            code=self.code,
                                            message=self.message,
                                            file_path=str(file_path),
                                            line_number=elt.lineno,
                                            column=elt.col_offset,
                                        )
                                    )

        return issues


class WGL003UsePredefinedVariables:
    """WGL003: Use predefined variables from intrinsics module."""

    code = "WGL003"
    message = "Use predefined variables from intrinsics module instead of raw strings"

    # Pattern to detect CI/CD variables in strings
    CI_VARIABLE_PATTERN = re.compile(r"\$CI_[A-Z_]+")

    def check(self, tree: ast.AST, file_path: Path) -> list[LintIssue]:
        """Check for raw CI variable strings."""
        issues: list[LintIssue] = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                # Check for Rule(...) call with if_ containing CI variables
                if isinstance(node.func, ast.Name) and node.func.id == "Rule":
                    for kw in node.keywords:
                        if kw.arg == "if_" and isinstance(kw.value, ast.Constant):
                            if isinstance(kw.value.value, str):
                                if self.CI_VARIABLE_PATTERN.search(kw.value.value):
                                    issues.append(
                                        LintIssue(
                                            code=self.code,
                                            message=self.message,
                                            file_path=str(file_path),
                                            line_number=kw.value.lineno,
                                            column=kw.value.col_offset,
                                        )
                                    )

        return issues


class WGL004UseCacheDataclass:
    """WGL004: Use Cache dataclass instead of raw dict for cache."""

    code = "WGL004"
    message = "Use Cache dataclass instead of raw dict for cache"

    def check(self, tree: ast.AST, file_path: Path) -> list[LintIssue]:
        """Check for raw dict usage in cache keyword."""
        issues: list[LintIssue] = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                # Check for Job(...) call with cache keyword containing dict
                if isinstance(node.func, ast.Name) and node.func.id == "Job":
                    for kw in node.keywords:
                        if kw.arg == "cache" and isinstance(kw.value, ast.Dict):
                            issues.append(
                                LintIssue(
                                    code=self.code,
                                    message=self.message,
                                    file_path=str(file_path),
                                    line_number=kw.value.lineno,
                                    column=kw.value.col_offset,
                                )
                            )

        return issues


class WGL005UseArtifactsDataclass:
    """WGL005: Use Artifacts dataclass instead of raw dict for artifacts."""

    code = "WGL005"
    message = "Use Artifacts dataclass instead of raw dict for artifacts"

    def check(self, tree: ast.AST, file_path: Path) -> list[LintIssue]:
        """Check for raw dict usage in artifacts keyword."""
        issues: list[LintIssue] = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                # Check for Job(...) call with artifacts keyword containing dict
                if isinstance(node.func, ast.Name) and node.func.id == "Job":
                    for kw in node.keywords:
                        if kw.arg == "artifacts" and isinstance(kw.value, ast.Dict):
                            issues.append(
                                LintIssue(
                                    code=self.code,
                                    message=self.message,
                                    file_path=str(file_path),
                                    line_number=kw.value.lineno,
                                    column=kw.value.col_offset,
                                )
                            )

        return issues


class WGL006UseTypedStageConstants:
    """WGL006: Use typed stage constants (placeholder for future Stage enum)."""

    code = "WGL006"
    message = "Consider using typed stage constants"

    def check(self, tree: ast.AST, file_path: Path) -> list[LintIssue]:
        """Check for string stage values (disabled by default)."""
        # This rule is currently a no-op since Stage enum doesn't exist yet
        # When implemented, it would check for raw string stages like "build", "test"
        return []


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


# All available rules
ALL_RULES: list[type] = [
    WGL001TypedComponentWrappers,
    WGL002UseRuleDataclass,
    WGL003UsePredefinedVariables,
    WGL004UseCacheDataclass,
    WGL005UseArtifactsDataclass,
    WGL006UseTypedStageConstants,
    WGL007DuplicateJobNames,
    WGL008FileTooLarge,
]

# Rule code to class mapping
RULE_REGISTRY: dict[str, type] = {
    "WGL001": WGL001TypedComponentWrappers,
    "WGL002": WGL002UseRuleDataclass,
    "WGL003": WGL003UsePredefinedVariables,
    "WGL004": WGL004UseCacheDataclass,
    "WGL005": WGL005UseArtifactsDataclass,
    "WGL006": WGL006UseTypedStageConstants,
    "WGL007": WGL007DuplicateJobNames,
    "WGL008": WGL008FileTooLarge,
}
