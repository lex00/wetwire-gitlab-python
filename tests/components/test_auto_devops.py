"""Tests for Auto DevOps templates module."""



class TestAutoDevOps:
    """Tests for AutoDevOps configuration."""

    def test_default_auto_devops(self):
        """Default Auto DevOps configuration."""
        from wetwire_gitlab.templates import AutoDevOps

        config = AutoDevOps()

        assert config.deploy_enabled is True
        assert config.test_disabled is False
        assert config.sast_disabled is False

    def test_auto_devops_to_include(self):
        """Auto DevOps generates include statement."""
        from wetwire_gitlab.templates import AutoDevOps

        config = AutoDevOps()
        include = config.to_include()

        assert include == {"template": "Auto-DevOps.gitlab-ci.yml"}

    def test_auto_devops_disabled_features(self):
        """Auto DevOps with disabled features."""
        from wetwire_gitlab.templates import AutoDevOps

        config = AutoDevOps(
            deploy_enabled=False,
            test_disabled=True,
            sast_disabled=True,
        )
        variables = config.to_variables()

        assert "AUTO_DEVOPS_DEPLOY_DISABLED" in variables
        assert "TEST_DISABLED" in variables
        assert "SAST_DISABLED" in variables

    def test_auto_devops_production_replicas(self):
        """Auto DevOps with custom production replicas."""
        from wetwire_gitlab.templates import AutoDevOps

        config = AutoDevOps(production_replicas=3)
        variables = config.to_variables()

        assert variables["PRODUCTION_REPLICAS"] == "3"

    def test_auto_devops_staging_enabled(self):
        """Auto DevOps with staging enabled."""
        from wetwire_gitlab.templates import AutoDevOps

        config = AutoDevOps(staging_enabled=True)
        variables = config.to_variables()

        assert variables["STAGING_ENABLED"] == "true"


class TestBuildTemplate:
    """Tests for Build template."""

    def test_build_to_include(self):
        """Build template generates include statement."""
        from wetwire_gitlab.templates import Build

        build = Build()
        include = build.to_include()

        assert include == {"template": "Jobs/Build.gitlab-ci.yml"}

    def test_build_with_custom_image(self):
        """Build template with custom image."""
        from wetwire_gitlab.templates import Build

        build = Build(image="python:3.11")

        assert build.image == "python:3.11"


class TestTestTemplate:
    """Tests for Test template."""

    def test_test_to_include(self):
        """Test template generates include statement."""
        from wetwire_gitlab.templates import Test

        test = Test()
        include = test.to_include()

        assert include == {"template": "Jobs/Test.gitlab-ci.yml"}

    def test_test_with_coverage(self):
        """Test template with coverage regex."""
        from wetwire_gitlab.templates import Test

        test = Test(coverage_regex=r"^TOTAL.+?(\d+\%)$")

        assert test.coverage_regex is not None


class TestDeployTemplate:
    """Tests for Deploy template."""

    def test_deploy_to_include(self):
        """Deploy template generates include statement."""
        from wetwire_gitlab.templates import Deploy

        deploy = Deploy()
        include = deploy.to_include()

        assert include == {"template": "Jobs/Deploy.gitlab-ci.yml"}

    def test_deploy_with_environment(self):
        """Deploy template with environment."""
        from wetwire_gitlab.templates import Deploy

        deploy = Deploy(environment="production")

        assert deploy.environment == "production"

    def test_deploy_with_kubernetes(self):
        """Deploy template with Kubernetes enabled."""
        from wetwire_gitlab.templates import Deploy

        deploy = Deploy(kubernetes=True)

        assert deploy.kubernetes is True


class TestSASTTemplate:
    """Tests for SAST template."""

    def test_sast_to_include(self):
        """SAST template generates include statement."""
        from wetwire_gitlab.templates import SAST

        sast = SAST()
        include = sast.to_include()

        assert include == {"template": "Security/SAST.gitlab-ci.yml"}

    def test_sast_disabled(self):
        """SAST with scanning disabled."""
        from wetwire_gitlab.templates import SAST

        sast = SAST(disabled=True)
        variables = sast.to_variables()

        assert variables["SAST_DISABLED"] == "true"

    def test_sast_excluded_paths(self):
        """SAST with excluded paths."""
        from wetwire_gitlab.templates import SAST

        sast = SAST(excluded_paths=["vendor/", "node_modules/"])
        variables = sast.to_variables()

        assert "vendor/,node_modules/" in variables["SAST_EXCLUDED_PATHS"]

    def test_sast_excluded_analyzers(self):
        """SAST with excluded analyzers."""
        from wetwire_gitlab.templates import SAST

        sast = SAST(excluded_analyzers=["eslint", "semgrep"])
        variables = sast.to_variables()

        assert "eslint,semgrep" in variables["SAST_EXCLUDED_ANALYZERS"]


class TestDASTTemplate:
    """Tests for DAST template."""

    def test_dast_to_include(self):
        """DAST template generates include statement."""
        from wetwire_gitlab.templates import DAST

        dast = DAST()
        include = dast.to_include()

        assert include == {"template": "Security/DAST.gitlab-ci.yml"}

    def test_dast_disabled(self):
        """DAST with scanning disabled."""
        from wetwire_gitlab.templates import DAST

        dast = DAST(disabled=True)
        variables = dast.to_variables()

        assert variables["DAST_DISABLED"] == "true"

    def test_dast_website(self):
        """DAST with target website."""
        from wetwire_gitlab.templates import DAST

        dast = DAST(website="https://example.com")
        variables = dast.to_variables()

        assert variables["DAST_WEBSITE"] == "https://example.com"

    def test_dast_full_scan(self):
        """DAST with full scan enabled."""
        from wetwire_gitlab.templates import DAST

        dast = DAST(full_scan_enabled=True)
        variables = dast.to_variables()

        assert variables["DAST_FULL_SCAN_ENABLED"] == "true"

    def test_dast_api_scan(self):
        """DAST with API scanning enabled."""
        from wetwire_gitlab.templates import DAST

        dast = DAST(
            api_scan_enabled=True,
            api_specification="openapi.yaml",
        )
        variables = dast.to_variables()

        assert variables["DAST_API_SCAN_ENABLED"] == "true"
        assert variables["DAST_API_SPECIFICATION"] == "openapi.yaml"


class TestTemplateIntegration:
    """Integration tests for templates."""

    def test_multiple_templates(self):
        """Use multiple templates together."""
        from wetwire_gitlab.templates import DAST, SAST, Build, Deploy, Test

        includes = [
            Build().to_include(),
            Test().to_include(),
            Deploy().to_include(),
            SAST().to_include(),
            DAST().to_include(),
        ]

        assert len(includes) == 5
        templates = [inc["template"] for inc in includes]
        assert "Jobs/Build.gitlab-ci.yml" in templates
        assert "Security/SAST.gitlab-ci.yml" in templates
