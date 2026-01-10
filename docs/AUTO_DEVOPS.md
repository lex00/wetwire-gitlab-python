# Auto DevOps

This guide documents the Auto DevOps template configuration for wetwire-gitlab.

## Overview

GitLab Auto DevOps provides a pre-configured CI/CD pipeline with:
- Build (using Buildpacks or Dockerfile)
- Test (code quality, SAST, dependency scanning)
- Review Apps
- Staging/Production deployment
- Performance and accessibility testing

wetwire-gitlab provides typed configuration for customizing Auto DevOps.

## Basic Usage

```python
from wetwire_gitlab.pipeline import Pipeline
from wetwire_gitlab.templates import AutoDevOps

# Create Auto DevOps configuration
auto_devops = AutoDevOps()

# Create pipeline with Auto DevOps
pipeline = Pipeline(
    include=[auto_devops.to_include()],
    variables=auto_devops.to_variables(),
)
```

## Configuration Options

### AutoDevOps

The `AutoDevOps` class provides toggle options for each feature.

```python
from wetwire_gitlab.templates import AutoDevOps

auto_devops = AutoDevOps(
    # Deployment settings
    deploy_enabled=True,           # Enable automatic deployment
    kubernetes_active=False,       # Kubernetes cluster configured
    staging_enabled=False,         # Enable staging environment
    production_replicas=1,         # Number of production replicas

    # Feature toggles (True = disabled)
    test_disabled=False,           # Disable automatic testing
    code_quality_disabled=False,   # Disable code quality checks
    sast_disabled=False,           # Disable SAST scanning
    dast_disabled=False,           # Disable DAST scanning
    container_scanning_disabled=False,    # Disable container scanning
    dependency_scanning_disabled=False,   # Disable dependency scanning
    license_management_disabled=False,    # Disable license management
    secret_detection_disabled=False,      # Disable secret detection
)
```

### Feature Flags

| Feature | Variable | Default |
|---------|----------|---------|
| Deploy | `AUTO_DEVOPS_DEPLOY_DISABLED` | Enabled |
| Testing | `TEST_DISABLED` | Enabled |
| Code Quality | `CODE_QUALITY_DISABLED` | Enabled |
| SAST | `SAST_DISABLED` | Enabled |
| DAST | `DAST_DISABLED` | Enabled |
| Container Scanning | `CONTAINER_SCANNING_DISABLED` | Enabled |
| Dependency Scanning | `DEPENDENCY_SCANNING_DISABLED` | Enabled |
| License Management | `LICENSE_MANAGEMENT_DISABLED` | Enabled |
| Secret Detection | `SECRET_DETECTION_DISABLED` | Enabled |

## Extended Configuration

### AutoDevOpsConfig

For more complex setups, use `AutoDevOpsConfig`:

```python
from wetwire_gitlab.templates import AutoDevOps, AutoDevOpsConfig

config = AutoDevOpsConfig(
    auto_devops=AutoDevOps(
        deploy_enabled=True,
        staging_enabled=True,
        production_replicas=3,
    ),
    custom_variables={
        "POSTGRES_ENABLED": "true",
        "PERFORMANCE_DISABLED": "true",
        "ACCESSIBILITY_DISABLED": "true",
    },
    include_extra=[
        {"template": "Security/SAST.gitlab-ci.yml"},
    ],
)

pipeline = Pipeline(
    include=config.to_include(),
    variables=config.to_variables(),
)
```

## Common Configurations

### Development Only (No Deploy)

```python
auto_devops = AutoDevOps(
    deploy_enabled=False,
)
```

Generated variables:
```yaml
variables:
  AUTO_DEVOPS_DEPLOY_DISABLED: "true"
```

### Production with Staging

```python
auto_devops = AutoDevOps(
    kubernetes_active=True,
    staging_enabled=True,
    production_replicas=3,
)
```

Generated variables:
```yaml
variables:
  KUBE_INGRESS_BASE_DOMAIN: "${CI_PROJECT_NAME}.example.com"
  STAGING_ENABLED: "true"
  PRODUCTION_REPLICAS: "3"
```

### Security Scanning Only

```python
auto_devops = AutoDevOps(
    deploy_enabled=False,
    test_disabled=True,
    code_quality_disabled=True,
    # Keep security scanning enabled (default)
)
```

### Minimal Pipeline

```python
auto_devops = AutoDevOps(
    deploy_enabled=False,
    sast_disabled=True,
    dast_disabled=True,
    container_scanning_disabled=True,
    dependency_scanning_disabled=True,
    license_management_disabled=True,
    secret_detection_disabled=True,
)
```

## Complete Example

```python
from wetwire_gitlab.pipeline import Pipeline, Job
from wetwire_gitlab.templates import AutoDevOps, AutoDevOpsConfig
from wetwire_gitlab.intrinsics import Rules

# Configure Auto DevOps
auto_devops_config = AutoDevOpsConfig(
    auto_devops=AutoDevOps(
        deploy_enabled=True,
        kubernetes_active=True,
        staging_enabled=True,
        production_replicas=3,
        # Disable some features to speed up pipeline
        dast_disabled=True,
        license_management_disabled=True,
    ),
    custom_variables={
        "POSTGRES_ENABLED": "true",
        "PERFORMANCE_DISABLED": "true",
    },
)

# Create pipeline
pipeline = Pipeline(
    include=auto_devops_config.to_include(),
    variables=auto_devops_config.to_variables(),
)

# Add custom jobs to extend Auto DevOps
custom_test = Job(
    name="custom-integration-tests",
    stage="test",
    script=[
        "pip install -r requirements.txt",
        "pytest tests/integration/",
    ],
)

manual_production = Job(
    name="deploy-production-manual",
    stage="production",
    script=["echo 'Deploying to production'"],
    rules=[Rules.MANUAL],
    environment={"name": "production", "url": "https://app.example.com"},
)
```

## Generated YAML

```yaml
include:
  - template: Auto-DevOps.gitlab-ci.yml

variables:
  KUBE_INGRESS_BASE_DOMAIN: "${CI_PROJECT_NAME}.example.com"
  STAGING_ENABLED: "true"
  PRODUCTION_REPLICAS: "3"
  DAST_DISABLED: "true"
  LICENSE_MANAGEMENT_DISABLED: "true"
  POSTGRES_ENABLED: "true"
  PERFORMANCE_DISABLED: "true"

custom-integration-tests:
  stage: test
  script:
    - pip install -r requirements.txt
    - pytest tests/integration/

deploy-production-manual:
  stage: production
  script:
    - echo 'Deploying to production'
  when: manual
  environment:
    name: production
    url: https://app.example.com
```

## Best Practices

1. **Start simple** - Enable Auto DevOps defaults, then customize
2. **Disable unused features** - Speed up pipelines by disabling unneeded scans
3. **Use staging** - Test deployments before production
4. **Scale replicas** - Set `production_replicas` based on traffic
5. **Add custom jobs** - Extend Auto DevOps with project-specific tests
6. **Use Kubernetes** - Full Auto DevOps features require a connected cluster

## References

- [GitLab Auto DevOps](https://docs.gitlab.com/ee/topics/autodevops/)
- [Customizing Auto DevOps](https://docs.gitlab.com/ee/topics/autodevops/customize.html)
- [Auto DevOps Variables](https://docs.gitlab.com/ee/topics/autodevops/cicd_variables.html)
