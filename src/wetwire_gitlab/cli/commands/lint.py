"""Lint command implementation."""

import argparse
import json
from pathlib import Path

from wetwire_gitlab.cli.utils import validate_path_exists


def run_lint(args: argparse.Namespace) -> int:
    """Execute the lint command.

    Args:
        args: Parsed command-line arguments.

    Returns:
        Exit code (0=no issues, 1=issues found, 2=error).
    """
    from wetwire_gitlab.linter import fix_file, lint_directory, lint_file

    path = Path(args.path)

    if validate_path_exists(path):
        return 2

    # Apply fixes if --fix flag is set
    if getattr(args, "fix", False):
        fixed_count = 0
        if path.is_file():
            original = path.read_text()
            fixed = fix_file(str(path), write=True)
            if fixed != original:
                fixed_count += 1
                print(f"Fixed: {path}")
        else:
            for py_file in path.rglob("*.py"):
                # Skip __pycache__ and hidden directories
                if "__pycache__" in str(py_file) or any(
                    p.startswith(".") for p in py_file.parts
                ):
                    continue
                original = py_file.read_text()
                fixed = fix_file(str(py_file), write=True)
                if fixed != original:
                    fixed_count += 1
                    print(f"Fixed: {py_file}")
        if fixed_count > 0:
            print(f"\nFixed {fixed_count} file(s)")

    # Lint the path
    if path.is_file():
        result = lint_file(path)
    else:
        result = lint_directory(path)

    # Output results
    if args.format == "json":
        output = {
            "success": result.success,
            "files_checked": result.files_checked,
            "issues": [
                {
                    "code": issue.code,
                    "message": issue.message,
                    "file": issue.file_path,
                    "line": issue.line_number,
                }
                for issue in result.issues
            ],
        }
        print(json.dumps(output, indent=2))
    else:
        if result.issues:
            for issue in result.issues:
                print(
                    f"{issue.file_path}:{issue.line_number}: {issue.code} {issue.message}"
                )
            print(
                f"\nFound {len(result.issues)} issue(s) in {result.files_checked} file(s)"
            )
        else:
            print(f"No issues found in {result.files_checked} file(s)")

    return 0 if result.success else 1
