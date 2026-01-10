"""GitLab CI/CD job template wrappers.

This module provides typed wrappers for GitLab's standard job templates
from the Jobs/ directory.
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class Build:
    """Build job template configuration.

    Wraps Jobs/Build.gitlab-ci.yml template.

    Attributes:
        image: Override the default build image.
        script: Override the default build script.
        variables: Additional build variables.
    """

    image: str | None = None
    script: list[str] | None = None
    variables: dict[str, Any] | None = None

    def to_include(self) -> dict[str, str]:
        """Generate include statement for Build template.

        Returns:
            Include configuration.
        """
        return {"template": "Jobs/Build.gitlab-ci.yml"}


@dataclass
class Test:
    """Test job template configuration.

    Wraps Jobs/Test.gitlab-ci.yml template.

    Attributes:
        image: Override the default test image.
        script: Override the default test script.
        variables: Additional test variables.
        coverage_regex: Coverage regex pattern.
    """

    image: str | None = None
    script: list[str] | None = None
    variables: dict[str, Any] | None = None
    coverage_regex: str | None = None

    def to_include(self) -> dict[str, str]:
        """Generate include statement for Test template.

        Returns:
            Include configuration.
        """
        return {"template": "Jobs/Test.gitlab-ci.yml"}


@dataclass
class Deploy:
    """Deploy job template configuration.

    Wraps Jobs/Deploy.gitlab-ci.yml template.

    Attributes:
        environment: Target environment name.
        kubernetes: Whether Kubernetes deployment is enabled.
        variables: Additional deployment variables.
    """

    environment: str | None = None
    kubernetes: bool = False
    variables: dict[str, Any] | None = None

    def to_include(self) -> dict[str, str]:
        """Generate include statement for Deploy template.

        Returns:
            Include configuration.
        """
        return {"template": "Jobs/Deploy.gitlab-ci.yml"}


@dataclass
class SAST:
    """SAST (Static Application Security Testing) template configuration.

    Wraps Security/SAST.gitlab-ci.yml template.

    Attributes:
        disabled: Disable SAST entirely.
        excluded_paths: Paths to exclude from scanning.
        excluded_analyzers: Analyzers to exclude.
        sast_excluded_paths: Specific paths to exclude from SAST.
    """

    disabled: bool = False
    excluded_paths: list[str] | None = None
    excluded_analyzers: list[str] | None = None
    sast_excluded_paths: list[str] | None = None

    def to_include(self) -> dict[str, str]:
        """Generate include statement for SAST template.

        Returns:
            Include configuration.
        """
        return {"template": "Security/SAST.gitlab-ci.yml"}

    def to_variables(self) -> dict[str, Any]:
        """Generate variables for SAST configuration.

        Returns:
            Dictionary of SAST variables.
        """
        variables: dict[str, Any] = {}

        if self.disabled:
            variables["SAST_DISABLED"] = "true"
        if self.excluded_paths:
            variables["SAST_EXCLUDED_PATHS"] = ",".join(self.excluded_paths)
        if self.excluded_analyzers:
            variables["SAST_EXCLUDED_ANALYZERS"] = ",".join(self.excluded_analyzers)
        if self.sast_excluded_paths:
            variables["SAST_EXCLUDED_PATHS"] = ",".join(self.sast_excluded_paths)

        return variables


@dataclass
class DAST:
    """DAST (Dynamic Application Security Testing) template configuration.

    Wraps Security/DAST.gitlab-ci.yml template.

    Attributes:
        disabled: Disable DAST entirely.
        website: Target website URL.
        full_scan_enabled: Enable full scan mode.
        browser_scan_enabled: Enable browser-based scanning.
        api_scan_enabled: Enable API scanning.
        api_specification: Path to API specification file.
    """

    disabled: bool = False
    website: str | None = None
    full_scan_enabled: bool = False
    browser_scan_enabled: bool = False
    api_scan_enabled: bool = False
    api_specification: str | None = None

    def to_include(self) -> dict[str, str]:
        """Generate include statement for DAST template.

        Returns:
            Include configuration.
        """
        return {"template": "Security/DAST.gitlab-ci.yml"}

    def to_variables(self) -> dict[str, Any]:
        """Generate variables for DAST configuration.

        Returns:
            Dictionary of DAST variables.
        """
        variables: dict[str, Any] = {}

        if self.disabled:
            variables["DAST_DISABLED"] = "true"
        if self.website:
            variables["DAST_WEBSITE"] = self.website
        if self.full_scan_enabled:
            variables["DAST_FULL_SCAN_ENABLED"] = "true"
        if self.browser_scan_enabled:
            variables["DAST_BROWSER_SCAN_ENABLED"] = "true"
        if self.api_scan_enabled:
            variables["DAST_API_SCAN_ENABLED"] = "true"
        if self.api_specification:
            variables["DAST_API_SPECIFICATION"] = self.api_specification

        return variables
