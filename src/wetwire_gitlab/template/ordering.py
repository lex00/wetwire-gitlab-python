"""Dependency ordering for pipeline template building.

This module provides topological sorting and cycle detection
for ordering jobs based on their dependencies.
"""

from collections import deque

from ..contracts import DiscoveredJob


def topological_sort(graph: dict[str, list[str]]) -> list[str]:
    """Perform topological sort on a dependency graph using Kahn's algorithm.

    Args:
        graph: Dictionary mapping node names to their dependencies.

    Returns:
        List of node names in topological order (dependencies first).

    Raises:
        ValueError: If the graph contains a cycle.
    """
    # Build in-degree map and reverse adjacency list
    in_degree: dict[str, int] = {node: 0 for node in graph}
    dependents: dict[str, list[str]] = {node: [] for node in graph}

    for node, dependencies in graph.items():
        for dep in dependencies:
            if dep in graph:  # Only count edges to nodes in the graph
                in_degree[node] += 1
                dependents[dep].append(node)

    # Find all nodes with no incoming edges (no dependencies)
    queue: deque[str] = deque()
    for node, degree in in_degree.items():
        if degree == 0:
            queue.append(node)

    result: list[str] = []

    while queue:
        node = queue.popleft()
        result.append(node)

        # Reduce in-degree for all dependents
        for dependent in dependents[node]:
            in_degree[dependent] -= 1
            if in_degree[dependent] == 0:
                queue.append(dependent)

    if len(result) != len(graph):
        raise ValueError("Graph contains a cycle")

    return result


def detect_cycle(graph: dict[str, list[str]]) -> tuple[bool, list[str]]:
    """Detect if a dependency graph contains a cycle.

    Args:
        graph: Dictionary mapping node names to their dependencies.

    Returns:
        Tuple of (has_cycle, cycle_nodes) where cycle_nodes contains
        the nodes involved in the cycle if one exists.
    """
    # Use DFS-based cycle detection with color states
    # 0 = unvisited, 1 = visiting (in current path), 2 = visited
    unvisited, visiting, visited = 0, 1, 2
    color: dict[str, int] = {node: unvisited for node in graph}
    cycle_nodes: list[str] = []

    def dfs(node: str, path: list[str]) -> bool:
        """DFS helper that returns True if a cycle is found."""
        if color[node] == visiting:
            # Found a cycle - extract the cycle from path
            cycle_start = path.index(node)
            cycle_nodes.extend(path[cycle_start:])
            return True
        if color[node] == visited:
            return False

        color[node] = visiting
        path.append(node)

        for dep in graph.get(node, []):
            if dep in graph:  # Only follow edges to nodes in the graph
                if dfs(dep, path):
                    return True

        path.pop()
        color[node] = visited
        return False

    for node in graph:
        if color[node] == unvisited:
            if dfs(node, []):
                return True, cycle_nodes

    return False, []


def build_graph_from_jobs(jobs: list[DiscoveredJob]) -> dict[str, list[str]]:
    """Build a dependency graph from a list of discovered jobs.

    Args:
        jobs: List of DiscoveredJob objects.

    Returns:
        Dictionary mapping job names to their dependencies.
    """
    graph: dict[str, list[str]] = {}

    for job in jobs:
        graph[job.name] = job.dependencies or []

    return graph


def order_jobs_for_yaml(jobs: list[DiscoveredJob]) -> list[DiscoveredJob]:
    """Order jobs for YAML generation based on dependencies.

    Jobs are ordered so that dependencies come before dependent jobs.

    Args:
        jobs: List of DiscoveredJob objects.

    Returns:
        List of jobs in dependency order.
    """
    if not jobs:
        return []

    # Build the dependency graph
    graph = build_graph_from_jobs(jobs)

    # Create a lookup map for jobs
    job_map = {job.name: job for job in jobs}

    try:
        # Get topological order
        ordered_names = topological_sort(graph)

        # Return jobs in order
        return [job_map[name] for name in ordered_names if name in job_map]
    except ValueError:
        # Cycle detected, return jobs in original order
        return jobs


def extract_stages(
    ordered_jobs: list[DiscoveredJob],
    job_stages: dict[str, str],
) -> list[str]:
    """Extract unique stages from ordered jobs.

    Stages are returned in the order they first appear in the job list,
    preserving the dependency-based ordering.

    Args:
        ordered_jobs: List of jobs in dependency order.
        job_stages: Mapping of job names to stage names.

    Returns:
        List of unique stage names in order.
    """
    seen: set[str] = set()
    stages: list[str] = []

    for job in ordered_jobs:
        stage = job_stages.get(job.name)
        if stage and stage not in seen:
            seen.add(stage)
            stages.append(stage)

    return stages
