"""Pipeline linter for wetwire-gitlab.

This module provides linting functionality for Python files containing
pipeline definitions.
"""

import ast
from pathlib import Path

from ..contracts import LintResult
from .rules import (
    RULE_REGISTRY,
    WGL008FileTooLarge,
)


def _should_skip_directory(name: str) -> bool:
    """Check if a directory should be skipped during linting.

    Args:
        name: Directory name.

    Returns:
        True if the directory should be skipped.
    """
    return name == "__pycache__" or name.startswith(".")


def lint_file(
    file_path: Path,
    *,
    rules: list[str] | None = None,
    exclude_rules: list[str] | None = None,
    max_jobs: int = 10,
) -> LintResult:
    """Lint a single Python file.

    Args:
        file_path: Path to the Python file to lint.
        rules: List of rule codes to run (None = all rules).
        exclude_rules: List of rule codes to exclude.
        max_jobs: Maximum number of jobs allowed per file.

    Returns:
        LintResult with lint issues and status.
    """
    if not file_path.suffix == ".py":
        return LintResult(success=True, issues=[], files_checked=0)

    try:
        source = file_path.read_text()
        tree = ast.parse(source)
    except (SyntaxError, OSError):
        return LintResult(success=True, issues=[], files_checked=0)

    # Determine which rules to run
    rules_to_run: list[str] = []
    if rules is not None:
        rules_to_run = rules
    else:
        rules_to_run = list(RULE_REGISTRY.keys())

    if exclude_rules:
        rules_to_run = [r for r in rules_to_run if r not in exclude_rules]

    # Run each rule
    all_issues = []
    for rule_code in rules_to_run:
        if rule_code not in RULE_REGISTRY:
            continue

        rule_class = RULE_REGISTRY[rule_code]

        # Handle rules with special initialization
        if rule_class == WGL008FileTooLarge:
            rule = rule_class(max_jobs=max_jobs)
        else:
            rule = rule_class()

        issues = rule.check(tree, file_path)
        all_issues.extend(issues)

    return LintResult(
        success=len(all_issues) == 0,
        issues=all_issues,
        files_checked=1,
    )


def lint_directory(
    directory: Path,
    *,
    rules: list[str] | None = None,
    exclude_rules: list[str] | None = None,
    max_jobs: int = 10,
) -> LintResult:
    """Lint all Python files in a directory recursively.

    Args:
        directory: Path to the directory to lint.
        rules: List of rule codes to run (None = all rules).
        exclude_rules: List of rule codes to exclude.
        max_jobs: Maximum number of jobs allowed per file.

    Returns:
        LintResult with all lint issues and total files checked.
    """
    all_issues = []
    files_checked = 0

    for path in directory.rglob("*.py"):
        # Check if any parent directory should be skipped
        should_skip = False
        for parent in path.relative_to(directory).parents:
            if parent.name and _should_skip_directory(parent.name):
                should_skip = True
                break

        if should_skip:
            continue

        result = lint_file(
            path,
            rules=rules,
            exclude_rules=exclude_rules,
            max_jobs=max_jobs,
        )
        all_issues.extend(result.issues)
        files_checked += result.files_checked

    return LintResult(
        success=len(all_issues) == 0,
        issues=all_issues,
        files_checked=files_checked,
    )
