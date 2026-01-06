"""Default job configuration for GitLab CI pipelines."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .artifacts import Artifacts
    from .cache import Cache
    from .image import Image


@dataclass
class Default:
    """Default configuration applied to all jobs.

    Attributes:
        image: Default Docker image.
        before_script: Default before_script commands.
        after_script: Default after_script commands.
        artifacts: Default artifacts configuration.
        cache: Default cache configuration.
        tags: Default runner tags.
        services: Default services.
        timeout: Default job timeout.
        retry: Default retry configuration.
        interruptible: Default interruptible setting.
        id_tokens: Default ID tokens configuration.
    """

    image: Image | None = None
    before_script: list[str] | None = None
    after_script: list[str] | None = None
    artifacts: Artifacts | None = None
    cache: Cache | list[Cache] | None = None
    tags: list[str] | None = None
    services: list[str | dict[str, Any]] | None = None
    timeout: str | None = None
    retry: int | dict[str, Any] | None = None
    interruptible: bool | None = None
    id_tokens: dict[str, Any] | None = None
