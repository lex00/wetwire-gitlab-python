"""Docker executor configuration."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class DockerConfig:
    """Configuration for the Docker executor.

    Attributes:
        image: Default Docker image for jobs.
        host: Docker endpoint.
        privileged: Run containers in privileged mode.
        memory: Memory limit (e.g., "512m").
        cpus: Number of CPUs.
        volumes: Additional volumes to mount.
        dns: DNS servers for containers.
        pull_policy: Image pull policy (never, if-not-present, always).
        allowed_images: Whitelist of allowed images.
        allowed_services: Whitelist of allowed services.
        wait_for_services_timeout: Service startup timeout in seconds.
        disable_cache: Disable automatic cache volumes.
        cap_add: Additional Linux capabilities.
        devices: Host devices to share.
        gpus: GPU devices (Docker format).
    """

    image: str | None = None
    host: str | None = None
    privileged: bool = False
    memory: str | None = None
    cpus: str | None = None
    volumes: list[str] = field(default_factory=list)
    dns: list[str] = field(default_factory=list)
    pull_policy: str = "always"
    allowed_images: list[str] = field(default_factory=list)
    allowed_services: list[str] = field(default_factory=list)
    wait_for_services_timeout: int = 30
    disable_cache: bool = False
    cap_add: list[str] = field(default_factory=list)
    devices: list[str] = field(default_factory=list)
    gpus: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for TOML serialization.

        Returns:
            Dictionary with non-default values.
        """
        result: dict[str, Any] = {}

        if self.image is not None:
            result["image"] = self.image
        if self.host is not None:
            result["host"] = self.host
        if self.privileged:
            result["privileged"] = self.privileged
        if self.memory is not None:
            result["memory"] = self.memory
        if self.cpus is not None:
            result["cpus"] = self.cpus
        if self.volumes:
            result["volumes"] = self.volumes
        if self.dns:
            result["dns"] = self.dns
        if self.pull_policy != "always":
            result["pull_policy"] = self.pull_policy
        if self.allowed_images:
            result["allowed_images"] = self.allowed_images
        if self.allowed_services:
            result["allowed_services"] = self.allowed_services
        if self.wait_for_services_timeout != 30:
            result["wait_for_services_timeout"] = self.wait_for_services_timeout
        if self.disable_cache:
            result["disable_cache"] = self.disable_cache
        if self.cap_add:
            result["cap_add"] = self.cap_add
        if self.devices:
            result["devices"] = self.devices
        if self.gpus is not None:
            result["gpus"] = self.gpus

        return result
