"""Schema and component specification parsing for wetwire-gitlab.

This module provides functionality to parse:
- GitLab CI JSON schema into intermediate representation
- CI/CD Component YAML specs into intermediate representation
"""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class PropertyIR:
    """Intermediate representation for a schema property.

    Attributes:
        name: Property name.
        type_: Property type (string, array, object, etc.).
        description: Property description.
        enum: List of allowed values if enum type.
        items: Item type for array properties.
        ref: Reference to another definition.
    """

    name: str
    type_: str | None = None
    description: str | None = None
    enum: list[str] | None = None
    items: dict[str, Any] | None = None
    ref: str | None = None


@dataclass
class SchemaDefinitionIR:
    """Intermediate representation for a schema definition.

    Attributes:
        name: Definition name.
        type_: Definition type.
        properties: Dictionary of property names to PropertyIR.
        required: List of required property names.
        description: Definition description.
    """

    name: str
    type_: str | None = None
    properties: dict[str, PropertyIR] = field(default_factory=dict)
    required: list[str] = field(default_factory=list)
    description: str | None = None


@dataclass
class SchemaIR:
    """Intermediate representation for the full CI schema.

    Attributes:
        definitions: Dictionary of definition names to SchemaDefinitionIR.
        root_properties: Top-level schema properties.
    """

    definitions: dict[str, SchemaDefinitionIR] = field(default_factory=dict)
    root_properties: dict[str, PropertyIR] = field(default_factory=dict)


@dataclass
class InputIR:
    """Intermediate representation for a component input.

    Attributes:
        name: Input name.
        default: Default value (None means required).
        description: Input description.
        type_: Input type.
        options: List of allowed values.
    """

    name: str
    default: str | None = None
    description: str | None = None
    type_: str | None = None
    options: list[str] | None = None

    @property
    def is_optional(self) -> bool:
        """Check if this input is optional (has a default)."""
        return self.default is not None


@dataclass
class ComponentIR:
    """Intermediate representation for a component specification.

    Attributes:
        name: Component name.
        inputs: List of InputIR for component inputs.
        description: Component description.
    """

    name: str
    inputs: list[InputIR] = field(default_factory=list)
    description: str | None = None


@dataclass
class ParsedSchemas:
    """Container for all parsed schemas.

    Attributes:
        ci_schema: Parsed CI schema.
        components: Dictionary of component names to ComponentIR.
    """

    ci_schema: SchemaIR | None = None
    components: dict[str, ComponentIR] = field(default_factory=dict)


def _parse_property(name: str, prop_data: dict[str, Any]) -> PropertyIR:
    """Parse a single property from schema.

    Args:
        name: Property name.
        prop_data: Property data from schema.

    Returns:
        PropertyIR instance.
    """
    return PropertyIR(
        name=name,
        type_=prop_data.get("type"),
        description=prop_data.get("description"),
        enum=prop_data.get("enum"),
        items=prop_data.get("items"),
        ref=prop_data.get("$ref"),
    )


def _parse_definition(name: str, def_data: dict[str, Any]) -> SchemaDefinitionIR:
    """Parse a single definition from schema.

    Args:
        name: Definition name.
        def_data: Definition data from schema.

    Returns:
        SchemaDefinitionIR instance.
    """
    properties = {}
    if "properties" in def_data:
        for prop_name, prop_data in def_data["properties"].items():
            properties[prop_name] = _parse_property(prop_name, prop_data)

    return SchemaDefinitionIR(
        name=name,
        type_=def_data.get("type"),
        properties=properties,
        required=def_data.get("required", []),
        description=def_data.get("description"),
    )


def parse_ci_schema(schema: dict[str, Any]) -> SchemaIR:
    """Parse CI schema JSON into intermediate representation.

    Args:
        schema: Parsed JSON schema.

    Returns:
        SchemaIR instance.
    """
    definitions = {}

    # Parse definitions
    if "definitions" in schema:
        for name, def_data in schema["definitions"].items():
            definitions[name] = _parse_definition(name, def_data)

    # Parse root properties
    root_properties = {}
    if "properties" in schema:
        for name, prop_data in schema["properties"].items():
            root_properties[name] = _parse_property(name, prop_data)

    return SchemaIR(
        definitions=definitions,
        root_properties=root_properties,
    )


def parse_ci_schema_file(path: Path) -> SchemaIR:
    """Parse CI schema from a file.

    Args:
        path: Path to ci-schema.json file.

    Returns:
        SchemaIR instance.
    """
    with open(path) as f:
        schema = json.load(f)
    return parse_ci_schema(schema)


def _parse_input(name: str, input_data: dict[str, Any]) -> InputIR:
    """Parse a single component input.

    Args:
        name: Input name.
        input_data: Input data from spec.

    Returns:
        InputIR instance.
    """
    return InputIR(
        name=name,
        default=input_data.get("default"),
        description=input_data.get("description"),
        type_=input_data.get("type"),
        options=input_data.get("options"),
    )


def parse_component_spec(content: str) -> ComponentIR:
    """Parse component specification YAML into intermediate representation.

    Args:
        content: YAML content as string.

    Returns:
        ComponentIR instance.
    """
    data = yaml.safe_load(content)

    inputs = []
    if data and "spec" in data and "inputs" in data["spec"]:
        for name, input_data in data["spec"]["inputs"].items():
            inputs.append(_parse_input(name, input_data or {}))

    return ComponentIR(
        name="",  # Will be set by caller
        inputs=inputs,
    )


def parse_component_spec_file(path: Path) -> ComponentIR:
    """Parse component specification from a file.

    Args:
        path: Path to component YAML file.

    Returns:
        ComponentIR instance.
    """
    with open(path) as f:
        content = f.read()

    component = parse_component_spec(content)
    component.name = path.stem  # Use filename as component name
    return component


def parse_all_schemas(specs_dir: Path) -> ParsedSchemas:
    """Parse all schemas in the specs directory.

    Args:
        specs_dir: Directory containing fetched schemas.

    Returns:
        ParsedSchemas instance with all parsed data.
    """
    result = ParsedSchemas()

    # Parse CI schema if it exists
    ci_schema_path = specs_dir / "ci-schema.json"
    if ci_schema_path.exists():
        result.ci_schema = parse_ci_schema_file(ci_schema_path)

    # Parse component specs
    components_dir = specs_dir / "components"
    if components_dir.exists():
        for spec_file in components_dir.glob("*.yml"):
            component = parse_component_spec_file(spec_file)
            result.components[component.name] = component

    return result
