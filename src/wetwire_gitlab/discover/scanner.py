"""AST-based discovery of pipeline and job declarations.

This module scans Python source files to find Job and Pipeline
declarations using the ast module.
"""

import ast
from pathlib import Path
from typing import Any

from ..contracts import DiscoveredJob, DiscoveredPipeline, ListResult


def _extract_string_value(node: ast.expr) -> str | None:
    """Extract a string value from an AST node.

    Args:
        node: AST expression node.

    Returns:
        String value if the node is a string constant, None otherwise.
    """
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def _extract_list_values(node: ast.expr) -> list[str] | None:
    """Extract a list of string values from an AST node.

    Args:
        node: AST expression node.

    Returns:
        List of strings if the node is a list of string constants, None otherwise.
    """
    if isinstance(node, ast.List):
        result = []
        for elt in node.elts:
            val = _extract_string_value(elt)
            if val is not None:
                result.append(val)
        return result if result else None
    return None


def _get_keyword_value(
    call: ast.Call, keyword_name: str
) -> tuple[ast.expr | None, Any]:
    """Get a keyword argument value from a function call.

    Args:
        call: AST Call node.
        keyword_name: Name of the keyword argument.

    Returns:
        Tuple of (node, extracted_value) or (None, None) if not found.
    """
    for kw in call.keywords:
        if kw.arg == keyword_name:
            # Try to extract common value types
            if isinstance(kw.value, ast.Constant):
                return kw.value, kw.value.value
            if isinstance(kw.value, ast.List):
                return kw.value, _extract_list_values(kw.value)
            return kw.value, None
    return None, None


def _is_job_call(node: ast.expr) -> bool:
    """Check if a node is a Job(...) call.

    Args:
        node: AST expression node.

    Returns:
        True if this is a call to Job.
    """
    if isinstance(node, ast.Call):
        if isinstance(node.func, ast.Name) and node.func.id == "Job":
            return True
        if isinstance(node.func, ast.Attribute) and node.func.attr == "Job":
            return True
    return False


def _is_pipeline_call(node: ast.expr) -> bool:
    """Check if a node is a Pipeline(...) call.

    Args:
        node: AST expression node.

    Returns:
        True if this is a call to Pipeline.
    """
    if isinstance(node, ast.Call):
        if isinstance(node.func, ast.Name) and node.func.id == "Pipeline":
            return True
        if isinstance(node.func, ast.Attribute) and node.func.attr == "Pipeline":
            return True
    return False


def discover_jobs(file_path: Path) -> list[DiscoveredJob]:
    """Discover Job declarations in a Python file.

    Args:
        file_path: Path to the Python file to scan.

    Returns:
        List of DiscoveredJob objects found in the file.
    """
    if not file_path.suffix == ".py":
        return []

    try:
        source = file_path.read_text()
        tree = ast.parse(source)
    except (SyntaxError, OSError):
        return []

    jobs: list[DiscoveredJob] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            # Get the variable name (handle simple names only)
            if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
                var_name = node.targets[0].id

                if _is_job_call(node.value):
                    call = node.value
                    assert isinstance(call, ast.Call)

                    # Extract name keyword
                    _, name = _get_keyword_value(call, "name")
                    job_name = name if isinstance(name, str) else ""

                    # Extract needs keyword for dependencies
                    _, needs = _get_keyword_value(call, "needs")
                    dependencies = needs if isinstance(needs, list) else None

                    jobs.append(
                        DiscoveredJob(
                            name=job_name,
                            variable_name=var_name,
                            file_path=str(file_path),
                            line_number=node.lineno,
                            dependencies=dependencies,
                        )
                    )

    return jobs


def discover_pipelines(file_path: Path) -> list[DiscoveredPipeline]:
    """Discover Pipeline declarations in a Python file.

    Args:
        file_path: Path to the Python file to scan.

    Returns:
        List of DiscoveredPipeline objects found in the file.
    """
    if not file_path.suffix == ".py":
        return []

    try:
        source = file_path.read_text()
        tree = ast.parse(source)
    except (SyntaxError, OSError):
        return []

    pipelines: list[DiscoveredPipeline] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            # Get the variable name (handle simple names only)
            if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
                var_name = node.targets[0].id

                if _is_pipeline_call(node.value):
                    pipelines.append(
                        DiscoveredPipeline(
                            name=var_name,
                            file_path=str(file_path),
                            jobs=[],  # Jobs are discovered separately
                        )
                    )

    return pipelines


def discover_file(file_path: Path) -> ListResult:
    """Discover both jobs and pipelines from a single file.

    Args:
        file_path: Path to the Python file to scan.

    Returns:
        ListResult containing discovered jobs and pipelines.
    """
    return ListResult(
        jobs=discover_jobs(file_path),
        pipelines=discover_pipelines(file_path),
    )


def _should_skip_directory(name: str) -> bool:
    """Check if a directory should be skipped during discovery.

    Args:
        name: Directory name.

    Returns:
        True if the directory should be skipped.
    """
    # Skip __pycache__ and hidden directories
    return name == "__pycache__" or name.startswith(".")


def discover_in_directory(directory: Path) -> ListResult:
    """Discover jobs and pipelines in a directory recursively.

    Args:
        directory: Path to the directory to scan.

    Returns:
        ListResult containing all discovered jobs and pipelines.
    """
    all_jobs: list[DiscoveredJob] = []
    all_pipelines: list[DiscoveredPipeline] = []

    for path in directory.rglob("*.py"):
        # Check if any parent directory should be skipped
        should_skip = False
        for parent in path.relative_to(directory).parents:
            if parent.name and _should_skip_directory(parent.name):
                should_skip = True
                break

        if should_skip:
            continue

        result = discover_file(path)
        all_jobs.extend(result.jobs)
        all_pipelines.extend(result.pipelines)

    return ListResult(jobs=all_jobs, pipelines=all_pipelines)


def build_dependency_graph(jobs: list[DiscoveredJob]) -> dict[str, list[str]]:
    """Build a dependency graph from discovered jobs.

    Args:
        jobs: List of discovered jobs.

    Returns:
        Dictionary mapping job names to their dependencies.
    """
    graph: dict[str, list[str]] = {}

    for job in jobs:
        graph[job.name] = job.dependencies or []

    return graph


def validate_references(jobs: list[DiscoveredJob]) -> list[str]:
    """Validate that all job references exist.

    Args:
        jobs: List of discovered jobs.

    Returns:
        List of error messages for missing references.
    """
    job_names = {job.name for job in jobs}
    errors: list[str] = []

    for job in jobs:
        if job.dependencies:
            for dep in job.dependencies:
                if dep not in job_names:
                    errors.append(
                        f"Job '{job.name}' references non-existent job '{dep}'"
                    )

    return errors
