"""Pattern-based rules for using predefined constants.

These rules encourage using predefined patterns like Rules.ON_DEFAULT_BRANCH
and When.MANUAL instead of manually constructing common patterns.
"""

import ast
import re
from pathlib import Path

from ...contracts import LintIssue


class WGL009UsePredefinedRules:
    """WGL009: Use predefined Rules constants (Rules.ON_DEFAULT_BRANCH, etc.)."""

    code = "WGL009"
    message = "Use predefined Rules constants instead of Rule with common patterns"

    # Patterns that match common rule conditions with their replacements
    PATTERN_MAP = [
        (r'^\$CI_COMMIT_BRANCH\s*==\s*\$CI_DEFAULT_BRANCH$', 'Rules.ON_DEFAULT_BRANCH', 'ON_DEFAULT_BRANCH'),
        (r'^\$CI_COMMIT_TAG$', 'Rules.ON_TAG', 'ON_TAG'),
        (r'^\$CI_PIPELINE_SOURCE\s*==\s*["\']merge_request_event["\']$', 'Rules.ON_MERGE_REQUEST', 'ON_MERGE_REQUEST'),
    ]

    def check(self, tree: ast.AST, file_path: Path) -> list[LintIssue]:
        """Check for Rule() calls with common patterns that have predefined constants."""
        issues: list[LintIssue] = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == "Rule":
                    for kw in node.keywords:
                        if kw.arg == "if_" and isinstance(kw.value, ast.Constant):
                            if isinstance(kw.value.value, str):
                                value = kw.value.value
                                for pattern, replacement, rule_name in self.PATTERN_MAP:
                                    if re.search(pattern, value):
                                        # Generate fix information
                                        # Handle quote styles - if value contains double quotes, use single quotes
                                        if '"' in value and "'" not in value:
                                            original = f"Rule(if_='{value}')"
                                        elif "'" in value and '"' not in value:
                                            original = f'Rule(if_="{value}")'
                                        else:
                                            # Default to double quotes
                                            original = f'Rule(if_="{value}")'

                                        suggestion = replacement

                                        issues.append(
                                            LintIssue(
                                                code=self.code,
                                                message=f"{self.message}: use {replacement}",
                                                file_path=str(file_path),
                                                line_number=node.lineno,
                                                column=node.col_offset,
                                                original=original,
                                                suggestion=suggestion,
                                                fix_imports=["from wetwire_gitlab.intrinsics import Rules"],
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
