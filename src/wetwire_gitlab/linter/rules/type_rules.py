"""Type safety rules for using typed constants and dataclasses.

These rules encourage using typed constructs instead of raw dicts or strings.
"""

import ast
import re
from pathlib import Path

from ...contracts import LintIssue


class WGL001TypedComponentWrappers:
    """WGL001: Use typed component wrappers instead of raw Include(component=...)."""

    code = "WGL001"
    message = "Use typed component wrappers instead of raw Include(component=...)"

    def check(self, tree: ast.AST, file_path: Path) -> list[LintIssue]:
        """Check for raw Include(component=...) usage."""
        issues: list[LintIssue] = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
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

    CI_VARIABLE_PATTERN = re.compile(r"\$CI_[A-Z_]+")

    def check(self, tree: ast.AST, file_path: Path) -> list[LintIssue]:
        """Check for raw CI variable strings."""
        issues: list[LintIssue] = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
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
        return []


class WGL012UseCachePolicyConstants:
    """WGL012: Use typed CachePolicy constants instead of string literals."""

    code = "WGL012"
    message = "Use typed CachePolicy constants instead of string literals"

    POLICY_VALUES = ["pull", "push", "pull-push"]

    def check(self, tree: ast.AST, file_path: Path) -> list[LintIssue]:
        """Check for string policy values that should use CachePolicy constants."""
        issues: list[LintIssue] = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == "Cache":
                    for kw in node.keywords:
                        if kw.arg == "policy" and isinstance(kw.value, ast.Constant):
                            if isinstance(kw.value.value, str):
                                value = kw.value.value
                                if value in self.POLICY_VALUES:
                                    # Generate fix information
                                    original = f'policy="{value}"'
                                    suggestion = f"policy=CachePolicy.{value.upper().replace('-', '_')}"
                                    issues.append(
                                        LintIssue(
                                            code=self.code,
                                            message=f"{self.message}: use CachePolicy.{value.upper().replace('-', '_')} instead of '{value}'",
                                            file_path=str(file_path),
                                            line_number=kw.value.lineno,
                                            column=kw.value.col_offset,
                                            original=original,
                                            suggestion=suggestion,
                                            fix_imports=["from wetwire_gitlab.intrinsics import CachePolicy"],
                                        )
                                    )

        return issues


class WGL013UseArtifactsWhenConstants:
    """WGL013: Use typed ArtifactsWhen constants instead of string literals."""

    code = "WGL013"
    message = "Use typed ArtifactsWhen constants instead of string literals"

    WHEN_VALUES = ["on_success", "on_failure", "always"]

    def check(self, tree: ast.AST, file_path: Path) -> list[LintIssue]:
        """Check for string when values in Artifacts that should use ArtifactsWhen constants."""
        issues: list[LintIssue] = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == "Artifacts":
                    for kw in node.keywords:
                        if kw.arg == "when" and isinstance(kw.value, ast.Constant):
                            if isinstance(kw.value.value, str):
                                value = kw.value.value
                                if value in self.WHEN_VALUES:
                                    # Generate fix information
                                    original = f'when="{value}"'
                                    suggestion = f"when=ArtifactsWhen.{value.upper()}"
                                    issues.append(
                                        LintIssue(
                                            code=self.code,
                                            message=f"{self.message}: use ArtifactsWhen.{value.upper()} instead of '{value}'",
                                            file_path=str(file_path),
                                            line_number=kw.value.lineno,
                                            column=kw.value.col_offset,
                                            original=original,
                                            suggestion=suggestion,
                                            fix_imports=["from wetwire_gitlab.intrinsics import ArtifactsWhen"],
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
