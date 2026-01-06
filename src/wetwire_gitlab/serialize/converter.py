"""Converter functions for dataclass to dict conversion."""

from dataclasses import fields, is_dataclass
from typing import Any

from wetwire_gitlab.contracts import JobRef

# Fields that need special name conversion
FIELD_NAME_MAP = {
    "if_": "if",
}


def convert_field_name(name: str) -> str:
    """Convert Python field name to YAML field name.

    Args:
        name: Python field name (e.g., "if_").

    Returns:
        YAML field name (e.g., "if").
    """
    return FIELD_NAME_MAP.get(name, name)


def to_dict(obj: Any) -> dict[str, Any]:
    """Convert a dataclass to a dictionary.

    - Omits None values
    - Converts nested dataclasses recursively
    - Handles JobRef serialization
    - Converts field names (e.g., if_ → if)

    Args:
        obj: A dataclass instance.

    Returns:
        Dictionary representation suitable for YAML serialization.
    """
    if not is_dataclass(obj) or isinstance(obj, type):
        return obj

    result = {}

    for field in fields(obj):
        value = getattr(obj, field.name)

        # Skip None values
        if value is None:
            continue

        # Convert field name
        yaml_name = convert_field_name(field.name)

        # Skip 'name' field for Job (used as YAML key, not in dict)
        if field.name == "name" and hasattr(obj, "script"):
            continue

        # Handle nested dataclasses
        if is_dataclass(value) and not isinstance(value, type):
            result[yaml_name] = to_dict(value)
        # Handle lists
        elif isinstance(value, list):
            result[yaml_name] = [_convert_list_item(item) for item in value]
        # Handle dicts
        elif isinstance(value, dict):
            result[yaml_name] = {k: _convert_list_item(v) for k, v in value.items()}
        else:
            result[yaml_name] = value

    return result


def _convert_list_item(item: Any) -> Any:
    """Convert a list item, handling dataclasses and JobRefs.

    Args:
        item: Any item in a list.

    Returns:
        Converted item suitable for YAML.
    """
    if isinstance(item, JobRef):
        return item.to_dict()
    if is_dataclass(item) and not isinstance(item, type):
        return to_dict(item)
    return item
