# Docker Build Example

A Docker build and push pipeline demonstrating container registry integration.

## Structure

```
docker-build/
├── ci/
│   ├── __init__.py
│   ├── jobs.py      # Job definitions
│   └── pipeline.py  # Pipeline configuration
├── pyproject.toml
└── README.md
```

## Pipeline Stages

1. **build** - Build Docker image
2. **test** - Test the built image
3. **push** - Push to container registry

## Features

- Uses GitLab Container Registry
- Multi-architecture builds with buildx
- Semantic versioning with tags
- Branch-based image tagging

## Usage

```bash
# Generate .gitlab-ci.yml
wetwire-gitlab build

# Validate the generated pipeline
wetwire-gitlab validate
```
