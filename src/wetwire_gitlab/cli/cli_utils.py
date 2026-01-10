"""CLI utility functions for common operations.

This module provides reusable utilities for CLI commands including
error handling, path validation, and argument parsing helpers.
"""

import argparse
import importlib.util
import sys
from pathlib import Path


def error_exit(message: str, hint: str | None = None) -> int:
    """Print error message and return exit code.

    Args:
        message: The error message to display.
        hint: Optional hint for resolving the error.

    Returns:
        Exit code 1 for error.
    """
    print(f"Error: {message}", file=sys.stderr)
    if hint:
        print(f"Hint: {hint}", file=sys.stderr)
    return 1


def validate_package_path(path: Path) -> Path | None:
    """Validate and resolve a package path.

    Checks if the path exists and looks for a src/ subdirectory
    if present, preferring that as the scan location.

    Args:
        path: Path to validate.

    Returns:
        Resolved absolute path, or None if path doesn't exist.
    """
    resolved = path.resolve()

    if not resolved.exists():
        return None

    # Prefer src/ subdirectory if it exists
    src_dir = resolved / "src"
    if src_dir.exists() and src_dir.is_dir():
        return src_dir

    return resolved


def require_optional_dependency(module_name: str, package_name: str) -> bool:
    """Check if an optional dependency is installed.

    Args:
        module_name: The Python module name to import.
        package_name: The pip package name for error messages.

    Returns:
        True if the dependency is installed, False otherwise.
    """
    spec = importlib.util.find_spec(module_name)
    return spec is not None


def resolve_output_dir(path: Path, create: bool = False) -> Path:
    """Resolve an output directory path.

    Args:
        path: The output directory path.
        create: If True, create the directory if it doesn't exist.

    Returns:
        Resolved absolute path to the output directory.
    """
    resolved = path.resolve()

    if create and not resolved.exists():
        resolved.mkdir(parents=True, exist_ok=True)

    return resolved


def add_common_args(
    parser: argparse.ArgumentParser,
    include_format: bool = False,
    format_choices: list[str] | None = None,
) -> None:
    """Add common arguments to an argument parser.

    Args:
        parser: The argument parser to modify.
        include_format: Whether to add --format argument.
        format_choices: List of format choices (default: ["text", "json"]).
    """
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )

    if include_format:
        choices = format_choices or ["text", "json"]
        parser.add_argument(
            "--format",
            choices=choices,
            default=choices[0],
            help=f"Output format (default: {choices[0]})",
        )


def print_success(message: str) -> None:
    """Print a success message to stdout.

    Args:
        message: The success message to display.
    """
    print(message)


def print_warning(message: str) -> None:
    """Print a warning message to stderr.

    Args:
        message: The warning message to display.
    """
    print(f"Warning: {message}", file=sys.stderr)


def get_scan_directory(path: Path) -> Path:
    """Get the directory to scan for Python files.

    Resolves the path and prefers src/ subdirectory if present.

    Args:
        path: Base path to scan.

    Returns:
        Directory path to scan for Python files.
    """
    if path.is_file():
        return path.parent

    src_dir = path / "src"
    if src_dir.exists():
        return src_dir

    return path


def format_file_path(path: Path, relative_to: Path | None = None) -> str:
    """Format a file path for display.

    Args:
        path: The file path to format.
        relative_to: If provided, show path relative to this directory.

    Returns:
        Formatted path string.
    """
    if relative_to:
        try:
            return str(path.relative_to(relative_to))
        except ValueError:
            pass
    return str(path)
