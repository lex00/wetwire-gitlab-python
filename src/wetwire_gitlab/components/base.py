"""Base class for GitLab CI/CD Component wrappers."""

from dataclasses import dataclass
from typing import Any


@dataclass
class ComponentBase:
    """Base class for GitLab CI/CD component wrappers.

    Attributes:
        version: Component version (default: ~latest).
    """

    version: str = "~latest"

    @property
    def component_path(self) -> str:
        """Return the component path without version."""
        raise NotImplementedError

    def to_include(self) -> dict[str, Any]:
        """Convert to GitLab CI include format.

        Returns:
            Dict suitable for pipeline include array.
        """
        result: dict[str, Any] = {
            "component": f"{self.component_path}@{self.version}",
        }

        inputs = self._get_inputs()
        if inputs:
            result["inputs"] = inputs

        return result

    def _get_inputs(self) -> dict[str, str]:
        """Get component inputs as a dictionary.

        Override in subclasses to provide component-specific inputs.

        Returns:
            Dict of input name to value.
        """
        return {}

    def _format_list(self, items: list[str] | None) -> str | None:
        """Format a list of items as comma-separated string.

        Args:
            items: List of items to format.

        Returns:
            Comma-separated string, or None if items is None/empty.
        """
        if not items:
            return None
        return ",".join(items)

    def _format_bool(self, value: bool | None) -> str | None:
        """Format a boolean as lowercase string.

        Args:
            value: Boolean value.

        Returns:
            "true" or "false", or None if value is None.
        """
        if value is None:
            return None
        return "true" if value else "false"
