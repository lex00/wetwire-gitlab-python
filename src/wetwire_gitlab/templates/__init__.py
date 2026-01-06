"""GitLab Auto DevOps templates module.

This module provides typed wrappers for GitLab Auto DevOps templates,
making it easy to include standard GitLab CI/CD templates with type safety.
"""

from .auto_devops import AutoDevOps
from .jobs import DAST, SAST, Build, Deploy, Test

__all__ = [
    "AutoDevOps",
    "Build",
    "DAST",
    "Deploy",
    "SAST",
    "Test",
]
