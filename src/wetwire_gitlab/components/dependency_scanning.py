"""Dependency Scanning component wrapper."""

from dataclasses import dataclass

from .base import ComponentBase


@dataclass
class DependencyScanningComponent(ComponentBase):
    """GitLab Dependency Scanning component wrapper.

    Scans your project dependencies for known vulnerabilities.

    See: https://docs.gitlab.com/ee/user/application_security/dependency_scanning/

    Attributes:
        ds_excluded_paths: Paths to exclude from scanning.
        ds_excluded_analyzers: Analyzers to exclude.
        version: Component version.
    """

    ds_excluded_paths: list[str] | None = None
    ds_excluded_analyzers: list[str] | None = None

    @property
    def component_path(self) -> str:
        return "gitlab.com/components/dependency-scanning"

    def _get_inputs(self) -> dict[str, str]:
        inputs: dict[str, str] = {}

        excluded_paths = self._format_list(self.ds_excluded_paths)
        if excluded_paths:
            inputs["DS_EXCLUDED_PATHS"] = excluded_paths

        excluded_analyzers = self._format_list(self.ds_excluded_analyzers)
        if excluded_analyzers:
            inputs["DS_EXCLUDED_ANALYZERS"] = excluded_analyzers

        return inputs
