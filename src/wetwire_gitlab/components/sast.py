"""SAST (Static Application Security Testing) component wrapper."""

from dataclasses import dataclass

from .base import ComponentBase


@dataclass
class SASTComponent(ComponentBase):
    """GitLab SAST component wrapper.

    Static Application Security Testing scans your source code for
    known vulnerabilities.

    See: https://docs.gitlab.com/ee/user/application_security/sast/

    Attributes:
        sast_excluded_paths: Paths to exclude from scanning.
        sast_excluded_analyzers: Analyzers to exclude.
        version: Component version.
    """

    sast_excluded_paths: list[str] | None = None
    sast_excluded_analyzers: list[str] | None = None

    @property
    def component_path(self) -> str:
        return "gitlab.com/components/sast"

    def _get_inputs(self) -> dict[str, str]:
        inputs: dict[str, str] = {}

        excluded_paths = self._format_list(self.sast_excluded_paths)
        if excluded_paths:
            inputs["SAST_EXCLUDED_PATHS"] = excluded_paths

        excluded_analyzers = self._format_list(self.sast_excluded_analyzers)
        if excluded_analyzers:
            inputs["SAST_EXCLUDED_ANALYZERS"] = excluded_analyzers

        return inputs
