"""Linter module for wetwire-gitlab."""

from .linter import fix_code, fix_file, lint_code, lint_directory, lint_file
from .rules import (
    ALL_RULES,
    RULE_REGISTRY,
    LintRule,
    WGL001TypedComponentWrappers,
    WGL002UseRuleDataclass,
    WGL003UsePredefinedVariables,
    WGL004UseCacheDataclass,
    WGL005UseArtifactsDataclass,
    WGL006UseTypedStageConstants,
    WGL007DuplicateJobNames,
    WGL008FileTooLarge,
    WGL009UsePredefinedRules,
    WGL010UseTypedWhenConstants,
    WGL011MissingStage,
    WGL012UseCachePolicyConstants,
    WGL013UseArtifactsWhenConstants,
    WGL014MissingScript,
    WGL015MissingName,
    WGL016UseImageDataclass,
    WGL017EmptyRulesList,
    WGL018NeedsWithoutStage,
    WGL019ManualWithoutAllowFailure,
    WGL020AvoidNestedJobConstructors,
    WGL021UseTypedServiceConstants,
    WGL022AvoidDuplicateNeeds,
    WGL023MissingImageForScriptJobs,
    WGL024CircularDependency,
    WGL025SecretPatternDetection,
)

__all__ = [
    # Protocol
    "LintRule",
    # Registries
    "ALL_RULES",
    "RULE_REGISTRY",
    # Type rules
    "WGL001TypedComponentWrappers",
    "WGL002UseRuleDataclass",
    "WGL003UsePredefinedVariables",
    "WGL004UseCacheDataclass",
    "WGL005UseArtifactsDataclass",
    "WGL006UseTypedStageConstants",
    "WGL012UseCachePolicyConstants",
    "WGL013UseArtifactsWhenConstants",
    "WGL016UseImageDataclass",
    "WGL021UseTypedServiceConstants",
    # Pattern rules
    "WGL009UsePredefinedRules",
    "WGL010UseTypedWhenConstants",
    # File rules
    "WGL007DuplicateJobNames",
    "WGL008FileTooLarge",
    # Job rules
    "WGL011MissingStage",
    "WGL014MissingScript",
    "WGL015MissingName",
    "WGL017EmptyRulesList",
    "WGL018NeedsWithoutStage",
    "WGL019ManualWithoutAllowFailure",
    "WGL020AvoidNestedJobConstructors",
    "WGL022AvoidDuplicateNeeds",
    "WGL023MissingImageForScriptJobs",
    "WGL024CircularDependency",
    "WGL025SecretPatternDetection",
    # Functions
    "fix_code",
    "fix_file",
    "lint_code",
    "lint_directory",
    "lint_file",
]
