"""Import command implementation."""

import argparse
import sys
from pathlib import Path


def run_import(args: argparse.Namespace) -> int:
    """Execute the import command.

    Args:
        args: Parsed command-line arguments.

    Returns:
        Exit code (0=success, 1=error).
    """
    from wetwire_gitlab.importer import generate_python_code, parse_gitlab_ci_file

    input_path = Path(args.path)

    if not input_path.exists():
        print(f"Error: File does not exist: {input_path}", file=sys.stderr)
        return 1

    # Parse the YAML file
    try:
        pipeline = parse_gitlab_ci_file(input_path)
    except Exception as e:
        print(f"Error parsing YAML: {e}", file=sys.stderr)
        return 1

    # Generate Python code
    code = generate_python_code(pipeline)

    # Determine output location
    output_dir = Path(args.output) if args.output else Path.cwd()

    if args.single_file:
        # Write to a single file
        output_file = output_dir / "pipeline.py"
        output_file.write_text(code)
        print(f"Generated {output_file}")
    else:
        # Create package structure
        if not args.no_scaffold:
            # Create src directory
            src_dir = output_dir / "src" / "pipeline"
            src_dir.mkdir(parents=True, exist_ok=True)

            # Create __init__.py
            (src_dir / "__init__.py").write_text('"""Pipeline package."""\n')

            # Create jobs.py
            (src_dir / "jobs.py").write_text(code)

            # Create pyproject.toml if scaffold is enabled
            pyproject_content = """[project]
name = "pipeline"
version = "0.1.0"
dependencies = ["wetwire-gitlab"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
"""
            (output_dir / "pyproject.toml").write_text(pyproject_content)
            print(f"Generated pipeline package in {output_dir}")
        else:
            # Just create the jobs.py file
            output_dir.mkdir(parents=True, exist_ok=True)
            output_file = output_dir / "jobs.py"
            output_file.write_text(code)
            print(f"Generated {output_file}")

    return 0
