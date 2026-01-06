"""Module loading and value extraction for wetwire-gitlab.

This module provides functionality to dynamically import Python modules
and extract Job/Pipeline values from them.
"""

import importlib.util
import sys
import tomllib
from pathlib import Path
from types import ModuleType
from typing import Any


def import_module_from_path(file_path: Path) -> ModuleType | None:
    """Import a Python module from a file path.

    Args:
        file_path: Path to the Python file.

    Returns:
        Imported module, or None if import failed.
    """
    try:
        # Create a unique module name based on the file path
        module_name = f"_wetwire_dynamic_{file_path.stem}_{id(file_path)}"

        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec is None or spec.loader is None:
            return None

        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module

        try:
            spec.loader.exec_module(module)
        except Exception:
            # Remove the failed module from sys.modules
            sys.modules.pop(module_name, None)
            return None

        return module

    except Exception:
        return None


def extract_jobs_from_module(
    module: ModuleType, job_class_name: str = "Job"
) -> list[Any]:
    """Extract Job instances from a module.

    Args:
        module: Imported module.
        job_class_name: Name of the Job class to look for.

    Returns:
        List of Job instances found in the module.
    """
    jobs: list[Any] = []

    # Get the Job class from the module (if defined there)
    job_class = getattr(module, job_class_name, None)

    # Also check common import locations
    if job_class is None:
        # Try to find it in module attributes
        for name in dir(module):
            obj = getattr(module, name)
            if isinstance(obj, type) and obj.__name__ == job_class_name:
                job_class = obj
                break

    if job_class is None:
        return jobs

    # Find all instances of Job class
    for name in dir(module):
        if name.startswith("_"):
            continue
        try:
            obj = getattr(module, name)
            if isinstance(obj, job_class):
                jobs.append(obj)
        except Exception:
            continue

    return jobs


def extract_pipelines_from_module(
    module: ModuleType, pipeline_class_name: str = "Pipeline"
) -> list[Any]:
    """Extract Pipeline instances from a module.

    Args:
        module: Imported module.
        pipeline_class_name: Name of the Pipeline class to look for.

    Returns:
        List of Pipeline instances found in the module.
    """
    pipelines: list[Any] = []

    # Get the Pipeline class from the module (if defined there)
    pipeline_class = getattr(module, pipeline_class_name, None)

    # Also check common import locations
    if pipeline_class is None:
        for name in dir(module):
            obj = getattr(module, name)
            if isinstance(obj, type) and obj.__name__ == pipeline_class_name:
                pipeline_class = obj
                break

    if pipeline_class is None:
        return pipelines

    # Find all instances of Pipeline class
    for name in dir(module):
        if name.startswith("_"):
            continue
        try:
            obj = getattr(module, name)
            if isinstance(obj, pipeline_class):
                pipelines.append(obj)
        except Exception:
            continue

    return pipelines


def resolve_module_path(
    file_path: Path, project_root: Path, src_dir: Path
) -> str:
    """Resolve a file path to a Python module path.

    Args:
        file_path: Path to the Python file.
        project_root: Root directory of the project.
        src_dir: Source directory (e.g., src/).

    Returns:
        Module path string (e.g., "mypackage.jobs").
    """
    try:
        relative = file_path.relative_to(src_dir)
    except ValueError:
        # File is not under src_dir, use project_root
        relative = file_path.relative_to(project_root)

    # Remove .py extension and convert path to module path
    parts = list(relative.with_suffix("").parts)
    return ".".join(parts)


def find_src_directory(project_root: Path) -> Path | None:
    """Find the source directory from project configuration.

    Args:
        project_root: Root directory of the project.

    Returns:
        Path to source directory, or None if not found.
    """
    # Try to read pyproject.toml
    pyproject_path = project_root / "pyproject.toml"
    if pyproject_path.exists():
        try:
            with open(pyproject_path, "rb") as f:
                data = tomllib.load(f)

            # Check hatch configuration
            hatch_packages = (
                data.get("tool", {})
                .get("hatch", {})
                .get("build", {})
                .get("targets", {})
                .get("wheel", {})
                .get("packages", [])
            )
            if hatch_packages:
                # Extract the first package path
                first_package = hatch_packages[0]
                if "/" in first_package:
                    src_name = first_package.split("/")[0]
                    src_path = project_root / src_name
                    if src_path.exists():
                        return src_path

            # Check setuptools configuration
            setuptools_packages = (
                data.get("tool", {}).get("setuptools", {}).get("packages", [])
            )
            if setuptools_packages:
                first_package = setuptools_packages[0]
                if "/" in first_package:
                    src_name = first_package.split("/")[0]
                    src_path = project_root / src_name
                    if src_path.exists():
                        return src_path
        except Exception:
            pass

    # Default: look for common source directory names
    for src_name in ["src", "lib", "source"]:
        src_path = project_root / src_name
        if src_path.exists() and src_path.is_dir():
            return src_path

    return None


def extract_all_jobs(
    directory: Path,
    job_class_name: str = "Job",
) -> list[Any]:
    """Extract all Job instances from Python files in a directory.

    Args:
        directory: Directory to scan.
        job_class_name: Name of the Job class to look for.

    Returns:
        List of all Job instances found.
    """
    all_jobs: list[Any] = []

    for py_file in directory.rglob("*.py"):
        # Skip __pycache__ and hidden directories
        if any(
            part.startswith(".") or part == "__pycache__"
            for part in py_file.parts
        ):
            continue

        module = import_module_from_path(py_file)
        if module is not None:
            jobs = extract_jobs_from_module(module, job_class_name)
            all_jobs.extend(jobs)

    return all_jobs


def extract_all_pipelines(
    directory: Path,
    pipeline_class_name: str = "Pipeline",
) -> list[Any]:
    """Extract all Pipeline instances from Python files in a directory.

    Args:
        directory: Directory to scan.
        pipeline_class_name: Name of the Pipeline class to look for.

    Returns:
        List of all Pipeline instances found.
    """
    all_pipelines: list[Any] = []

    for py_file in directory.rglob("*.py"):
        # Skip __pycache__ and hidden directories
        if any(
            part.startswith(".") or part == "__pycache__"
            for part in py_file.parts
        ):
            continue

        module = import_module_from_path(py_file)
        if module is not None:
            pipelines = extract_pipelines_from_module(module, pipeline_class_name)
            all_pipelines.extend(pipelines)

    return all_pipelines
