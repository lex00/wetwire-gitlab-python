"""Code Quality component wrapper."""

from dataclasses import dataclass

from .base import ComponentBase


@dataclass
class CodeQualityComponent(ComponentBase):
    """GitLab Code Quality component wrapper.

    Analyzes your source code quality using Code Climate.

    See: https://docs.gitlab.com/ee/ci/testing/code_quality.html

    Attributes:
        source_code_dir: Source code directory to analyze.
        code_quality_disabled: Disable Code Quality scanning.
        version: Component version.
    """

    source_code_dir: str | None = None
    code_quality_disabled: bool | None = None

    @property
    def component_path(self) -> str:
        return "gitlab.com/components/code-quality"

    def _get_inputs(self) -> dict[str, str]:
        inputs: dict[str, str] = {}

        if self.source_code_dir:
            inputs["SOURCE_CODE_DIR"] = self.source_code_dir

        disabled = self._format_bool(self.code_quality_disabled)
        if disabled:
            inputs["CODE_QUALITY_DISABLED"] = disabled

        return inputs
