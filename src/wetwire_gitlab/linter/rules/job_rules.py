"""Job validation rules.

These rules check for common issues in Job definitions, such as missing
required fields or potentially problematic configurations.
"""

import ast
from pathlib import Path

from ...contracts import LintIssue


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


class WGL017EmptyRulesList:
    """WGL017: Empty rules list means job never runs."""

    code = "WGL017"
    message = "Empty rules list means job never runs"

    def check(self, tree: ast.AST, file_path: Path) -> list[LintIssue]:
        """Check for empty rules list in Job definitions."""
        issues: list[LintIssue] = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
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
