"""Monorepo CI/CD pipeline."""

from .jobs import detect_changes, trigger_backend, trigger_frontend, trigger_shared
from .pipeline import pipeline

__all__ = [
    "detect_changes",
    "pipeline",
    "trigger_backend",
    "trigger_frontend",
    "trigger_shared",
]
