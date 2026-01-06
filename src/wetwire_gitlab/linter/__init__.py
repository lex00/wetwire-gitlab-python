"""Linter module for wetwire-gitlab."""

from .linter import lint_directory, lint_file
from .rules import (
    ALL_RULES,
    RULE_REGISTRY,
    WGL001TypedComponentWrappers,
    WGL002UseRuleDataclass,
    WGL003UsePredefinedVariables,
    WGL004UseCacheDataclass,
    WGL005UseArtifactsDataclass,
    WGL006UseTypedStageConstants,
    WGL007DuplicateJobNames,
    WGL008FileTooLarge,
)

__all__ = [
    "ALL_RULES",
    "RULE_REGISTRY",
    "WGL001TypedComponentWrappers",
    "WGL002UseRuleDataclass",
    "WGL003UsePredefinedVariables",
    "WGL004UseCacheDataclass",
    "WGL005UseArtifactsDataclass",
    "WGL006UseTypedStageConstants",
    "WGL007DuplicateJobNames",
    "WGL008FileTooLarge",
    "lint_directory",
    "lint_file",
]
