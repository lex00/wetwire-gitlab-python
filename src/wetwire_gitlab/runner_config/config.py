"""Top-level GitLab Runner configuration."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .cache import CacheConfig, CacheGCSConfig, CacheS3Config
from .docker import DockerConfig
from .executor import Executor
from .kubernetes import KubernetesConfig
from .runner import Runner


@dataclass
class Config:
    """Top-level GitLab Runner configuration (config.toml).

    Attributes:
        concurrent: Limits how many jobs can run concurrently.
        runners: List of runner configurations.
        log_level: Log level (debug, info, warn, error, fatal, panic).
        log_format: Log format (runner, text, json).
        check_interval: Seconds between runner checking for new jobs.
        sentry_dsn: Enable Sentry error tracking.
        connection_max_age: Maximum TLS keepalive connection duration.
        listen_address: Address for Prometheus metrics HTTP server.
        shutdown_timeout: Seconds until forceful shutdown times out.
    """

    concurrent: int
    runners: list[Runner] = field(default_factory=list)
    log_level: str | None = None
    log_format: str | None = None
    check_interval: int = 3
    sentry_dsn: str | None = None
    connection_max_age: str | None = None
    listen_address: str | None = None
    shutdown_timeout: int = 30

    def to_toml(self) -> str:
        """Serialize configuration to TOML format.

        Returns:
            TOML-formatted string.
        """
        lines: list[str] = []

        # Global settings
        lines.append(f"concurrent = {self.concurrent}")

        if self.log_level is not None:
            lines.append(f'log_level = "{self.log_level}"')
        if self.log_format is not None:
            lines.append(f'log_format = "{self.log_format}"')
        if self.check_interval != 3:
            lines.append(f"check_interval = {self.check_interval}")
        if self.sentry_dsn is not None:
            lines.append(f'sentry_dsn = "{self.sentry_dsn}"')
        if self.connection_max_age is not None:
            lines.append(f'connection_max_age = "{self.connection_max_age}"')
        if self.listen_address is not None:
            lines.append(f'listen_address = "{self.listen_address}"')
        if self.shutdown_timeout != 30:
            lines.append(f"shutdown_timeout = {self.shutdown_timeout}")

        # Runners
        for runner in self.runners:
            lines.append("")
            lines.append("[[runners]]")
            runner_dict = runner.to_dict()
            for key, value in runner_dict.items():
                lines.append(_format_toml_value(key, value))

            # Docker config
            if runner.docker is not None:
                docker_dict = runner.docker.to_dict()
                if docker_dict:
                    lines.append("")
                    lines.append("[runners.docker]")
                    for key, value in docker_dict.items():
                        lines.append(_format_toml_value(key, value))

            # Kubernetes config
            if runner.kubernetes is not None:
                k8s_dict = runner.kubernetes.to_dict()
                if k8s_dict:
                    lines.append("")
                    lines.append("[runners.kubernetes]")
                    for key, value in k8s_dict.items():
                        lines.append(_format_toml_value(key, value))

            # Cache config
            if runner.cache is not None:
                cache_dict = runner.cache.to_dict()
                if cache_dict:
                    lines.append("")
                    lines.append("[runners.cache]")
                    for key, value in cache_dict.items():
                        lines.append(_format_toml_value(key, value))

                # S3 cache
                if runner.cache.s3 is not None:
                    s3_dict = runner.cache.s3.to_dict()
                    if s3_dict:
                        lines.append("")
                        lines.append("[runners.cache.s3]")
                        for key, value in s3_dict.items():
                            lines.append(_format_toml_value(key, value))

                # GCS cache
                if runner.cache.gcs is not None:
                    gcs_dict = runner.cache.gcs.to_dict()
                    if gcs_dict:
                        lines.append("")
                        lines.append("[runners.cache.gcs]")
                        for key, value in gcs_dict.items():
                            lines.append(_format_toml_value(key, value))

        lines.append("")
        return "\n".join(lines)

    @classmethod
    def from_toml(cls, toml_str: str) -> Config:
        """Parse TOML string into Config object.

        Args:
            toml_str: TOML-formatted configuration string.

        Returns:
            Parsed Config object.
        """
        try:
            import tomllib
        except ImportError:
            import tomli as tomllib  # type: ignore[import-not-found,no-redef]

        data = tomllib.loads(toml_str)

        runners: list[Runner] = []
        for runner_data in data.get("runners", []):
            executor = Executor(runner_data["executor"])

            # Parse docker config
            docker = None
            if "docker" in runner_data:
                docker_data = runner_data["docker"]
                docker = DockerConfig(
                    image=docker_data.get("image"),
                    host=docker_data.get("host"),
                    privileged=docker_data.get("privileged", False),
                    memory=docker_data.get("memory"),
                    cpus=docker_data.get("cpus"),
                    volumes=docker_data.get("volumes", []),
                    dns=docker_data.get("dns", []),
                    pull_policy=docker_data.get("pull_policy", "always"),
                )

            # Parse kubernetes config
            kubernetes = None
            if "kubernetes" in runner_data:
                k8s_data = runner_data["kubernetes"]
                kubernetes = KubernetesConfig(
                    host=k8s_data.get("host"),
                    namespace=k8s_data.get("namespace"),
                    image=k8s_data.get("image"),
                    privileged=k8s_data.get("privileged", False),
                    service_account=k8s_data.get("service_account"),
                    image_pull_secrets=k8s_data.get("image_pull_secrets", []),
                )

            # Parse cache config
            cache = None
            if "cache" in runner_data:
                cache_data = runner_data["cache"]
                s3 = None
                if "s3" in cache_data:
                    s3_data = cache_data["s3"]
                    s3 = CacheS3Config(
                        server_address=s3_data.get("ServerAddress"),
                        access_key=s3_data.get("AccessKey"),
                        secret_key=s3_data.get("SecretKey"),
                        bucket_name=s3_data.get("BucketName"),
                        bucket_location=s3_data.get("BucketLocation"),
                    )
                gcs = None
                if "gcs" in cache_data:
                    gcs_data = cache_data["gcs"]
                    gcs = CacheGCSConfig(
                        credentials_file=gcs_data.get("CredentialsFile"),
                        access_id=gcs_data.get("AccessID"),
                        private_key=gcs_data.get("PrivateKey"),
                        bucket_name=gcs_data.get("BucketName"),
                    )
                cache = CacheConfig(
                    type=cache_data.get("Type"),
                    path=cache_data.get("Path"),
                    shared=cache_data.get("Shared", False),
                    s3=s3,
                    gcs=gcs,
                )

            runner = Runner(
                name=runner_data["name"],
                url=runner_data["url"],
                token=runner_data["token"],
                executor=executor,
                limit=runner_data.get("limit", 0),
                request_concurrency=runner_data.get("request_concurrency", 1),
                output_limit=runner_data.get("output_limit", 4096),
                shell=runner_data.get("shell"),
                builds_dir=runner_data.get("builds_dir"),
                cache_dir=runner_data.get("cache_dir"),
                environment=runner_data.get("environment", []),
                clone_url=runner_data.get("clone_url"),
                docker=docker,
                kubernetes=kubernetes,
                cache=cache,
            )
            runners.append(runner)

        return cls(
            concurrent=data["concurrent"],
            runners=runners,
            log_level=data.get("log_level"),
            log_format=data.get("log_format"),
            check_interval=data.get("check_interval", 3),
            sentry_dsn=data.get("sentry_dsn"),
            connection_max_age=data.get("connection_max_age"),
            listen_address=data.get("listen_address"),
            shutdown_timeout=data.get("shutdown_timeout", 30),
        )


def _format_toml_value(key: str, value: Any) -> str:
    """Format a key-value pair as TOML.

    Args:
        key: The key name.
        value: The value to format.

    Returns:
        Formatted TOML line.
    """
    if isinstance(value, bool):
        return f"{key} = {str(value).lower()}"
    elif isinstance(value, int):
        return f"{key} = {value}"
    elif isinstance(value, str):
        return f'{key} = "{value}"'
    elif isinstance(value, list):
        items = ", ".join(f'"{v}"' for v in value)
        return f"{key} = [{items}]"
    else:
        return f'{key} = "{value}"'
