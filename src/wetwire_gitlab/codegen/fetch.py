"""Schema and component specification fetching for wetwire-gitlab.

This module provides functionality to fetch:
- GitLab CI schema from gitlab-org/gitlab repository
- CI/CD Component specifications from gitlab.com/components/*
"""

import json
import time
import urllib.request
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

# GitLab CI schema URL
CI_SCHEMA_URL = (
    "https://gitlab.com/gitlab-org/gitlab/-/raw/master/"
    "app/assets/javascripts/editor/schema/ci.json"
)

# CI/CD Component URLs (gitlab.com/components/*)
COMPONENT_URLS = {
    "sast": "https://gitlab.com/components/sast/-/raw/main/template.yml",
    "secret-detection": "https://gitlab.com/components/secret-detection/-/raw/main/template.yml",
    "dependency-scanning": "https://gitlab.com/components/dependency-scanning/-/raw/main/template.yml",
    "container-scanning": "https://gitlab.com/components/container-scanning/-/raw/main/template.yml",
    "dast": "https://gitlab.com/components/dast/-/raw/main/template.yml",
    "license-scanning": "https://gitlab.com/components/license-scanning/-/raw/main/template.yml",
    "coverage-report": "https://gitlab.com/components/coverage-report/-/raw/main/template.yml",
}


class FetchError(Exception):
    """Exception raised when fetching fails."""

    pass


def fetch_url(url: str, retries: int = 3, delay: float = 1.0) -> str:
    """Fetch content from a URL with retry logic.

    Args:
        url: The URL to fetch.
        retries: Number of retry attempts.
        delay: Delay between retries in seconds.

    Returns:
        The content as a string.

    Raises:
        FetchError: If all retries fail.
    """
    last_error = None

    for attempt in range(retries):
        try:
            with urllib.request.urlopen(url, timeout=30) as response:
                return response.read().decode("utf-8")
        except Exception as e:
            last_error = e
            if attempt < retries - 1:
                time.sleep(delay)

    raise FetchError(f"Failed to fetch {url} after {retries} attempts: {last_error}")


def fetch_ci_schema() -> dict[str, Any]:
    """Fetch the GitLab CI schema.

    Returns:
        Parsed JSON schema as a dictionary.

    Raises:
        FetchError: If fetching fails.
    """
    content = fetch_url(CI_SCHEMA_URL)
    return json.loads(content)


def fetch_component_spec(component: str) -> str:
    """Fetch a component specification.

    Args:
        component: Component name (e.g., "sast", "dast").

    Returns:
        The component specification content.

    Raises:
        FetchError: If the component is unknown or fetching fails.
    """
    if component not in COMPONENT_URLS:
        raise FetchError(
            f"Unknown component: {component}. "
            f"Available: {', '.join(COMPONENT_URLS.keys())}"
        )

    return fetch_url(COMPONENT_URLS[component])


def fetch_all_schemas(specs_dir: Path) -> dict[str, Any]:
    """Fetch all schemas and component specs.

    Args:
        specs_dir: Directory to save fetched schemas.

    Returns:
        Dictionary with fetch status for each schema.
    """
    specs_dir.mkdir(parents=True, exist_ok=True)
    components_dir = specs_dir / "components"
    components_dir.mkdir(exist_ok=True)

    result: dict[str, Any] = {
        "ci_schema": False,
        "components": {},
    }

    # Fetch CI schema
    try:
        schema = fetch_ci_schema()
        schema_path = specs_dir / "ci-schema.json"
        with open(schema_path, "w") as f:
            json.dump(schema, f, indent=2)
        result["ci_schema"] = True
    except FetchError as e:
        result["ci_schema_error"] = str(e)

    # Fetch component specs
    for component in COMPONENT_URLS:
        try:
            spec = fetch_component_spec(component)
            spec_path = components_dir / f"{component}.yml"
            with open(spec_path, "w") as f:
                f.write(spec)
            result["components"][component] = True
        except FetchError as e:
            result["components"][component] = False
            result.setdefault("component_errors", {})[component] = str(e)

    # Create manifest
    create_manifest(
        specs_dir,
        ci_schema=result["ci_schema"],
        components=result["components"],
    )

    return result


def create_manifest(
    specs_dir: Path,
    ci_schema: bool,
    components: dict[str, bool],
) -> None:
    """Create or update the manifest file.

    Args:
        specs_dir: Directory containing specs.
        ci_schema: Whether CI schema was fetched.
        components: Dictionary of component fetch status.
    """
    manifest = {
        "version": "1.0",
        "fetched_at": datetime.now(UTC).isoformat(),
        "ci_schema": ci_schema,
        "components": components,
    }

    manifest_path = specs_dir / "manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)


def load_manifest(specs_dir: Path) -> dict[str, Any] | None:
    """Load the manifest file if it exists.

    Args:
        specs_dir: Directory containing specs.

    Returns:
        Manifest dictionary or None if not found.
    """
    manifest_path = specs_dir / "manifest.json"

    if not manifest_path.exists():
        return None

    with open(manifest_path) as f:
        return json.load(f)
