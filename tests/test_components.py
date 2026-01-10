"""Tests for GitLab CI/CD Component wrappers."""

from __future__ import annotations


class TestSASTComponent:
    """Tests for SAST component wrapper."""

    def test_sast_default(self):
        """SAST component with defaults generates correct include."""
        from wetwire_gitlab.components import SASTComponent

        sast = SASTComponent()
        include = sast.to_include()

        assert include["component"] == "gitlab.com/components/sast@~latest"
        assert "inputs" not in include or include["inputs"] == {}

    def test_sast_with_excluded_paths(self):
        """SAST component with excluded paths."""
        from wetwire_gitlab.components import SASTComponent

        sast = SASTComponent(sast_excluded_paths=["vendor/", "node_modules/"])
        include = sast.to_include()

        assert include["component"] == "gitlab.com/components/sast@~latest"
        assert include["inputs"]["SAST_EXCLUDED_PATHS"] == "vendor/,node_modules/"

    def test_sast_with_excluded_analyzers(self):
        """SAST component with excluded analyzers."""
        from wetwire_gitlab.components import SASTComponent

        sast = SASTComponent(sast_excluded_analyzers=["eslint", "bandit"])
        include = sast.to_include()

        assert include["inputs"]["SAST_EXCLUDED_ANALYZERS"] == "eslint,bandit"

    def test_sast_with_version(self):
        """SAST component with specific version."""
        from wetwire_gitlab.components import SASTComponent

        sast = SASTComponent(version="1.0.0")
        include = sast.to_include()

        assert include["component"] == "gitlab.com/components/sast@1.0.0"


class TestSecretDetectionComponent:
    """Tests for Secret Detection component wrapper."""

    def test_secret_detection_default(self):
        """Secret Detection component with defaults."""
        from wetwire_gitlab.components import SecretDetectionComponent

        sd = SecretDetectionComponent()
        include = sd.to_include()

        assert include["component"] == "gitlab.com/components/secret-detection@~latest"

    def test_secret_detection_with_historic_scan(self):
        """Secret Detection with historic scan enabled."""
        from wetwire_gitlab.components import SecretDetectionComponent

        sd = SecretDetectionComponent(secret_detection_historic_scan=True)
        include = sd.to_include()

        assert include["inputs"]["SECRET_DETECTION_HISTORIC_SCAN"] == "true"

    def test_secret_detection_with_excluded_paths(self):
        """Secret Detection with excluded paths."""
        from wetwire_gitlab.components import SecretDetectionComponent

        sd = SecretDetectionComponent(secret_detection_excluded_paths=["test/fixtures/"])
        include = sd.to_include()

        assert include["inputs"]["SECRET_DETECTION_EXCLUDED_PATHS"] == "test/fixtures/"


class TestDependencyScanningComponent:
    """Tests for Dependency Scanning component wrapper."""

    def test_dependency_scanning_default(self):
        """Dependency Scanning component with defaults."""
        from wetwire_gitlab.components import DependencyScanningComponent

        ds = DependencyScanningComponent()
        include = ds.to_include()

        assert include["component"] == "gitlab.com/components/dependency-scanning@~latest"

    def test_dependency_scanning_with_excluded_paths(self):
        """Dependency Scanning with excluded paths."""
        from wetwire_gitlab.components import DependencyScanningComponent

        ds = DependencyScanningComponent(ds_excluded_paths=["vendor/"])
        include = ds.to_include()

        assert include["inputs"]["DS_EXCLUDED_PATHS"] == "vendor/"


class TestContainerScanningComponent:
    """Tests for Container Scanning component wrapper."""

    def test_container_scanning_default(self):
        """Container Scanning component with defaults."""
        from wetwire_gitlab.components import ContainerScanningComponent

        cs = ContainerScanningComponent()
        include = cs.to_include()

        assert include["component"] == "gitlab.com/components/container-scanning@~latest"

    def test_container_scanning_with_image(self):
        """Container Scanning with custom image."""
        from wetwire_gitlab.components import ContainerScanningComponent

        cs = ContainerScanningComponent(cs_image="$CI_REGISTRY_IMAGE:$CI_COMMIT_SHA")
        include = cs.to_include()

        assert include["inputs"]["CS_IMAGE"] == "$CI_REGISTRY_IMAGE:$CI_COMMIT_SHA"


class TestCodeQualityComponent:
    """Tests for Code Quality component wrapper."""

    def test_code_quality_default(self):
        """Code Quality component with defaults."""
        from wetwire_gitlab.components import CodeQualityComponent

        cq = CodeQualityComponent()
        include = cq.to_include()

        assert include["component"] == "gitlab.com/components/code-quality@~latest"

    def test_code_quality_with_source_dir(self):
        """Code Quality with custom source directory."""
        from wetwire_gitlab.components import CodeQualityComponent

        cq = CodeQualityComponent(source_code_dir="src/")
        include = cq.to_include()

        assert include["inputs"]["SOURCE_CODE_DIR"] == "src/"


class TestLicenseScanningComponent:
    """Tests for License Scanning component wrapper."""

    def test_license_scanning_default(self):
        """License Scanning component with defaults."""
        from wetwire_gitlab.components import LicenseScanningComponent

        ls = LicenseScanningComponent()
        include = ls.to_include()

        assert include["component"] == "gitlab.com/components/license-scanning@~latest"


class TestCoverageComponent:
    """Tests for Coverage component wrapper."""

    def test_coverage_default(self):
        """Coverage component with defaults."""
        from wetwire_gitlab.components import CoverageComponent

        cov = CoverageComponent()
        include = cov.to_include()

        assert include["component"] == "gitlab.com/components/coverage-report@~latest"

    def test_coverage_with_artifact_path(self):
        """Coverage with custom artifact path."""
        from wetwire_gitlab.components import CoverageComponent

        cov = CoverageComponent(coverage_artifact_path="coverage/")
        include = cov.to_include()

        assert include["inputs"]["COVERAGE_ARTIFACT_PATH"] == "coverage/"


class TestTerraformComponent:
    """Tests for Terraform component wrapper."""

    def test_terraform_default(self):
        """Terraform component with defaults."""
        from wetwire_gitlab.components import TerraformComponent

        tf = TerraformComponent()
        include = tf.to_include()

        assert include["component"] == "gitlab.com/components/opentofu@~latest"

    def test_terraform_with_directory(self):
        """Terraform with custom directory."""
        from wetwire_gitlab.components import TerraformComponent

        tf = TerraformComponent(terraform_root_dir="infra/")
        include = tf.to_include()

        assert include["inputs"]["TERRAFORM_ROOT_DIR"] == "infra/"


class TestDASTComponent:
    """Tests for DAST component wrapper."""

    def test_dast_default(self):
        """DAST component with defaults."""
        from wetwire_gitlab.components import DASTComponent

        dast = DASTComponent(dast_website="https://example.com")
        include = dast.to_include()

        assert include["component"] == "gitlab.com/components/dast@~latest"
        assert include["inputs"]["DAST_WEBSITE"] == "https://example.com"

    def test_dast_with_full_scan(self):
        """DAST with full scan mode."""
        from wetwire_gitlab.components import DASTComponent

        dast = DASTComponent(dast_website="https://example.com", dast_full_scan_enabled=True)
        include = dast.to_include()

        assert include["inputs"]["DAST_FULL_SCAN_ENABLED"] == "true"


class TestComponentInPipeline:
    """Tests for using components in pipeline includes."""

    def test_multiple_components(self):
        """Multiple components can be used together."""
        from wetwire_gitlab.components import SASTComponent, SecretDetectionComponent
        from wetwire_gitlab.pipeline import Pipeline

        sast = SASTComponent()
        secret = SecretDetectionComponent()

        pipeline = Pipeline(
            stages=["test"],
            include=[sast.to_include(), secret.to_include()],
        )

        assert len(pipeline.include) == 2
        assert pipeline.include[0]["component"].startswith("gitlab.com/components/sast")
        assert pipeline.include[1]["component"].startswith("gitlab.com/components/secret-detection")


class TestComponentExports:
    """Tests for components module exports."""

    def test_all_components_exported(self):
        """All component classes are exported from components module."""
        from wetwire_gitlab import components

        assert hasattr(components, "SASTComponent")
        assert hasattr(components, "SecretDetectionComponent")
        assert hasattr(components, "DependencyScanningComponent")
        assert hasattr(components, "ContainerScanningComponent")
        assert hasattr(components, "CodeQualityComponent")
        assert hasattr(components, "LicenseScanningComponent")
        assert hasattr(components, "CoverageComponent")
        assert hasattr(components, "TerraformComponent")
        assert hasattr(components, "DASTComponent")
