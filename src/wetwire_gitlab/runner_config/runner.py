"""Runner configuration for GitLab Runner."""

from dataclasses import dataclass, field
from typing import Any

from .cache import CacheConfig
from .docker import DockerConfig
from .executor import Executor
from .kubernetes import KubernetesConfig


@dataclass
class Runner:
    """Configuration for a single GitLab Runner.

    Attributes:
        name: Runner description (informational).
        url: GitLab instance URL.
        token: Runner authentication token.
        executor: Environment processor type.
        limit: Concurrent jobs limit for this runner.
        request_concurrency: Concurrent job requests from GitLab.
        output_limit: Max build log size in KB.
        shell: Shell to generate scripts.
        builds_dir: Absolute path to builds directory.
        cache_dir: Absolute path to cache directory.
        environment: Environment variables to append/overwrite.
        clone_url: Overwrite GitLab instance URL for cloning.
        docker: Docker executor configuration.
        kubernetes: Kubernetes executor configuration.
        cache: Cache configuration.
    """

    name: str
    url: str
    token: str
    executor: Executor
    limit: int = 0
    request_concurrency: int = 1
    output_limit: int = 4096
    shell: str | None = None
    builds_dir: str | None = None
    cache_dir: str | None = None
    environment: list[str] = field(default_factory=list)
    clone_url: str | None = None
    docker: DockerConfig | None = None
    kubernetes: KubernetesConfig | None = None
    cache: CacheConfig | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for TOML serialization.

        Returns:
            Dictionary with non-default values.
        """
        result: dict[str, Any] = {
            "name": self.name,
            "url": self.url,
            "token": self.token,
            "executor": self.executor.value,
        }

        if self.limit != 0:
            result["limit"] = self.limit
        if self.request_concurrency != 1:
            result["request_concurrency"] = self.request_concurrency
        if self.output_limit != 4096:
            result["output_limit"] = self.output_limit
        if self.shell is not None:
            result["shell"] = self.shell
        if self.builds_dir is not None:
            result["builds_dir"] = self.builds_dir
        if self.cache_dir is not None:
            result["cache_dir"] = self.cache_dir
        if self.environment:
            result["environment"] = self.environment
        if self.clone_url is not None:
            result["clone_url"] = self.clone_url

        return result
