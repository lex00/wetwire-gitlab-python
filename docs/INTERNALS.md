# Internals

This document describes the internal architecture of wetwire-gitlab.

## Package Structure

```
src/wetwire_gitlab/
├── __init__.py
├── cli/                    # CLI implementation
│   ├── __init__.py
│   ├── __main__.py        # Entry point
│   └── main.py            # Command handlers
├── codegen/               # Code generation
│   ├── fetch.py           # HTTP fetching
│   ├── generate.py        # Jinja2 code generation
│   └── parse.py           # Schema parsing
├── contracts.py           # Type contracts
├── discover/              # AST discovery
│   └── scanner.py         # File scanning
├── importer/              # YAML import
│   ├── codegen.py         # Python code generation
│   ├── ir.py              # Intermediate representation
│   └── parser.py          # YAML parsing
├── intrinsics.py          # CI variables and constants
├── linter/                # Lint rules
│   ├── linter.py          # Rule execution
│   └── rules.py           # Rule definitions
├── pipeline/              # Core types
│   ├── artifacts.py
│   ├── cache.py
│   ├── job.py
│   ├── pipeline.py
│   ├── rules.py
│   └── ...
├── runner/                # Runtime extraction
│   └── loader.py
├── runner_config/         # GitLab Runner config
│   ├── config.py
│   ├── docker.py
│   ├── executor.py
│   └── ...
├── serialize/             # Output serialization
│   ├── converter.py
│   └── yaml_builder.py
├── template/              # Template building
│   └── ordering.py        # Topological sort
├── templates/             # Auto DevOps templates
│   ├── auto_devops.py
│   └── jobs.py
└── validation/            # External validation
    └── glab.py            # glab CLI integration
```

## Build Pipeline

The build process follows these stages:

```
1. DISCOVER
   ├── Scan source files
   ├── Parse Python AST
   └── Extract Job/Pipeline declarations

2. VALIDATE
   ├── Check references exist
   ├── Detect circular dependencies
   └── Validate job names unique

3. EXTRACT
   ├── Import Python modules
   ├── Execute to get runtime values
   └── Collect Job/Pipeline instances

4. ORDER
   ├── Build dependency graph
   ├── Topological sort (Kahn's algorithm)
   └── Handle cycles with errors

5. SERIALIZE
   ├── Convert dataclasses to dicts
   ├── Transform field names (snake_case → kebab-case)
   └── Handle special types (refs, intrinsics)

6. EMIT
   ├── Generate YAML/JSON
   └── Write to output file
```

## Key Components

### Discovery (discover/scanner.py)

Uses Python's AST module to find `Job` and `Pipeline` declarations without executing code:

```python
class JobVisitor(ast.NodeVisitor):
    def visit_Assign(self, node):
        # Look for: job_name = Job(...)
        if isinstance(node.value, ast.Call):
            if self._is_job_call(node.value):
                self._extract_job(node)
```

### Dependency Graph (template/ordering.py)

Builds a directed graph from job dependencies:

```python
def build_dependency_graph(jobs: list[DiscoveredJob]) -> dict[str, set[str]]:
    graph = {job.name: set() for job in jobs}
    for job in jobs:
        for need in job.needs or []:
            graph[job.name].add(need)
    return graph
```

Uses Kahn's algorithm for topological sort:

```python
def topological_sort(graph: dict[str, set[str]]) -> list[str]:
    in_degree = {node: 0 for node in graph}
    for deps in graph.values():
        for dep in deps:
            in_degree[dep] += 1

    queue = [n for n in in_degree if in_degree[n] == 0]
    result = []

    while queue:
        node = queue.pop(0)
        result.append(node)
        for neighbor in graph.get(node, []):
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    return result
```

### Serialization (serialize/converter.py)

Converts dataclass instances to dictionaries suitable for YAML:

```python
def serialize_job(job: Job) -> dict[str, Any]:
    result = {}
    if job.stage:
        result["stage"] = job.stage
    if job.image:
        result["image"] = job.image
    if job.script:
        result["script"] = job.script
    # ... more fields
    return result
```

### Intrinsics (intrinsics.py)

Provides typed access to GitLab CI/CD predefined variables:

```python
class _CIContext:
    @property
    def commit_sha(self) -> str:
        return "$CI_COMMIT_SHA"

    COMMIT_SHA = property(lambda self: self.commit_sha)

CI = _CIContext()
# Usage: CI.COMMIT_SHA or CI.commit_sha
```

## Extension Points

### Adding New Lint Rules

1. Create rule class in `linter/rules.py`:

```python
class WGL009(LintRule):
    code = "WGL009"
    message = "Description of issue"

    def check(self, node: ast.AST, filename: str) -> list[LintIssue]:
        issues = []
        # ... analyze AST
        return issues
```

2. Register in `linter/linter.py`:

```python
RULES = [WGL001, WGL002, ..., WGL009]
```

### Adding New Pipeline Types

1. Create dataclass in `pipeline/`:

```python
@dataclass
class MyType:
    name: str
    value: str | None = None
```

2. Add to exports in `pipeline/__init__.py`

3. Update serialization in `serialize/converter.py`

### Adding New Templates

1. Create dataclass in `templates/`:

```python
@dataclass
class MyTemplate:
    def to_include(self) -> dict[str, str]:
        return {"template": "Path/To/Template.yml"}

    def to_variables(self) -> dict[str, Any]:
        return {}
```

2. Add to exports in `templates/__init__.py`
