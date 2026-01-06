"""Pipeline types for GitLab CI configuration."""

from .artifacts import Artifacts
from .cache import Cache, CacheKey
from .default import Default
from .image import Image
from .include import Include
from .job import Job
from .pipeline import Pipeline
from .rules import Rule
from .trigger import Trigger
from .variables import Variable, Variables
from .workflow import Workflow

__all__ = [
    "Artifacts",
    "Cache",
    "CacheKey",
    "Default",
    "Image",
    "Include",
    "Job",
    "Pipeline",
    "Rule",
    "Trigger",
    "Variable",
    "Variables",
    "Workflow",
]
