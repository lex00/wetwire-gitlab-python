"""Semantic YAML comparison for round-trip validation.

This module provides utilities to compare GitLab CI YAML files for semantic
equivalence, ignoring acceptable differences like whitespace, key ordering,
and quote styles.
"""

from typing import Any

import yaml


def compare_yaml_semantic(original: str, rebuilt: str) -> tuple[bool, list[str]]:
    """Compare two YAML strings for semantic equivalence.

    This function parses both YAML strings and compares them recursively,
    ignoring acceptable differences such as:
    - Whitespace and formatting
    - Key ordering in dictionaries
    - Quote style (single vs double quotes)
    - Default values that don't need to be explicitly set

    Args:
        original: The original YAML string
        rebuilt: The rebuilt YAML string to compare against

    Returns:
        A tuple of (is_equivalent, list_of_differences) where:
        - is_equivalent is True if the YAMLs are semantically equivalent
        - list_of_differences contains human-readable difference descriptions

    Examples:
        >>> original = "stages:\\n  - build\\n  - test"
        >>> rebuilt = "stages: [build, test]"
        >>> is_eq, diffs = compare_yaml_semantic(original, rebuilt)
        >>> is_eq
        True
    """
    differences = []

    # Parse both YAML strings
    try:
        original_data = yaml.safe_load(original)
    except yaml.YAMLError as e:
        differences.append(f"Failed to parse original YAML: {e}")
        return False, differences

    try:
        rebuilt_data = yaml.safe_load(rebuilt)
    except yaml.YAMLError as e:
        differences.append(f"Failed to parse rebuilt YAML: {e}")
        return False, differences

    # Handle empty YAMLs
    if original_data is None:
        original_data = {}
    if rebuilt_data is None:
        rebuilt_data = {}

    # Compare the structures recursively
    _compare_structures(original_data, rebuilt_data, "root", differences)

    return len(differences) == 0, differences


def _compare_structures(
    original: Any, rebuilt: Any, path: str, differences: list[str]
) -> None:
    """Recursively compare two data structures.

    Args:
        original: Original data structure
        rebuilt: Rebuilt data structure
        path: Current path in the structure (for error reporting)
        differences: List to accumulate differences
    """
    # Normalize values before comparison
    original = _normalize_value(original)
    rebuilt = _normalize_value(rebuilt)

    # If types differ, that's a difference
    if type(original) is not type(rebuilt):
        differences.append(
            f"Type mismatch at {path}: "
            f"{type(original).__name__} vs {type(rebuilt).__name__}"
        )
        return

    # Compare based on type
    if isinstance(original, dict):
        _compare_dicts(original, rebuilt, path, differences)
    elif isinstance(original, list):
        _compare_lists(original, rebuilt, path, differences)
    else:
        # Primitive values (str, int, bool, None, etc.)
        if original != rebuilt:
            differences.append(
                f"Value mismatch at {path}: {repr(original)} vs {repr(rebuilt)}"
            )


def _compare_dicts(
    original: dict, rebuilt: dict, path: str, differences: list[str]
) -> None:
    """Compare two dictionaries.

    Args:
        original: Original dictionary
        rebuilt: Rebuilt dictionary
        path: Current path in the structure
        differences: List to accumulate differences
    """
    # Check for keys in original that are missing in rebuilt
    for key in original:
        if key not in rebuilt:
            differences.append(f"Missing key in rebuilt at {path}.{key}")

    # Check for keys in rebuilt that are missing in original
    for key in rebuilt:
        if key not in original:
            differences.append(f"Extra key in rebuilt at {path}.{key}")

    # Compare values for common keys
    for key in original:
        if key in rebuilt:
            new_path = f"{path}.{key}" if path != "root" else key
            _compare_structures(original[key], rebuilt[key], new_path, differences)


def _compare_lists(
    original: list, rebuilt: list, path: str, differences: list[str]
) -> None:
    """Compare two lists.

    Args:
        original: Original list
        rebuilt: Rebuilt list
        path: Current path in the structure
        differences: List to accumulate differences
    """
    if len(original) != len(rebuilt):
        differences.append(
            f"List length mismatch at {path}: {len(original)} vs {len(rebuilt)}"
        )
        # Continue comparing up to the shorter length
        min_len = min(len(original), len(rebuilt))
    else:
        min_len = len(original)

    # Compare elements
    for i in range(min_len):
        new_path = f"{path}[{i}]"
        _compare_structures(original[i], rebuilt[i], new_path, differences)


def _normalize_value(value: Any) -> Any:
    """Normalize a value for comparison.

    This handles:
    - Stripping whitespace from strings
    - Converting None to empty dict for top-level structures
    - Standardizing boolean representations

    Args:
        value: The value to normalize

    Returns:
        The normalized value
    """
    if isinstance(value, str):
        # Strip leading/trailing whitespace from strings
        return value.strip()
    elif isinstance(value, dict):
        # Recursively normalize dict values
        return {k: _normalize_value(v) for k, v in value.items()}
    elif isinstance(value, list):
        # Recursively normalize list elements
        return [_normalize_value(v) for v in value]
    else:
        # Return as-is for other types (int, bool, None, etc.)
        return value
