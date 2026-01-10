"""Pipeline linter for wetwire-gitlab.

This module provides linting functionality for Python files containing
pipeline definitions.
"""

import ast
from pathlib import Path

from ..contracts import LintIssue, LintResult
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


def lint_code(
    source: str,
    *,
    filename: str = "<string>",
    rules: list[str] | None = None,
    exclude_rules: list[str] | None = None,
    max_jobs: int = 10,
) -> list[LintIssue]:
    """Lint Python source code.

    Args:
        source: The Python source code to lint.
        filename: Optional filename for context.
        rules: List of rule codes to run (None = all rules).
        exclude_rules: List of rule codes to exclude.
        max_jobs: Maximum number of jobs allowed per file.

    Returns:
        List of LintIssue objects.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []

    # Determine which rules to run
    rules_to_run: list[str] = []
    if rules is not None:
        rules_to_run = rules
    else:
        rules_to_run = list(RULE_REGISTRY.keys())

    if exclude_rules:
        rules_to_run = [r for r in rules_to_run if r not in exclude_rules]

    # Run each rule
    all_issues: list[LintIssue] = []
    for rule_code in rules_to_run:
        if rule_code not in RULE_REGISTRY:
            continue

        rule_class = RULE_REGISTRY[rule_code]

        # Handle rules with special initialization
        if rule_class == WGL008FileTooLarge:
            rule = rule_class(max_jobs=max_jobs)
        else:
            rule = rule_class()

        issues = rule.check(tree, Path(filename))
        all_issues.extend(issues)

    return all_issues


def fix_code(
    source: str,
    *,
    filename: str = "<string>",
    rules: list[str] | None = None,
    add_imports: bool = True,
) -> str:
    """Fix lint issues in Python source code.

    Args:
        source: The Python source code to fix.
        filename: Optional filename for context.
        rules: List of rule codes to apply (None = all rules).
        add_imports: Whether to add required imports. Defaults to True.

    Returns:
        The fixed source code.
    """
    issues = lint_code(source, filename=filename, rules=rules)
    if not issues:
        return source

    # Filter issues that have fix information
    fixable_issues = [i for i in issues if i.original and i.suggestion]
    if not fixable_issues:
        return source

    # Collect all fix imports
    all_imports: set[str] = set()
    if add_imports:
        for issue in fixable_issues:
            if issue.fix_imports:
                all_imports.update(issue.fix_imports)

    # Separate insertions from replacements
    insertions = [i for i in fixable_issues if i.insert_after_line is not None]
    replacements = [i for i in fixable_issues if i.insert_after_line is None]

    # Apply replacements (in reverse order by line number)
    fixed_source = source
    for issue in sorted(
        replacements, key=lambda i: (i.line_number, i.column or 0), reverse=True
    ):
        if issue.original and issue.suggestion:
            # Try both double and single quotes
            original_patterns = [
                issue.original,
                issue.original.replace('"', "'"),
                issue.original.replace("'", '"'),
            ]
            for pattern in original_patterns:
                if pattern in fixed_source:
                    fixed_source = fixed_source.replace(pattern, issue.suggestion, 1)
                    break

    # Apply insertions (in reverse line order)
    if insertions:
        lines = fixed_source.splitlines(keepends=True)
        for issue in sorted(
            insertions, key=lambda i: i.insert_after_line or 0, reverse=True
        ):
            if issue.insert_after_line is not None and issue.suggestion:
                suggestion = issue.suggestion
                if not suggestion.endswith("\n"):
                    suggestion += "\n"
                lines.insert(issue.insert_after_line, suggestion)
        fixed_source = "".join(lines)

    # Add imports if needed
    if add_imports and all_imports:
        fixed_source = _add_imports(fixed_source, all_imports)

    return fixed_source


def fix_file(
    filepath: str,
    *,
    rules: list[str] | None = None,
    add_imports: bool = True,
    write: bool = False,
) -> str:
    """Fix lint issues in a Python file.

    Args:
        filepath: Path to the Python file to fix.
        rules: List of rule codes to apply (None = all rules).
        add_imports: Whether to add required imports. Defaults to True.
        write: Whether to write the fixed code back to the file.

    Returns:
        The fixed source code.
    """
    with open(filepath, encoding="utf-8") as f:
        source = f.read()

    fixed = fix_code(source, filename=filepath, rules=rules, add_imports=add_imports)

    if write and fixed != source:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(fixed)

    return fixed


def _add_imports(source: str, imports: set[str]) -> str:
    """Add import statements to source code.

    Tries to add imports in a sensible location:
    1. After existing wetwire_gitlab imports
    2. After other imports
    3. At the beginning of the file

    Args:
        source: The source code.
        imports: Set of import statements to add.

    Returns:
        Source code with imports added.
    """
    if not imports:
        return source

    lines = source.splitlines(keepends=True)

    # Find the last import line
    last_import_line = -1
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("import ") or stripped.startswith("from "):
            last_import_line = i

    # Build import block
    import_block = "\n".join(sorted(imports)) + "\n"

    if last_import_line >= 0:
        # Insert after last import
        lines.insert(last_import_line + 1, import_block)
    else:
        # Insert at beginning (after any docstrings/comments)
        insert_pos = 0
        for i, line in enumerate(lines):
            stripped = line.strip()
            if (
                stripped
                and not stripped.startswith("#")
                and not stripped.startswith('"""')
                and not stripped.startswith("'''")
            ):
                insert_pos = i
                break
        lines.insert(insert_pos, import_block)

    return "".join(lines)
