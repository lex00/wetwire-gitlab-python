"""Base class and protocol for lint rules."""

import ast
from pathlib import Path
from typing import Protocol

from ...contracts import LintIssue


class LintRule(Protocol):
    """Protocol for lint rules."""

    code: str
    message: str

    def check(self, tree: ast.AST, file_path: Path) -> list[LintIssue]:
        """Check the AST for violations.

        Args:
            tree: Parsed AST of the Python file.
            file_path: Path to the file being checked.

        Returns:
            List of lint issues found.
        """
        ...
