"""Lint rules for pipeline definitions.

This package contains categorized lint rules:
- type_rules: Rules for using typed constants and dataclasses
- pattern_rules: Rules for using predefined patterns
- file_rules: File-level rules
- job_rules: Job validation rules
"""

from .base import LintRule
from .file_rules import WGL007DuplicateJobNames, WGL008FileTooLarge
from .job_rules import (
    WGL011MissingStage,
    WGL014MissingScript,
    WGL015MissingName,
    WGL017EmptyRulesList,
    WGL018NeedsWithoutStage,
    WGL019ManualWithoutAllowFailure,
    WGL020AvoidNestedJobConstructors,
    WGL022AvoidDuplicateNeeds,
    WGL023MissingImageForScriptJobs,
)
from .pattern_rules import WGL009UsePredefinedRules, WGL010UseTypedWhenConstants
from .type_rules import (
    WGL001TypedComponentWrappers,
    WGL002UseRuleDataclass,
    WGL003UsePredefinedVariables,
    WGL004UseCacheDataclass,
    WGL005UseArtifactsDataclass,
    WGL006UseTypedStageConstants,
    WGL012UseCachePolicyConstants,
    WGL013UseArtifactsWhenConstants,
    WGL016UseImageDataclass,
    WGL021UseTypedServiceConstants,
)

# All available rules
ALL_RULES: list[type] = [
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
]

# Rule code to class mapping
RULE_REGISTRY: dict[str, type] = {
    "WGL001": WGL001TypedComponentWrappers,
    "WGL002": WGL002UseRuleDataclass,
    "WGL003": WGL003UsePredefinedVariables,
    "WGL004": WGL004UseCacheDataclass,
    "WGL005": WGL005UseArtifactsDataclass,
    "WGL006": WGL006UseTypedStageConstants,
    "WGL007": WGL007DuplicateJobNames,
    "WGL008": WGL008FileTooLarge,
    "WGL009": WGL009UsePredefinedRules,
    "WGL010": WGL010UseTypedWhenConstants,
    "WGL011": WGL011MissingStage,
    "WGL012": WGL012UseCachePolicyConstants,
    "WGL013": WGL013UseArtifactsWhenConstants,
    "WGL014": WGL014MissingScript,
    "WGL015": WGL015MissingName,
    "WGL016": WGL016UseImageDataclass,
    "WGL017": WGL017EmptyRulesList,
    "WGL018": WGL018NeedsWithoutStage,
    "WGL019": WGL019ManualWithoutAllowFailure,
    "WGL020": WGL020AvoidNestedJobConstructors,
    "WGL021": WGL021UseTypedServiceConstants,
    "WGL022": WGL022AvoidDuplicateNeeds,
    "WGL023": WGL023MissingImageForScriptJobs,
}

__all__ = [
    # Protocol
    "LintRule",
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
    # Registries
    "ALL_RULES",
    "RULE_REGISTRY",
]
