"""AST-based discovery module for wetwire-gitlab."""

from .scanner import (
    build_dependency_graph,
    discover_file,
    discover_in_directory,
    discover_jobs,
    discover_pipelines,
    validate_references,
)

__all__ = [
    "build_dependency_graph",
    "discover_file",
    "discover_in_directory",
    "discover_jobs",
    "discover_pipelines",
    "validate_references",
]
