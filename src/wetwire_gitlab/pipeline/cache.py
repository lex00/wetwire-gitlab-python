"""Cache configuration for GitLab CI jobs."""

from dataclasses import dataclass


@dataclass
class CacheKey:
    """Cache key configuration.

    Attributes:
        files: List of files to use for key generation.
        prefix: Prefix for the cache key.
    """

    files: list[str] | None = None
    prefix: str | None = None


@dataclass
class Cache:
    """Cache configuration for a job.

    Attributes:
        paths: List of paths to cache.
        key: Cache key (string or CacheKey object).
        untracked: Cache git-untracked files.
        unprotect: Allow unprotected branches to use cache.
        when: When to save cache (on_success, on_failure, always).
        policy: Cache policy (pull, push, pull-push).
        fallback_keys: List of fallback cache keys.
    """

    paths: list[str] | None = None
    key: str | CacheKey | None = None
    untracked: bool | None = None
    unprotect: bool | None = None
    when: str | None = None
    policy: str | None = None
    fallback_keys: list[str] | None = None
