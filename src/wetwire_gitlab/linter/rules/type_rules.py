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

    # Patterns that should be handled by WGL009 instead
    WGL009_PATTERNS = [
        r'^\$CI_COMMIT_BRANCH\s*==\s*\$CI_DEFAULT_BRANCH$',
        r'^\$CI_COMMIT_TAG$',
        r'^\$CI_PIPELINE_SOURCE\s*==\s*["\']merge_request_event["\']$',
    ]

    # Map of CI variable strings to their intrinsic equivalents
    CI_VAR_MAP = {
        "$CI_COMMIT_SHA": "CI.COMMIT_SHA",
        "$CI_COMMIT_SHORT_SHA": "CI.COMMIT_SHORT_SHA",
        "$CI_COMMIT_REF_NAME": "CI.COMMIT_REF_NAME",
        "$CI_COMMIT_REF_SLUG": "CI.COMMIT_REF_SLUG",
        "$CI_COMMIT_BRANCH": "CI.COMMIT_BRANCH",
        "$CI_COMMIT_TAG": "CI.COMMIT_TAG",
        "$CI_COMMIT_MESSAGE": "CI.COMMIT_MESSAGE",
        "$CI_COMMIT_TITLE": "CI.COMMIT_TITLE",
        "$CI_COMMIT_BEFORE_SHA": "CI.COMMIT_BEFORE_SHA",
        "$CI_DEFAULT_BRANCH": "CI.DEFAULT_BRANCH",
        "$CI_PIPELINE_ID": "CI.PIPELINE_ID",
        "$CI_PIPELINE_IID": "CI.PIPELINE_IID",
        "$CI_PIPELINE_SOURCE": "CI.PIPELINE_SOURCE",
        "$CI_PIPELINE_URL": "CI.PIPELINE_URL",
        "$CI_JOB_ID": "CI.JOB_ID",
        "$CI_JOB_NAME": "CI.JOB_NAME",
        "$CI_JOB_STAGE": "CI.JOB_STAGE",
        "$CI_JOB_TOKEN": "CI.JOB_TOKEN",
        "$CI_JOB_URL": "CI.JOB_URL",
        "$CI_PROJECT_ID": "CI.PROJECT_ID",
        "$CI_PROJECT_NAME": "CI.PROJECT_NAME",
        "$CI_PROJECT_NAMESPACE": "CI.PROJECT_NAMESPACE",
        "$CI_PROJECT_PATH": "CI.PROJECT_PATH",
        "$CI_PROJECT_PATH_SLUG": "CI.PROJECT_PATH_SLUG",
        "$CI_PROJECT_URL": "CI.PROJECT_URL",
        "$CI_PROJECT_DIR": "CI.PROJECT_DIR",
        "$CI_REGISTRY": "CI.REGISTRY",
        "$CI_REGISTRY_IMAGE": "CI.REGISTRY_IMAGE",
        "$CI_REGISTRY_USER": "CI.REGISTRY_USER",
        "$CI_REGISTRY_PASSWORD": "CI.REGISTRY_PASSWORD",
        "$CI_SERVER_HOST": "CI.SERVER_HOST",
        "$CI_SERVER_URL": "CI.SERVER_URL",
        "$CI_ENVIRONMENT_NAME": "CI.ENVIRONMENT_NAME",
        "$CI_ENVIRONMENT_SLUG": "CI.ENVIRONMENT_SLUG",
        "$CI_ENVIRONMENT_URL": "CI.ENVIRONMENT_URL",
    }

    def check(self, tree: ast.AST, file_path: Path) -> list[LintIssue]:
        """Check for raw CI variable strings."""
        issues: list[LintIssue] = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == "Rule":
                    for kw in node.keywords:
                        if kw.arg == "if_" and isinstance(kw.value, ast.Constant):
                            if isinstance(kw.value.value, str):
                                original_value = kw.value.value

                                # Skip if this pattern should be handled by WGL009
                                skip_for_wgl009 = False
                                for pattern in self.WGL009_PATTERNS:
                                    if re.search(pattern, original_value):
                                        skip_for_wgl009 = True
                                        break

                                if skip_for_wgl009:
                                    continue

                                if self.CI_VARIABLE_PATTERN.search(original_value):
                                    # Handle simple cases where entire value is just a variable
                                    if original_value in self.CI_VAR_MAP:
                                        suggestion_value = self.CI_VAR_MAP[original_value]
                                    else:
                                        # Build complex expression with string concatenation
                                        # Replace CI variables with Python expressions
                                        suggestion_parts = []
                                        remaining = original_value

                                        while remaining:
                                            # Find the next CI variable
                                            match = self.CI_VARIABLE_PATTERN.search(remaining)
                                            if match:
                                                # Add the part before the variable as a string literal
                                                before = remaining[:match.start()]
                                                if before:
                                                    suggestion_parts.append(f'"{before}"')

                                                # Add the CI variable as a Python expression
                                                ci_var = match.group()
                                                if ci_var in self.CI_VAR_MAP:
                                                    suggestion_parts.append(self.CI_VAR_MAP[ci_var])
                                                else:
                                                    # Unknown variable, keep as is
                                                    suggestion_parts.append(f'"{ci_var}"')

                                                # Continue with the rest
                                                remaining = remaining[match.end():]
                                            else:
                                                # No more variables, add the rest as a string literal
                                                if remaining:
                                                    suggestion_parts.append(f'"{remaining}"')
                                                break

                                        # Join parts with +
                                        suggestion_value = " + ".join(suggestion_parts)

                                    # Build the original and suggestion strings
                                    # For complex strings with nested quotes, we need to handle both quote styles
                                    # If the value contains double quotes, it's likely single-quoted in source
                                    # If the value contains single quotes, it's likely double-quoted in source
                                    if '"' in original_value and "'" not in original_value:
                                        # Value has double quotes, use single quotes for outer
                                        original = f"if_='{original_value}'"
                                    elif "'" in original_value and '"' not in original_value:
                                        # Value has single quotes, use double quotes for outer
                                        original = f'if_="{original_value}"'
                                    else:
                                        # Either has both or neither, try double quotes first
                                        original = f'if_="{original_value}"'

                                    suggestion = f"if_={suggestion_value}"

                                    issues.append(
                                        LintIssue(
                                            code=self.code,
                                            message=f"{self.message}: replace with intrinsics",
                                            file_path=str(file_path),
                                            line_number=kw.value.lineno,
                                            column=kw.value.col_offset,
                                            original=original,
                                            suggestion=suggestion,
                                            fix_imports=["from wetwire_gitlab.intrinsics import CI"],
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


class WGL021UseTypedServiceConstants:
    """WGL021: Use typed Service constants instead of raw strings."""

    code = "WGL021"
    message = "Use Service dataclass instead of string literal"

    def check(self, tree: ast.AST, file_path: Path) -> list[LintIssue]:
        """Check for string service values that should use Service dataclass."""
        issues: list[LintIssue] = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == "Job":
                    for kw in node.keywords:
                        if kw.arg == "services" and isinstance(kw.value, ast.List):
                            # Check each element in the services list
                            for elt in kw.value.elts:
                                if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                                    issues.append(
                                        LintIssue(
                                            code=self.code,
                                            message=f"{self.message}: use Service(name=\"{elt.value}\")",
                                            file_path=str(file_path),
                                            line_number=elt.lineno,
                                            column=elt.col_offset,
                                        )
                                    )

        return issues
