"""DAST (Dynamic Application Security Testing) component wrapper."""

from dataclasses import dataclass

from .base import ComponentBase


@dataclass
class DASTComponent(ComponentBase):
    """GitLab DAST component wrapper.

    Dynamic Application Security Testing scans running applications
    for vulnerabilities.

    See: https://docs.gitlab.com/ee/user/application_security/dast/

    Attributes:
        dast_website: Target website URL to scan (required).
        dast_full_scan_enabled: Enable full scan mode.
        dast_api_url: API endpoint URL for API scanning.
        version: Component version.
    """

    dast_website: str | None = None
    dast_full_scan_enabled: bool | None = None
    dast_api_url: str | None = None

    @property
    def component_path(self) -> str:
        return "gitlab.com/components/dast"

    def _get_inputs(self) -> dict[str, str]:
        inputs: dict[str, str] = {}

        if self.dast_website:
            inputs["DAST_WEBSITE"] = self.dast_website

        full_scan = self._format_bool(self.dast_full_scan_enabled)
        if full_scan:
            inputs["DAST_FULL_SCAN_ENABLED"] = full_scan

        if self.dast_api_url:
            inputs["DAST_API_URL"] = self.dast_api_url

        return inputs
