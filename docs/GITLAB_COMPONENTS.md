# GitLab CI/CD Components

This guide documents the typed Python wrappers for official GitLab CI/CD Components.

## Overview

GitLab CI/CD Components are reusable pipeline configurations from the GitLab Component Catalog. wetwire-gitlab provides typed Python wrappers for security scanning and code quality components.

## Available Components

| Component | Description | GitLab Documentation |
|-----------|-------------|---------------------|
| `SASTComponent` | Static Application Security Testing | [SAST](https://docs.gitlab.com/ee/user/application_security/sast/) |
| `SecretDetectionComponent` | Detect secrets in source code | [Secret Detection](https://docs.gitlab.com/ee/user/application_security/secret_detection/) |
| `DependencyScanningComponent` | Scan dependencies for vulnerabilities | [Dependency Scanning](https://docs.gitlab.com/ee/user/application_security/dependency_scanning/) |
| `ContainerScanningComponent` | Scan container images | [Container Scanning](https://docs.gitlab.com/ee/user/application_security/container_scanning/) |
| `DASTComponent` | Dynamic Application Security Testing | [DAST](https://docs.gitlab.com/ee/user/application_security/dast/) |
| `CodeQualityComponent` | Code quality analysis | [Code Quality](https://docs.gitlab.com/ee/ci/testing/code_quality.html) |
| `LicenseScanningComponent` | Scan for license compliance | [License Scanning](https://docs.gitlab.com/ee/user/compliance/license_scanning_of_cyclonedx_files/) |
| `CoverageComponent` | Code coverage visualization | [Coverage](https://docs.gitlab.com/ee/ci/testing/test_coverage_visualization.html) |
| `TerraformComponent` | Terraform infrastructure scanning | [Terraform](https://docs.gitlab.com/ee/user/infrastructure/iac/) |

## Basic Usage

```python
from wetwire_gitlab.pipeline import *
from wetwire_gitlab.components import SASTComponent, SecretDetectionComponent

# Create component instances
sast = SASTComponent()
secret = SecretDetectionComponent()

# Add to pipeline includes
pipeline = Pipeline(
    stages=["test", "security"],
    include=[sast.to_include(), secret.to_include()],
)
```

## Component Configuration

### SASTComponent

Static Application Security Testing scans source code for vulnerabilities.

```python
from wetwire_gitlab.components import SASTComponent

# Basic usage
sast = SASTComponent()

# With exclusions
sast = SASTComponent(
    sast_excluded_paths=["vendor/", "node_modules/", "test/"],
    sast_excluded_analyzers=["eslint", "bandit"],
)

# Add to pipeline
include = sast.to_include()
# Result: {"component": "gitlab.com/components/sast@1", "inputs": {...}}
```

**Configuration Options:**

| Attribute | Type | Description |
|-----------|------|-------------|
| `sast_excluded_paths` | `list[str]` | Paths to exclude from scanning |
| `sast_excluded_analyzers` | `list[str]` | Analyzers to disable |
| `version` | `str` | Component version (default: "1") |

### SecretDetectionComponent

Detect secrets (API keys, tokens, passwords) in source code.

```python
from wetwire_gitlab.components import SecretDetectionComponent

# Basic usage
secret = SecretDetectionComponent()

# With exclusions
secret = SecretDetectionComponent(
    secret_detection_excluded_paths=["test/fixtures/", "docs/examples/"],
)
```

**Configuration Options:**

| Attribute | Type | Description |
|-----------|------|-------------|
| `secret_detection_excluded_paths` | `list[str]` | Paths to exclude |
| `version` | `str` | Component version |

### DependencyScanningComponent

Scan dependencies for known vulnerabilities.

```python
from wetwire_gitlab.components import DependencyScanningComponent

dep_scan = DependencyScanningComponent(
    ds_excluded_paths=["vendor/"],
    ds_excluded_analyzers=["bundler-audit"],
)
```

### ContainerScanningComponent

Scan container images for vulnerabilities.

```python
from wetwire_gitlab.components import ContainerScanningComponent

container_scan = ContainerScanningComponent(
    cs_image="${CI_REGISTRY_IMAGE}:${CI_COMMIT_SHA}",
)
```

### DASTComponent

Dynamic Application Security Testing against running applications.

```python
from wetwire_gitlab.components import DASTComponent

dast = DASTComponent(
    dast_website="https://staging.example.com",
    dast_full_scan_enabled=True,
)
```

### CodeQualityComponent

Code quality analysis using Code Climate.

```python
from wetwire_gitlab.components import CodeQualityComponent

code_quality = CodeQualityComponent(
    code_quality_disabled="false",
)
```

### CoverageComponent

Code coverage visualization.

```python
from wetwire_gitlab.components import CoverageComponent

coverage = CoverageComponent(
    coverage_format="cobertura",
)
```

### TerraformComponent

Infrastructure as Code security scanning.

```python
from wetwire_gitlab.components import TerraformComponent

terraform = TerraformComponent(
    tf_root="terraform/",
)
```

## Complete Example

```python
from wetwire_gitlab.pipeline import *, Job
from wetwire_gitlab.components import (
    SASTComponent,
    SecretDetectionComponent,
    DependencyScanningComponent,
    ContainerScanningComponent,
)

# Configure components
sast = SASTComponent(sast_excluded_paths=["vendor/"])
secret = SecretDetectionComponent()
deps = DependencyScanningComponent()
container = ContainerScanningComponent(
    cs_image="${CI_REGISTRY_IMAGE}:${CI_COMMIT_SHA}",
)

# Build pipeline
pipeline = Pipeline(
    stages=["build", "test", "security", "deploy"],
    include=[
        sast.to_include(),
        secret.to_include(),
        deps.to_include(),
        container.to_include(),
    ],
)

# Add custom jobs
build = Job(
    name="build",
    stage="build",
    script=["docker build -t ${CI_REGISTRY_IMAGE}:${CI_COMMIT_SHA} ."],
)

deploy = Job(
    name="deploy",
    stage="deploy",
    script=["deploy.sh"],
    needs=["sast", "secret_detection", "dependency_scanning"],
)
```

## Generated YAML

The components generate GitLab CI include statements:

```yaml
include:
  - component: gitlab.com/components/sast@1
    inputs:
      SAST_EXCLUDED_PATHS: "vendor/,node_modules/"
  - component: gitlab.com/components/secret-detection@1
  - component: gitlab.com/components/dependency-scanning@1
  - component: gitlab.com/components/container-scanning@1
    inputs:
      CS_IMAGE: "${CI_REGISTRY_IMAGE}:${CI_COMMIT_SHA}"
```

## Best Practices

1. **Start with SAST and Secret Detection** - These provide broad coverage with minimal configuration
2. **Exclude vendor directories** - Avoid false positives from third-party code
3. **Use Container Scanning** for Docker images - Scan before pushing to registry
4. **Configure DAST for staging** - Test against actual running applications
5. **Review security reports** - Components generate SARIF/JSON reports for GitLab Security Dashboard
