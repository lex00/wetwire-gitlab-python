"""Validation module for wetwire-gitlab."""

from .glab import (
    GlabNotFoundError,
    is_glab_installed,
)
from .glab import (
    validate_file as validate_file_glab,
)
from .glab import (
    validate_pipeline as validate_pipeline_glab,
)
from .schema import (
    SchemaFetchError,
    fetch_schema,
    get_cached_schema_path,
    validate_yaml,
)
from .schema import (
    validate_file as validate_file_schema,
)

__all__ = [
    # glab validation
    "GlabNotFoundError",
    "is_glab_installed",
    "validate_file_glab",
    "validate_pipeline_glab",
    # schema validation
    "SchemaFetchError",
    "fetch_schema",
    "get_cached_schema_path",
    "validate_file_schema",
    "validate_yaml",
]
