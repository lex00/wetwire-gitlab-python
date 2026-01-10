"""Coverage Report component wrapper."""

from dataclasses import dataclass

from .base import ComponentBase


@dataclass
class CoverageComponent(ComponentBase):
    """GitLab Coverage Report component wrapper.

    Generates and reports code coverage information.

    See: https://docs.gitlab.com/ee/ci/testing/code_coverage.html

    Attributes:
        coverage_artifact_path: Path to coverage artifacts.
        coverage_report_format: Coverage report format (cobertura, jacoco, etc.).
        version: Component version.
    """

    coverage_artifact_path: str | None = None
    coverage_report_format: str | None = None

    @property
    def component_path(self) -> str:
        return "gitlab.com/components/coverage-report"

    def _get_inputs(self) -> dict[str, str]:
        inputs: dict[str, str] = {}

        if self.coverage_artifact_path:
            inputs["COVERAGE_ARTIFACT_PATH"] = self.coverage_artifact_path

        if self.coverage_report_format:
            inputs["COVERAGE_REPORT_FORMAT"] = self.coverage_report_format

        return inputs
