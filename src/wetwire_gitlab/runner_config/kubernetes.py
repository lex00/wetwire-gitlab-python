"""Kubernetes executor configuration."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class KubernetesConfig:
    """Configuration for the Kubernetes executor.

    Attributes:
        host: Kubernetes host URL.
        namespace: Namespace for Kubernetes jobs.
        image: Default container image.
        privileged: Run with privilege escalation.
        service_account: Default service account for pods.
        image_pull_secrets: Docker registry secret names.
        allowed_images: Whitelist of allowed images.
        allowed_services: Whitelist of allowed services.
    """

    host: str | None = None
    namespace: str | None = None
    image: str | None = None
    privileged: bool = False
    service_account: str | None = None
    image_pull_secrets: list[str] = field(default_factory=list)
    allowed_images: list[str] = field(default_factory=list)
    allowed_services: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for TOML serialization.

        Returns:
            Dictionary with non-default values.
        """
        result: dict[str, Any] = {}

        if self.host is not None:
            result["host"] = self.host
        if self.namespace is not None:
            result["namespace"] = self.namespace
        if self.image is not None:
            result["image"] = self.image
        if self.privileged:
            result["privileged"] = self.privileged
        if self.service_account is not None:
            result["service_account"] = self.service_account
        if self.image_pull_secrets:
            result["image_pull_secrets"] = self.image_pull_secrets
        if self.allowed_images:
            result["allowed_images"] = self.allowed_images
        if self.allowed_services:
            result["allowed_services"] = self.allowed_services

        return result
