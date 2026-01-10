"""License Scanning component wrapper."""

from dataclasses import dataclass

from .base import ComponentBase


@dataclass
class LicenseScanningComponent(ComponentBase):
    """GitLab License Scanning component wrapper.

    Scans your project dependencies for license compliance.

    See: https://docs.gitlab.com/ee/user/compliance/license_scanning_of_cyclonedx_files/

    Attributes:
        license_finder_cli_opts: Additional License Finder CLI options.
        version: Component version.
    """

    license_finder_cli_opts: str | None = None

    @property
    def component_path(self) -> str:
        return "gitlab.com/components/license-scanning"

    def _get_inputs(self) -> dict[str, str]:
        inputs: dict[str, str] = {}

        if self.license_finder_cli_opts:
            inputs["LICENSE_FINDER_CLI_OPTS"] = self.license_finder_cli_opts

        return inputs
