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

__all__ = [
    "CI_SCHEMA_URL",
    "COMPONENT_URLS",
    "FetchError",
    "create_manifest",
    "fetch_all_schemas",
    "fetch_ci_schema",
    "fetch_component_spec",
    "fetch_url",
    "load_manifest",
]
