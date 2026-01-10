"""Secret Detection component wrapper."""

from dataclasses import dataclass

from .base import ComponentBase


@dataclass
class SecretDetectionComponent(ComponentBase):
    """GitLab Secret Detection component wrapper.

    Scans your source code for secrets like API keys, passwords,
    and tokens that should not be committed.

    See: https://docs.gitlab.com/ee/user/application_security/secret_detection/

    Attributes:
        secret_detection_historic_scan: Scan all commits, not just changes.
        secret_detection_excluded_paths: Paths to exclude from scanning.
        version: Component version.
    """

    secret_detection_historic_scan: bool | None = None
    secret_detection_excluded_paths: list[str] | None = None

    @property
    def component_path(self) -> str:
        return "gitlab.com/components/secret-detection"

    def _get_inputs(self) -> dict[str, str]:
        inputs: dict[str, str] = {}

        historic = self._format_bool(self.secret_detection_historic_scan)
        if historic:
            inputs["SECRET_DETECTION_HISTORIC_SCAN"] = historic

        excluded_paths = self._format_list(self.secret_detection_excluded_paths)
        if excluded_paths:
            inputs["SECRET_DETECTION_EXCLUDED_PATHS"] = excluded_paths

        return inputs
