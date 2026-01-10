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


class WGL009UsePredefinedRules:
    """WGL009: Use predefined Rules constants (Rules.ON_DEFAULT_BRANCH, etc.)."""

    code = "WGL009"
    message = "Use predefined Rules constants instead of Rule with common patterns"

    # Patterns that match common rule conditions
    COMMON_PATTERNS = [
        r'\$CI_COMMIT_BRANCH\s*==\s*\$CI_DEFAULT_BRANCH',  # ON_DEFAULT_BRANCH
        r'\$CI_COMMIT_TAG',  # ON_TAG
        r'\$CI_PIPELINE_SOURCE\s*==\s*["\']merge_request_event["\']',  # ON_MERGE_REQUEST
    ]

    def check(self, tree: ast.AST, file_path: Path) -> list[LintIssue]:
        """Check for Rule() calls with common patterns that have predefined constants."""
        issues: list[LintIssue] = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                # Check for Rule(...) call with if_ keyword
                if isinstance(node.func, ast.Name) and node.func.id == "Rule":
                    for kw in node.keywords:
                        if kw.arg == "if_" and isinstance(kw.value, ast.Constant):
                            if isinstance(kw.value.value, str):
                                value = kw.value.value
                                for pattern in self.COMMON_PATTERNS:
                                    if re.search(pattern, value):
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


class WGL010UseTypedWhenConstants:
    """WGL010: Use typed When constants (When.MANUAL, When.ALWAYS, etc.)."""

    code = "WGL010"
    message = "Use typed When constants instead of string literals"

    # When values that should use constants
    WHEN_VALUES = ["manual", "always", "never", "on_success", "on_failure", "delayed"]

    def check(self, tree: ast.AST, file_path: Path) -> list[LintIssue]:
        """Check for string when values that should use When constants."""
        issues: list[LintIssue] = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                # Check for Job(...) or Rule(...) calls with when keyword
                if isinstance(node.func, ast.Name) and node.func.id in ("Job", "Rule"):
                    for kw in node.keywords:
                        if kw.arg == "when" and isinstance(kw.value, ast.Constant):
                            if isinstance(kw.value.value, str):
                                value = kw.value.value
                                if value in self.WHEN_VALUES:
                                    # Generate fix information
                                    original = f'when="{value}"'
                                    suggestion = f"when=When.{value.upper()}"
                                    issues.append(
                                        LintIssue(
                                            code=self.code,
                                            message=f"{self.message}: use When.{value.upper()} instead of '{value}'",
                                            file_path=str(file_path),
                                            line_number=kw.value.lineno,
                                            column=kw.value.col_offset,
                                            original=original,
                                            suggestion=suggestion,
                                            fix_imports=["from wetwire_gitlab.intrinsics import When"],
                                        )
                                    )

        return issues


class WGL011MissingStage:
    """WGL011: Job definitions should have an explicit stage."""

    code = "WGL011"
    message = "Job should have an explicit stage"

    def check(self, tree: ast.AST, file_path: Path) -> list[LintIssue]:
        """Check for Job() calls without stage keyword."""
        issues: list[LintIssue] = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == "Job":
                    has_stage = False
                    for kw in node.keywords:
                        if kw.arg == "stage":
                            has_stage = True
                            break
                    if not has_stage:
                        issues.append(
                            LintIssue(
                                code=self.code,
                                message=self.message,
                                file_path=str(file_path),
                                line_number=node.lineno,
                                column=node.col_offset,
                            )
                        )

        return issues


class WGL012UseCachePolicyConstants:
    """WGL012: Use typed CachePolicy constants instead of string literals."""

    code = "WGL012"
    message = "Use typed CachePolicy constants instead of string literals"

    # CachePolicy values that should use constants
    POLICY_VALUES = ["pull", "push", "pull-push"]

    def check(self, tree: ast.AST, file_path: Path) -> list[LintIssue]:
        """Check for string policy values that should use CachePolicy constants."""
        issues: list[LintIssue] = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                # Check for Cache(...) call with policy keyword
                if isinstance(node.func, ast.Name) and node.func.id == "Cache":
                    for kw in node.keywords:
                        if kw.arg == "policy" and isinstance(kw.value, ast.Constant):
                            if isinstance(kw.value.value, str):
                                value = kw.value.value
                                if value in self.POLICY_VALUES:
                                    issues.append(
                                        LintIssue(
                                            code=self.code,
                                            message=f"{self.message}: use CachePolicy.{value.upper().replace('-', '_')} instead of '{value}'",
                                            file_path=str(file_path),
                                            line_number=kw.value.lineno,
                                            column=kw.value.col_offset,
                                        )
                                    )

        return issues


class WGL013UseArtifactsWhenConstants:
    """WGL013: Use typed ArtifactsWhen constants instead of string literals."""

    code = "WGL013"
    message = "Use typed ArtifactsWhen constants instead of string literals"

    # ArtifactsWhen values that should use constants
    WHEN_VALUES = ["on_success", "on_failure", "always"]

    def check(self, tree: ast.AST, file_path: Path) -> list[LintIssue]:
        """Check for string when values in Artifacts that should use ArtifactsWhen constants."""
        issues: list[LintIssue] = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                # Check for Artifacts(...) call with when keyword
                if isinstance(node.func, ast.Name) and node.func.id == "Artifacts":
                    for kw in node.keywords:
                        if kw.arg == "when" and isinstance(kw.value, ast.Constant):
                            if isinstance(kw.value.value, str):
                                value = kw.value.value
                                if value in self.WHEN_VALUES:
                                    issues.append(
                                        LintIssue(
                                            code=self.code,
                                            message=f"{self.message}: use ArtifactsWhen.{value.upper()} instead of '{value}'",
                                            file_path=str(file_path),
                                            line_number=kw.value.lineno,
                                            column=kw.value.col_offset,
                                        )
                                    )

        return issues


class WGL014MissingScript:
    """WGL014: Job should have script, trigger, or extends."""

    code = "WGL014"
    message = "Job should have script, trigger, or extends"

    def check(self, tree: ast.AST, file_path: Path) -> list[LintIssue]:
        """Check for Job() calls without script, trigger, or extends."""
        issues: list[LintIssue] = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == "Job":
                    has_script = False
                    has_trigger = False
                    has_extends = False
                    for kw in node.keywords:
                        if kw.arg == "script":
                            has_script = True
                        elif kw.arg == "trigger":
                            has_trigger = True
                        elif kw.arg == "extends":
                            has_extends = True
                    if not has_script and not has_trigger and not has_extends:
                        issues.append(
                            LintIssue(
                                code=self.code,
                                message=self.message,
                                file_path=str(file_path),
                                line_number=node.lineno,
                                column=node.col_offset,
                            )
                        )

        return issues


class WGL015MissingName:
    """WGL015: Job should have explicit name."""

    code = "WGL015"
    message = "Job should have explicit name"

    def check(self, tree: ast.AST, file_path: Path) -> list[LintIssue]:
        """Check for Job() calls without name keyword."""
        issues: list[LintIssue] = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == "Job":
                    has_name = False
                    for kw in node.keywords:
                        if kw.arg == "name":
                            has_name = True
                            break
                    if not has_name:
                        issues.append(
                            LintIssue(
                                code=self.code,
                                message=self.message,
                                file_path=str(file_path),
                                line_number=node.lineno,
                                column=node.col_offset,
                            )
                        )

        return issues


class WGL016UseImageDataclass:
    """WGL016: Use Image dataclass instead of string."""

    code = "WGL016"
    message = "Use Image dataclass instead of string literal"

    def check(self, tree: ast.AST, file_path: Path) -> list[LintIssue]:
        """Check for string image values that should use Image dataclass."""
        issues: list[LintIssue] = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                # Check for Job(...) call with image keyword containing string
                if isinstance(node.func, ast.Name) and node.func.id == "Job":
                    for kw in node.keywords:
                        if kw.arg == "image" and isinstance(kw.value, ast.Constant):
                            if isinstance(kw.value.value, str):
                                issues.append(
                                    LintIssue(
                                        code=self.code,
                                        message=f"{self.message}: use Image(name=\"{kw.value.value}\")",
                                        file_path=str(file_path),
                                        line_number=kw.value.lineno,
                                        column=kw.value.col_offset,
                                    )
                                )

        return issues


class WGL017EmptyRulesList:
    """WGL017: Empty rules list means job never runs."""

    code = "WGL017"
    message = "Empty rules list means job never runs"

    def check(self, tree: ast.AST, file_path: Path) -> list[LintIssue]:
        """Check for empty rules list in Job definitions."""
        issues: list[LintIssue] = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                # Check for Job(...) call with rules=[]
                if isinstance(node.func, ast.Name) and node.func.id == "Job":
                    for kw in node.keywords:
                        if kw.arg == "rules" and isinstance(kw.value, ast.List):
                            if len(kw.value.elts) == 0:
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


class WGL018NeedsWithoutStage:
    """WGL018: Jobs with needs should specify stage."""

    code = "WGL018"
    message = "Jobs with needs should specify stage for clarity"

    def check(self, tree: ast.AST, file_path: Path) -> list[LintIssue]:
        """Check for Job() calls with needs but without stage."""
        issues: list[LintIssue] = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == "Job":
                    has_needs = False
                    has_stage = False
                    for kw in node.keywords:
                        if kw.arg == "needs":
                            has_needs = True
                        elif kw.arg == "stage":
                            has_stage = True
                    if has_needs and not has_stage:
                        issues.append(
                            LintIssue(
                                code=self.code,
                                message=self.message,
                                file_path=str(file_path),
                                line_number=node.lineno,
                                column=node.col_offset,
                            )
                        )

        return issues


class WGL019ManualWithoutAllowFailure:
    """WGL019: Manual jobs should consider allow_failure."""

    code = "WGL019"
    message = "Manual jobs should consider allow_failure to avoid blocking pipelines"

    def check(self, tree: ast.AST, file_path: Path) -> list[LintIssue]:
        """Check for manual jobs without allow_failure."""
        issues: list[LintIssue] = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == "Job":
                    is_manual = False
                    has_allow_failure = False
                    when_lineno = 0
                    when_col = 0

                    for kw in node.keywords:
                        if kw.arg == "when":
                            # Check for string "manual"
                            if isinstance(kw.value, ast.Constant):
                                if kw.value.value == "manual":
                                    is_manual = True
                                    when_lineno = kw.value.lineno
                                    when_col = kw.value.col_offset
                            # Check for When.MANUAL attribute access
                            elif isinstance(kw.value, ast.Attribute):
                                if kw.value.attr == "MANUAL":
                                    is_manual = True
                                    when_lineno = kw.value.lineno
                                    when_col = kw.value.col_offset
                        elif kw.arg == "allow_failure":
                            has_allow_failure = True

                    if is_manual and not has_allow_failure:
                        issues.append(
                            LintIssue(
                                code=self.code,
                                message=self.message,
                                file_path=str(file_path),
                                line_number=when_lineno or node.lineno,
                                column=when_col or node.col_offset,
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
    WGL009UsePredefinedRules,
    WGL010UseTypedWhenConstants,
    WGL011MissingStage,
    WGL012UseCachePolicyConstants,
    WGL013UseArtifactsWhenConstants,
    WGL014MissingScript,
    WGL015MissingName,
    WGL016UseImageDataclass,
    WGL017EmptyRulesList,
    WGL018NeedsWithoutStage,
    WGL019ManualWithoutAllowFailure,
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
    "WGL009": WGL009UsePredefinedRules,
    "WGL010": WGL010UseTypedWhenConstants,
    "WGL011": WGL011MissingStage,
    "WGL012": WGL012UseCachePolicyConstants,
    "WGL013": WGL013UseArtifactsWhenConstants,
    "WGL014": WGL014MissingScript,
    "WGL015": WGL015MissingName,
    "WGL016": WGL016UseImageDataclass,
    "WGL017": WGL017EmptyRulesList,
    "WGL018": WGL018NeedsWithoutStage,
    "WGL019": WGL019ManualWithoutAllowFailure,
}
