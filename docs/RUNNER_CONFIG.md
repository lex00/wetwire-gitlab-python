# GitLab Runner Configuration

This guide documents the typed Python classes for GitLab Runner config.toml generation.

## Overview

wetwire-gitlab provides dataclasses for generating GitLab Runner configuration files. This enables type-safe, version-controlled runner configuration.

## Available Classes

| Class | Description |
|-------|-------------|
| `Config` | Top-level runner configuration |
| `Runner` | Individual runner definition |
| `Executor` | Executor type constants |
| `DockerConfig` | Docker executor settings |
| `KubernetesConfig` | Kubernetes executor settings |
| `CacheConfig` | Cache configuration |
| `CacheS3Config` | S3 cache backend |
| `CacheGCSConfig` | GCS cache backend |

## Basic Usage

```python
from wetwire_gitlab.runner_config import (
    Config,
    Runner,
    Executor,
    DockerConfig,
)

# Create a runner with Docker executor
runner = Runner(
    name="docker-runner",
    url="https://gitlab.example.com/",
    token="REGISTRATION_TOKEN",
    executor=Executor.DOCKER,
    docker=DockerConfig(
        image="alpine:latest",
        privileged=False,
    ),
)

# Create config
config = Config(
    concurrent=4,
    check_interval=0,
    runners=[runner],
)

# Generate TOML
toml_output = config.to_toml()
```

## Configuration Classes

### Config

Top-level configuration for all runners.

```python
config = Config(
    concurrent=4,           # Maximum concurrent jobs
    check_interval=0,       # How often to check for new jobs (0 = default)
    log_level="info",       # Log verbosity: debug, info, warn, error
    log_format="text",      # Log format: text, json
    runners=[runner1, runner2],
)
```

### Runner

Individual runner definition.

```python
runner = Runner(
    name="my-runner",
    url="https://gitlab.example.com/",
    token="${RUNNER_TOKEN}",
    executor=Executor.DOCKER,
    limit=10,                    # Max jobs for this runner
    output_limit=4096,           # Max job log size (KB)
    builds_dir="/builds",        # Where to store builds
    cache_dir="/cache",          # Where to store cache
    environment=["VAR=value"],   # Environment variables
    pre_clone_script="",         # Script before clone
    pre_build_script="",         # Script before build
    post_build_script="",        # Script after build
    docker=DockerConfig(...),    # Docker-specific config
)
```

### Executor

Executor type constants.

```python
from wetwire_gitlab.runner_config import Executor

Executor.SHELL        # "shell"
Executor.DOCKER       # "docker"
Executor.DOCKER_SSH   # "docker-ssh"
Executor.SSH          # "ssh"
Executor.PARALLELS    # "parallels"
Executor.VIRTUALBOX   # "virtualbox"
Executor.DOCKER_MACHINE # "docker+machine"
Executor.KUBERNETES   # "kubernetes"
```

### DockerConfig

Docker executor configuration.

```python
docker = DockerConfig(
    image="alpine:latest",          # Default image
    privileged=False,               # Privileged mode
    disable_cache=False,            # Disable image caching
    volumes=["/var/run/docker.sock:/var/run/docker.sock"],
    shm_size=0,                     # Shared memory size
    pull_policy="if-not-present",   # always, if-not-present, never
    allowed_images=["ruby:*", "python:*"],  # Allowed image patterns
    allowed_services=["postgres:*", "redis:*"],
    network_mode="bridge",          # Network mode
    cap_add=["SYS_ADMIN"],          # Linux capabilities to add
    cap_drop=["NET_RAW"],           # Linux capabilities to drop
    security_opt=["seccomp=unconfined"],
    devices=["/dev/kvm"],           # Devices to mount
    dns=["8.8.8.8"],                # DNS servers
    dns_search=["example.com"],     # DNS search domains
    extra_hosts=["host:ip"],        # Extra /etc/hosts entries
    helper_image="",                # Custom helper image
    tls_verify=False,               # Verify TLS
    disable_entrypoint_overwrite=False,
)
```

### KubernetesConfig

Kubernetes executor configuration.

```python
kubernetes = KubernetesConfig(
    namespace="gitlab-runner",
    service_account="gitlab-runner",
    pod_labels={"env": "ci"},
    pod_annotations={},
    image="alpine:latest",
    privileged=False,
    cpu_limit="2",
    memory_limit="4Gi",
    cpu_request="500m",
    memory_request="1Gi",
    helper_cpu_limit="500m",
    helper_memory_limit="256Mi",
)
```

### Cache Configuration

#### CacheConfig (Base)

```python
cache = CacheConfig(
    type="s3",                      # s3, gcs, azure
    path="runner/cache",            # Cache path prefix
    shared=True,                    # Share cache between runners
)
```

#### CacheS3Config

```python
from wetwire_gitlab.runner_config import CacheS3Config

s3_cache = CacheS3Config(
    server_address="s3.amazonaws.com",
    bucket_name="my-runner-cache",
    bucket_location="us-east-1",
    access_key="${AWS_ACCESS_KEY}",
    secret_key="${AWS_SECRET_KEY}",
    insecure=False,
)
```

#### CacheGCSConfig

```python
from wetwire_gitlab.runner_config import CacheGCSConfig

gcs_cache = CacheGCSConfig(
    bucket_name="my-runner-cache",
    credentials_file="/path/to/credentials.json",
)
```

## Complete Example

```python
from wetwire_gitlab.runner_config import (
    Config,
    Runner,
    Executor,
    DockerConfig,
    CacheConfig,
    CacheS3Config,
)

# Configure S3 cache
s3_cache = CacheS3Config(
    server_address="s3.amazonaws.com",
    bucket_name="gitlab-runner-cache",
    bucket_location="us-east-1",
    access_key="${AWS_ACCESS_KEY}",
    secret_key="${AWS_SECRET_KEY}",
)

# Configure Docker executor
docker = DockerConfig(
    image="alpine:latest",
    privileged=False,
    volumes=[
        "/var/run/docker.sock:/var/run/docker.sock",
        "/cache:/cache",
    ],
    pull_policy="if-not-present",
)

# Configure runner
runner = Runner(
    name="production-runner",
    url="https://gitlab.example.com/",
    token="${RUNNER_TOKEN}",
    executor=Executor.DOCKER,
    limit=10,
    docker=docker,
    cache=CacheConfig(type="s3", path="runner/", shared=True),
)
runner.cache_s3 = s3_cache

# Configure global settings
config = Config(
    concurrent=10,
    check_interval=3,
    log_level="info",
    runners=[runner],
)

# Generate config.toml
print(config.to_toml())
```

## Generated TOML

```toml
concurrent = 10
check_interval = 3
log_level = "info"

[[runners]]
  name = "production-runner"
  url = "https://gitlab.example.com/"
  token = "${RUNNER_TOKEN}"
  executor = "docker"
  limit = 10

  [runners.docker]
    image = "alpine:latest"
    privileged = false
    volumes = ["/var/run/docker.sock:/var/run/docker.sock", "/cache:/cache"]
    pull_policy = "if-not-present"

  [runners.cache]
    Type = "s3"
    Path = "runner/"
    Shared = true

    [runners.cache.s3]
      ServerAddress = "s3.amazonaws.com"
      BucketName = "gitlab-runner-cache"
      BucketLocation = "us-east-1"
      AccessKey = "${AWS_ACCESS_KEY}"
      SecretKey = "${AWS_SECRET_KEY}"
```

## Best Practices

1. **Use environment variables** for sensitive values (tokens, keys)
2. **Set appropriate limits** to prevent resource exhaustion
3. **Configure caching** for faster builds
4. **Use pull policies** to balance freshness vs speed
5. **Restrict allowed images** in shared environments
