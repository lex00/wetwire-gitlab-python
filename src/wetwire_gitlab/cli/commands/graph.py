"""Graph command implementation."""

import argparse
import sys
from pathlib import Path


def run_graph(args: argparse.Namespace) -> int:
    """Execute the graph command.

    Args:
        args: Parsed command-line arguments.

    Returns:
        Exit code (0=success, 1=error).
    """
    from wetwire_gitlab.discover import discover_in_directory

    path = Path(args.path)

    if not path.exists():
        print(f"Error: Path does not exist: {path}", file=sys.stderr)
        return 1

    # Find source directory
    if path.is_file():
        scan_dir = path.parent
    else:
        src_dir = path / "src"
        if src_dir.exists():
            scan_dir = src_dir
        else:
            scan_dir = path

    # Discover jobs
    result = discover_in_directory(scan_dir)

    if not result.jobs:
        print("No jobs found.", file=sys.stderr)
        return 1

    # Build dependency graph
    graph_lines = []
    include_params = getattr(args, "params", False)
    use_clusters = getattr(args, "cluster", False)

    if args.format == "dot":
        graph_lines.extend(
            _generate_dot_graph(result.jobs, include_params, use_clusters)
        )
    else:
        # Mermaid format (default)
        graph_lines.extend(
            _generate_mermaid_graph(result.jobs, include_params, use_clusters)
        )

    output = "\n".join(graph_lines)

    if args.output:
        output_path = Path(args.output)
        output_path.write_text(output)
        print(f"Generated {output_path}")
    else:
        print(output)

    return 0


def _generate_mermaid_graph(
    jobs: list, include_params: bool = False, use_clusters: bool = False
) -> list[str]:
    """Generate Mermaid graph output.

    Args:
        jobs: List of DiscoveredJob objects.
        include_params: Whether to include variable nodes.
        use_clusters: Whether to group jobs by stage.

    Returns:
        List of graph lines.
    """
    lines = ["graph LR"]

    if use_clusters:
        # Group jobs by stage
        stages: dict[str, list] = {}
        for job in jobs:
            stage = job.stage or "default"
            if stage not in stages:
                stages[stage] = []
            stages[stage].append(job)

        # Generate subgraphs for each stage
        for stage, stage_jobs in stages.items():
            lines.append(f"  subgraph {stage}")
            for job in stage_jobs:
                node_label = _mermaid_node_label(job)
                lines.append(f"    {job.name}{node_label}")
            lines.append("  end")
    else:
        # Flat graph
        for job in jobs:
            node_label = _mermaid_node_label(job)
            lines.append(f"  {job.name}{node_label}")

    # Add edges for dependencies
    for job in jobs:
        if job.dependencies:
            for dep in job.dependencies:
                lines.append(f"  {dep} --> {job.name}")

    # Add variable nodes if requested
    if include_params:
        all_vars: set[str] = set()
        for job in jobs:
            if job.variables:
                for var_name in job.variables:
                    all_vars.add(var_name)
                    lines.append(f"  {var_name}([{var_name}]) -.-> {job.name}")

    return lines


def _mermaid_node_label(job) -> str:
    """Generate Mermaid node label with annotations.

    Args:
        job: DiscoveredJob object.

    Returns:
        Node label string (empty or with brackets for custom label).
    """
    if job.when:
        return f"[{job.name}<br/>{job.when}]"
    return ""


def _generate_dot_graph(
    jobs: list, include_params: bool = False, use_clusters: bool = False
) -> list[str]:
    """Generate DOT graph output.

    Args:
        jobs: List of DiscoveredJob objects.
        include_params: Whether to include variable nodes.
        use_clusters: Whether to group jobs by stage.

    Returns:
        List of graph lines.
    """
    lines = ["digraph pipeline {", "  rankdir=LR;", "  node [shape=box];"]

    if use_clusters:
        # Group jobs by stage
        stages: dict[str, list] = {}
        for job in jobs:
            stage = job.stage or "default"
            if stage not in stages:
                stages[stage] = []
            stages[stage].append(job)

        # Generate subgraphs for each stage
        for idx, (stage, stage_jobs) in enumerate(stages.items()):
            lines.append(f"  subgraph cluster_{idx} {{")
            lines.append(f'    label="{stage}";')
            for job in stage_jobs:
                node_label = _dot_node_label(job)
                lines.append(f'    "{job.name}"{node_label};')
            lines.append("  }")
    else:
        # Flat graph
        for job in jobs:
            node_label = _dot_node_label(job)
            lines.append(f'  "{job.name}"{node_label};')

    # Add edges for dependencies
    for job in jobs:
        if job.dependencies:
            for dep in job.dependencies:
                lines.append(f'  "{dep}" -> "{job.name}";')

    # Add variable nodes if requested
    if include_params:
        lines.append("  node [shape=ellipse, style=dashed];")
        for job in jobs:
            if job.variables:
                for var_name in job.variables:
                    lines.append(f'  "{var_name}";')
                    lines.append(f'  "{var_name}" -> "{job.name}" [style=dashed];')

    lines.append("}")
    return lines


def _dot_node_label(job) -> str:
    """Generate DOT node label with annotations.

    Args:
        job: DiscoveredJob object.

    Returns:
        Node label string for DOT format.
    """
    if job.when:
        return f' [label="{job.name}\\n({job.when})"]'
    return ""
