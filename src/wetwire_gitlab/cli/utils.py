"""CLI utility functions for wetwire-gitlab commands.

This module provides common helper functions used across CLI commands
to reduce code duplication and standardize error handling.
"""

import sys
from pathlib import Path


def error_exit(message: str, code: int = 1) -> int:
    """Print error message to stderr and return exit code.

    Args:
        message: Error message to display.
        code: Exit code to return (default: 1).

    Returns:
        The exit code for use in return statements.
    """
    print(f"Error: {message}", file=sys.stderr)
    return code


def validate_path_exists(path: Path, path_type: str = "Path") -> int | None:
    """Validate that a path exists.

    Args:
        path: Path to validate.
        path_type: Description of the path type for error message
            (e.g., "File", "Directory").

    Returns:
        Exit code 1 if path doesn't exist, None if it does.
    """
    if not path.exists():
        return error_exit(f"{path_type} does not exist: {path}")
    return None


def require_optional_dependency(
    module_name: str,
    package_name: str,
    extra_name: str | None = None,
) -> int | None:
    """Check if an optional dependency is available.

    Args:
        module_name: Name of the module to import.
        package_name: Display name of the package for error message.
        extra_name: Optional extra name for pip install command
            (e.g., 'watch' for 'pip install wetwire-gitlab[watch]').

    Returns:
        Exit code 1 if dependency is missing, None if available.
    """
    try:
        __import__(module_name)
        return None
    except ImportError:
        if extra_name:
            install_cmd = f"pip install 'wetwire-gitlab[{extra_name}]'"
        else:
            install_cmd = f"pip install {package_name}"

        print(f"Error: {package_name} package is required.", file=sys.stderr)
        print(f"Install with: {install_cmd}", file=sys.stderr)
        return 1


def resolve_source_dir(path: Path) -> Path:
    """Resolve the source directory from a given path.

    Looks for a 'src' subdirectory if the path is a directory,
    otherwise returns the parent directory if path is a file.

    Args:
        path: Input path (file or directory).

    Returns:
        Resolved source directory path.
    """
    if path.is_file():
        return path.parent

    # Look for src directory
    src_dir = path / "src"
    if src_dir.exists():
        return src_dir
    return path


def resolve_output_dir(path: Path, default_dir: Path | None = None) -> Path:
    """Resolve the output directory from a given path.

    Args:
        path: Input path that may be a file or directory.
        default_dir: Default directory if path is a file (default: path's parent).

    Returns:
        Resolved output directory path.
    """
    if path.is_file():
        return default_dir if default_dir else path.parent
    return path
