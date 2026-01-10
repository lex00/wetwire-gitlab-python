"""Container Scanning component wrapper."""

from dataclasses import dataclass

from .base import ComponentBase


@dataclass
class ContainerScanningComponent(ComponentBase):
    """GitLab Container Scanning component wrapper.

    Scans container images for known vulnerabilities.

    See: https://docs.gitlab.com/ee/user/application_security/container_scanning/

    Attributes:
        cs_image: Container image to scan.
        cs_registry_user: Registry username.
        cs_registry_password: Registry password.
        version: Component version.
    """

    cs_image: str | None = None
    cs_registry_user: str | None = None
    cs_registry_password: str | None = None

    @property
    def component_path(self) -> str:
        return "gitlab.com/components/container-scanning"

    def _get_inputs(self) -> dict[str, str]:
        inputs: dict[str, str] = {}

        if self.cs_image:
            inputs["CS_IMAGE"] = self.cs_image

        if self.cs_registry_user:
            inputs["CS_REGISTRY_USER"] = self.cs_registry_user

        if self.cs_registry_password:
            inputs["CS_REGISTRY_PASSWORD"] = self.cs_registry_password

        return inputs
