"""Auto DevOps template configuration.

This module provides the AutoDevOps dataclass for configuring
GitLab Auto DevOps pipelines.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class AutoDevOps:
    """Configuration for GitLab Auto DevOps.

    This generates the include statement and variables for Auto DevOps.

    Attributes:
        deploy_enabled: Enable automatic deployment.
        test_disabled: Disable automatic testing.
        code_quality_disabled: Disable code quality checks.
        sast_disabled: Disable SAST scanning.
        dast_disabled: Disable DAST scanning.
        container_scanning_disabled: Disable container scanning.
        dependency_scanning_disabled: Disable dependency scanning.
        license_management_disabled: Disable license management.
        secret_detection_disabled: Disable secret detection.
        kubernetes_active: Whether Kubernetes is configured.
        staging_enabled: Enable staging environment.
        production_replicas: Number of production replicas.
    """

    deploy_enabled: bool = True
    test_disabled: bool = False
    code_quality_disabled: bool = False
    sast_disabled: bool = False
    dast_disabled: bool = False
    container_scanning_disabled: bool = False
    dependency_scanning_disabled: bool = False
    license_management_disabled: bool = False
    secret_detection_disabled: bool = False
    kubernetes_active: bool = False
    staging_enabled: bool = False
    production_replicas: int = 1

    def to_include(self) -> dict[str, str]:
        """Generate the Auto DevOps include statement.

        Returns:
            Include configuration for Auto DevOps template.
        """
        return {"template": "Auto-DevOps.gitlab-ci.yml"}

    def to_variables(self) -> dict[str, Any]:
        """Generate variables for Auto DevOps configuration.

        Returns:
            Dictionary of Auto DevOps variables.
        """
        variables: dict[str, Any] = {}

        if not self.deploy_enabled:
            variables["AUTO_DEVOPS_DEPLOY_DISABLED"] = "true"
        if self.test_disabled:
            variables["TEST_DISABLED"] = "true"
        if self.code_quality_disabled:
            variables["CODE_QUALITY_DISABLED"] = "true"
        if self.sast_disabled:
            variables["SAST_DISABLED"] = "true"
        if self.dast_disabled:
            variables["DAST_DISABLED"] = "true"
        if self.container_scanning_disabled:
            variables["CONTAINER_SCANNING_DISABLED"] = "true"
        if self.dependency_scanning_disabled:
            variables["DEPENDENCY_SCANNING_DISABLED"] = "true"
        if self.license_management_disabled:
            variables["LICENSE_MANAGEMENT_DISABLED"] = "true"
        if self.secret_detection_disabled:
            variables["SECRET_DETECTION_DISABLED"] = "true"
        if self.kubernetes_active:
            variables["KUBE_INGRESS_BASE_DOMAIN"] = "${CI_PROJECT_NAME}.example.com"
        if self.staging_enabled:
            variables["STAGING_ENABLED"] = "true"
        if self.production_replicas != 1:
            variables["PRODUCTION_REPLICAS"] = str(self.production_replicas)

        return variables


@dataclass
class AutoDevOpsConfig:
    """Extended Auto DevOps configuration.

    Attributes:
        auto_devops: Base Auto DevOps configuration.
        custom_variables: Additional custom variables.
        include_extra: Additional templates to include.
    """

    auto_devops: AutoDevOps = field(default_factory=AutoDevOps)
    custom_variables: dict[str, Any] = field(default_factory=dict)
    include_extra: list[dict[str, str]] = field(default_factory=list)

    def to_include(self) -> list[dict[str, str]]:
        """Generate all include statements.

        Returns:
            List of include configurations.
        """
        includes = [self.auto_devops.to_include()]
        includes.extend(self.include_extra)
        return includes

    def to_variables(self) -> dict[str, Any]:
        """Generate all variables.

        Returns:
            Combined variables dictionary.
        """
        variables = self.auto_devops.to_variables()
        variables.update(self.custom_variables)
        return variables
