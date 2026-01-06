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
