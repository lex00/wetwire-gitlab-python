"""GitLab CI/CD Component wrappers.

This module provides typed Python wrappers for official GitLab CI/CD Components
from the component catalog.

Usage:
    from wetwire_gitlab.components import SASTComponent, SecretDetectionComponent

    sast = SASTComponent(sast_excluded_paths=["vendor/"])
    secret = SecretDetectionComponent()

    pipeline = Pipeline(
        include=[sast.to_include(), secret.to_include()],
    )
"""

from .code_quality import CodeQualityComponent
from .container_scanning import ContainerScanningComponent
from .coverage import CoverageComponent
from .dast import DASTComponent
from .dependency_scanning import DependencyScanningComponent
from .license_scanning import LicenseScanningComponent
from .sast import SASTComponent
from .secret_detection import SecretDetectionComponent
from .terraform import TerraformComponent

__all__ = [
    "SASTComponent",
    "SecretDetectionComponent",
    "DependencyScanningComponent",
    "ContainerScanningComponent",
    "CodeQualityComponent",
    "LicenseScanningComponent",
    "CoverageComponent",
    "TerraformComponent",
    "DASTComponent",
]
