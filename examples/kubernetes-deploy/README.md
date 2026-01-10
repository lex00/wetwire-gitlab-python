# Kubernetes Deployment Example

A Kubernetes deployment pipeline with Helm charts and multiple environments.

## Structure

```
kubernetes-deploy/
├── ci/
│   ├── __init__.py
│   ├── jobs.py      # Job definitions
│   └── pipeline.py  # Pipeline configuration
├── pyproject.toml
└── README.md
```

## Pipeline Stages

1. **build** - Build and push Docker image
2. **deploy** - Deploy to Kubernetes environments

## Features

- Helm chart deployment
- Multi-environment support (dev, staging, production)
- Kubernetes namespace isolation
- GitLab-managed clusters integration

## Usage

```bash
# Generate .gitlab-ci.yml
wetwire-gitlab build

# Validate the generated pipeline
wetwire-gitlab validate
```

## Environment Variables Required

- `KUBE_CONTEXT` - Kubernetes context for deployment
- `HELM_RELEASE_NAME` - Helm release name
