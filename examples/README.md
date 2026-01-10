# Examples

This directory contains example projects demonstrating wetwire-gitlab usage patterns.

## Available Examples

| Example | Description |
|---------|-------------|
| [python-app](python-app/) | Basic Python CI/CD with test, lint, deploy |
| [docker-build](docker-build/) | Docker build and push to registry |
| [multi-stage](multi-stage/) | Complex pipeline with job dependencies |
| [kubernetes-deploy](kubernetes-deploy/) | Helm-based Kubernetes deployment |
| [monorepo](monorepo/) | Dynamic child pipelines for monorepos |

## Running Examples

Each example can be built independently:

```bash
# Navigate to an example
cd examples/python-app

# Generate .gitlab-ci.yml
wetwire-gitlab build

# Validate the pipeline
wetwire-gitlab validate

# List discovered jobs
wetwire-gitlab list
```

## Example Structure

Each example follows the same structure:

```
example-name/
├── ci/
│   ├── __init__.py   # Exports jobs and pipeline
│   ├── jobs.py       # Job definitions
│   └── pipeline.py   # Pipeline configuration
├── pyproject.toml    # Project configuration
└── README.md         # Example documentation
```

## Key Concepts Demonstrated

### python-app
- Multi-version Python testing
- Code coverage with artifacts
- Manual deployment gates
- Cache configuration

### docker-build
- Docker-in-Docker (DinD) setup
- GitLab Container Registry integration
- Conditional image tagging

### multi-stage
- Parallel job execution
- Job dependencies with `needs`
- Artifact passing between jobs
- Environment-based deployments

### kubernetes-deploy
- Helm chart deployments
- Multi-environment configuration
- GitLab-managed clusters

### monorepo
- Change detection with git diff
- Dynamic child pipelines
- Package-specific CI/CD
