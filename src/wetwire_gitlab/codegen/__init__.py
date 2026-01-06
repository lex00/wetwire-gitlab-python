"""Code generation module for wetwire-gitlab."""

from .fetch import (
    CI_SCHEMA_URL,
    COMPONENT_URLS,
    FetchError,
    create_manifest,
    fetch_all_schemas,
    fetch_ci_schema,
    fetch_component_spec,
    fetch_url,
    load_manifest,
)
from .generate import (
    component_to_class_name,
    component_to_module_name,
    generate_all_components,
    generate_component_code,
    generate_component_module,
    generate_component_module_file,
    generate_init_file,
)
from .parse import (
    ComponentIR,
    InputIR,
    ParsedSchemas,
    PropertyIR,
    SchemaDefinitionIR,
    SchemaIR,
    parse_all_schemas,
    parse_ci_schema,
    parse_ci_schema_file,
    parse_component_spec,
    parse_component_spec_file,
)

__all__ = [
    # fetch
    "CI_SCHEMA_URL",
    "COMPONENT_URLS",
    "FetchError",
    "create_manifest",
    "fetch_all_schemas",
    "fetch_ci_schema",
    "fetch_component_spec",
    "fetch_url",
    "load_manifest",
    # generate
    "component_to_class_name",
    "component_to_module_name",
    "generate_all_components",
    "generate_component_code",
    "generate_component_module",
    "generate_component_module_file",
    "generate_init_file",
    # parse
    "ComponentIR",
    "InputIR",
    "ParsedSchemas",
    "PropertyIR",
    "SchemaDefinitionIR",
    "SchemaIR",
    "parse_all_schemas",
    "parse_ci_schema",
    "parse_ci_schema_file",
    "parse_component_spec",
    "parse_component_spec_file",
]
