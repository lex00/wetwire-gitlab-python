"""Intrinsics module for GitLab CI predefined variables and helpers.

This module provides:
- CI, GitLab, MR context classes for accessing predefined variables
- When, CachePolicy, and other constant enums
- Predefined rule helpers (on_default_branch, on_tag, etc.)
"""

from wetwire_gitlab.pipeline import Rule


class _CIContext:
    """CI predefined variables context.

    Provides access to CI_* predefined variables via attribute access.
    Example: CI.commit_sha returns "$CI_COMMIT_SHA"
    """

    @property
    def commit_sha(self) -> str:
        """The commit revision the project is built for."""
        return "$CI_COMMIT_SHA"

    @property
    def commit_short_sha(self) -> str:
        """The first 8 characters of CI_COMMIT_SHA."""
        return "$CI_COMMIT_SHORT_SHA"

    @property
    def commit_ref_name(self) -> str:
        """The branch or tag name for which project is built."""
        return "$CI_COMMIT_REF_NAME"

    @property
    def commit_ref_slug(self) -> str:
        """CI_COMMIT_REF_NAME in lowercase, shortened to 63 bytes."""
        return "$CI_COMMIT_REF_SLUG"

    @property
    def commit_branch(self) -> str:
        """The commit branch name. Available for branch pipelines."""
        return "$CI_COMMIT_BRANCH"

    @property
    def commit_tag(self) -> str:
        """The commit tag name. Available for tag pipelines."""
        return "$CI_COMMIT_TAG"

    @property
    def commit_message(self) -> str:
        """The full commit message."""
        return "$CI_COMMIT_MESSAGE"

    @property
    def commit_title(self) -> str:
        """The title of the commit (first line of message)."""
        return "$CI_COMMIT_TITLE"

    @property
    def default_branch(self) -> str:
        """The name of the project's default branch."""
        return "$CI_DEFAULT_BRANCH"

    @property
    def pipeline_id(self) -> str:
        """The unique ID of the current pipeline."""
        return "$CI_PIPELINE_ID"

    @property
    def pipeline_iid(self) -> str:
        """The project-level unique ID of the current pipeline."""
        return "$CI_PIPELINE_IID"

    @property
    def pipeline_source(self) -> str:
        """How the pipeline was triggered."""
        return "$CI_PIPELINE_SOURCE"

    @property
    def pipeline_url(self) -> str:
        """The URL for the pipeline details."""
        return "$CI_PIPELINE_URL"

    @property
    def job_id(self) -> str:
        """The unique ID of the current job."""
        return "$CI_JOB_ID"

    @property
    def job_name(self) -> str:
        """The name of the job."""
        return "$CI_JOB_NAME"

    @property
    def job_stage(self) -> str:
        """The name of the stage."""
        return "$CI_JOB_STAGE"

    @property
    def job_token(self) -> str:
        """Token to authenticate with certain API endpoints."""
        return "$CI_JOB_TOKEN"

    @property
    def job_url(self) -> str:
        """The URL for the job details."""
        return "$CI_JOB_URL"

    @property
    def project_id(self) -> str:
        """The unique ID of the current project."""
        return "$CI_PROJECT_ID"

    @property
    def project_name(self) -> str:
        """The name of the project (directory name)."""
        return "$CI_PROJECT_NAME"

    @property
    def project_namespace(self) -> str:
        """The namespace (group/subgroup path)."""
        return "$CI_PROJECT_NAMESPACE"

    @property
    def project_path(self) -> str:
        """The full project path (namespace/name)."""
        return "$CI_PROJECT_PATH"

    @property
    def project_path_slug(self) -> str:
        """CI_PROJECT_PATH in lowercase, shortened to 63 bytes."""
        return "$CI_PROJECT_PATH_SLUG"

    @property
    def project_url(self) -> str:
        """The HTTP URL for the project."""
        return "$CI_PROJECT_URL"

    @property
    def project_dir(self) -> str:
        """The full directory path where the repository is cloned."""
        return "$CI_PROJECT_DIR"

    @property
    def registry(self) -> str:
        """The address of the container registry."""
        return "$CI_REGISTRY"

    @property
    def registry_image(self) -> str:
        """The registry address with project path for container images."""
        return "$CI_REGISTRY_IMAGE"

    @property
    def registry_user(self) -> str:
        """The username to push containers to the project registry."""
        return "$CI_REGISTRY_USER"

    @property
    def registry_password(self) -> str:
        """The password to push containers to the project registry."""
        return "$CI_REGISTRY_PASSWORD"

    @property
    def server_host(self) -> str:
        """The host of the GitLab instance URL."""
        return "$CI_SERVER_HOST"

    @property
    def server_url(self) -> str:
        """The base URL of the GitLab instance."""
        return "$CI_SERVER_URL"

    @property
    def environment_name(self) -> str:
        """The name of the environment for this job."""
        return "$CI_ENVIRONMENT_NAME"

    @property
    def environment_slug(self) -> str:
        """The simplified version of the environment name."""
        return "$CI_ENVIRONMENT_SLUG"

    @property
    def environment_url(self) -> str:
        """The URL of the environment for this job."""
        return "$CI_ENVIRONMENT_URL"

    @property
    def commit_before_sha(self) -> str:
        """The previous latest commit present on a branch before a push."""
        return "$CI_COMMIT_BEFORE_SHA"

    # PascalCase aliases for convenience
    COMMIT_SHA = property(lambda self: self.commit_sha)
    COMMIT_SHORT_SHA = property(lambda self: self.commit_short_sha)
    COMMIT_REF_NAME = property(lambda self: self.commit_ref_name)
    COMMIT_REF_SLUG = property(lambda self: self.commit_ref_slug)
    COMMIT_BRANCH = property(lambda self: self.commit_branch)
    COMMIT_TAG = property(lambda self: self.commit_tag)
    COMMIT_MESSAGE = property(lambda self: self.commit_message)
    COMMIT_TITLE = property(lambda self: self.commit_title)
    COMMIT_BEFORE_SHA = property(lambda self: self.commit_before_sha)
    DEFAULT_BRANCH = property(lambda self: self.default_branch)
    PIPELINE_ID = property(lambda self: self.pipeline_id)
    PIPELINE_IID = property(lambda self: self.pipeline_iid)
    PIPELINE_SOURCE = property(lambda self: self.pipeline_source)
    PIPELINE_URL = property(lambda self: self.pipeline_url)
    JOB_ID = property(lambda self: self.job_id)
    JOB_NAME = property(lambda self: self.job_name)
    JOB_STAGE = property(lambda self: self.job_stage)
    JOB_TOKEN = property(lambda self: self.job_token)
    JOB_URL = property(lambda self: self.job_url)
    PROJECT_ID = property(lambda self: self.project_id)
    PROJECT_NAME = property(lambda self: self.project_name)
    PROJECT_NAMESPACE = property(lambda self: self.project_namespace)
    PROJECT_PATH = property(lambda self: self.project_path)
    PROJECT_PATH_SLUG = property(lambda self: self.project_path_slug)
    PROJECT_URL = property(lambda self: self.project_url)
    PROJECT_DIR = property(lambda self: self.project_dir)
    REGISTRY = property(lambda self: self.registry)
    REGISTRY_IMAGE = property(lambda self: self.registry_image)
    REGISTRY_USER = property(lambda self: self.registry_user)
    REGISTRY_PASSWORD = property(lambda self: self.registry_password)
    SERVER_HOST = property(lambda self: self.server_host)
    SERVER_URL = property(lambda self: self.server_url)
    ENVIRONMENT_NAME = property(lambda self: self.environment_name)
    ENVIRONMENT_SLUG = property(lambda self: self.environment_slug)
    ENVIRONMENT_URL = property(lambda self: self.environment_url)


class _GitLabContext:
    """GitLab predefined variables context.

    Provides access to GITLAB_* predefined variables via attribute access.
    Example: GitLab.user_login returns "$GITLAB_USER_LOGIN"
    """

    @property
    def user_login(self) -> str:
        """The username of the user who triggered the pipeline."""
        return "$GITLAB_USER_LOGIN"

    @property
    def user_email(self) -> str:
        """The email of the user who triggered the pipeline."""
        return "$GITLAB_USER_EMAIL"

    @property
    def user_name(self) -> str:
        """The name of the user who triggered the pipeline."""
        return "$GITLAB_USER_NAME"

    @property
    def user_id(self) -> str:
        """The ID of the user who triggered the pipeline."""
        return "$GITLAB_USER_ID"

    @property
    def features(self) -> str:
        """The feature flags enabled for the project."""
        return "$GITLAB_FEATURES"


class _MRContext:
    """Merge Request predefined variables context.

    Provides access to CI_MERGE_REQUEST_* predefined variables via attribute access.
    Example: MR.iid returns "$CI_MERGE_REQUEST_IID"
    """

    @property
    def iid(self) -> str:
        """The project-level IID of the merge request."""
        return "$CI_MERGE_REQUEST_IID"

    @property
    def id(self) -> str:
        """The instance-level ID of the merge request."""
        return "$CI_MERGE_REQUEST_ID"

    @property
    def source_branch(self) -> str:
        """The source branch name of the merge request."""
        return "$CI_MERGE_REQUEST_SOURCE_BRANCH_NAME"

    @property
    def source_branch_sha(self) -> str:
        """The HEAD SHA of the source branch."""
        return "$CI_MERGE_REQUEST_SOURCE_BRANCH_SHA"

    @property
    def target_branch(self) -> str:
        """The target branch name of the merge request."""
        return "$CI_MERGE_REQUEST_TARGET_BRANCH_NAME"

    @property
    def target_branch_sha(self) -> str:
        """The HEAD SHA of the target branch."""
        return "$CI_MERGE_REQUEST_TARGET_BRANCH_SHA"

    @property
    def title(self) -> str:
        """The title of the merge request."""
        return "$CI_MERGE_REQUEST_TITLE"

    @property
    def description(self) -> str:
        """The description of the merge request."""
        return "$CI_MERGE_REQUEST_DESCRIPTION"

    @property
    def labels(self) -> str:
        """The comma-separated list of labels."""
        return "$CI_MERGE_REQUEST_LABELS"

    @property
    def milestone(self) -> str:
        """The milestone title."""
        return "$CI_MERGE_REQUEST_MILESTONE"

    @property
    def project_id(self) -> str:
        """The ID of the project of the merge request."""
        return "$CI_MERGE_REQUEST_PROJECT_ID"

    @property
    def project_path(self) -> str:
        """The path of the project of the merge request."""
        return "$CI_MERGE_REQUEST_PROJECT_PATH"

    @property
    def project_url(self) -> str:
        """The URL of the project of the merge request."""
        return "$CI_MERGE_REQUEST_PROJECT_URL"


# Singleton instances for context classes
CI = _CIContext()
GitLab = _GitLabContext()
MR = _MRContext()


class When:
    """Constants for the 'when' keyword."""

    ALWAYS = "always"
    NEVER = "never"
    ON_SUCCESS = "on_success"
    ON_FAILURE = "on_failure"
    MANUAL = "manual"
    DELAYED = "delayed"


class CachePolicy:
    """Constants for cache policy."""

    PULL = "pull"
    PUSH = "push"
    PULL_PUSH = "pull-push"


class ArtifactsWhen:
    """Constants for artifacts 'when' keyword."""

    ON_SUCCESS = "on_success"
    ON_FAILURE = "on_failure"
    ALWAYS = "always"


class PipelineSource:
    """Constants for pipeline source values."""

    PUSH = "push"
    MERGE_REQUEST_EVENT = "merge_request_event"
    SCHEDULE = "schedule"
    WEB = "web"
    API = "api"
    TRIGGER = "trigger"
    PIPELINE = "pipeline"
    PARENT_PIPELINE = "parent_pipeline"
    CHAT = "chat"
    WEBIDE = "webide"
    EXTERNAL = "external"
    EXTERNAL_PULL_REQUEST_EVENT = "external_pull_request_event"


# Predefined rule helpers
on_default_branch = Rule(
    if_="$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH",
)

on_tag = Rule(
    if_="$CI_COMMIT_TAG",
)

on_merge_request = Rule(
    if_='$CI_PIPELINE_SOURCE == "merge_request_event"',
)

manual_only = Rule(
    when="manual",
)

always = Rule(
    when="always",
)

never = Rule(
    when="never",
)


class Rules:
    """Collection of predefined rules for common use cases."""

    ON_DEFAULT_BRANCH = on_default_branch
    ON_TAG = on_tag
    ON_MERGE_REQUEST = on_merge_request
    MANUAL = manual_only
    ALWAYS = always
    NEVER = never


class Images:
    """Common Docker images for GitLab CI jobs.

    Provides typed constants for popular Docker images used in CI/CD pipelines.
    Use these constants instead of hardcoded strings.
    """

    # Python images
    PYTHON_3_11 = "python:3.11"
    PYTHON_3_11_SLIM = "python:3.11-slim"
    PYTHON_3_12 = "python:3.12"
    PYTHON_3_12_SLIM = "python:3.12-slim"
    PYTHON_3_13 = "python:3.13"

    # Node.js images
    NODE_18 = "node:18"
    NODE_20 = "node:20"
    NODE_20_ALPINE = "node:20-alpine"

    # Go images
    GO_1_21 = "golang:1.21"
    GO_1_22 = "golang:1.22"
    GO_1_23 = "golang:1.23"

    # Ruby images
    RUBY_3_2 = "ruby:3.2"
    RUBY_3_3 = "ruby:3.3"

    # Rust images
    RUST_1_75 = "rust:1.75"
    RUST_LATEST = "rust:latest"

    # Alpine images
    ALPINE_LATEST = "alpine:latest"
    ALPINE_3_19 = "alpine:3.19"

    # Ubuntu images
    UBUNTU_22_04 = "ubuntu:22.04"
    UBUNTU_24_04 = "ubuntu:24.04"


class Services:
    """Common service images for GitLab CI jobs.

    Provides typed constants for popular service containers used in CI/CD pipelines.
    Services run alongside your job and are typically used for databases, caches, etc.
    """

    # Docker-in-Docker services
    DOCKER_DIND = "docker:dind"
    DOCKER_24_DIND = "docker:24-dind"

    # PostgreSQL services
    POSTGRES_14 = "postgres:14"
    POSTGRES_15 = "postgres:15"
    POSTGRES_16 = "postgres:16"

    # MySQL services
    MYSQL_8 = "mysql:8"

    # Redis services
    REDIS_7 = "redis:7"

    # MongoDB services
    MONGODB_6 = "mongo:6"

    # Elasticsearch services
    ELASTICSEARCH_8 = "elasticsearch:8"


__all__ = [
    # Context classes
    "CI",
    "GitLab",
    "MR",
    # Constants
    "When",
    "CachePolicy",
    "ArtifactsWhen",
    "PipelineSource",
    "Rules",
    "Images",
    "Services",
    # Predefined rules
    "on_default_branch",
    "on_tag",
    "on_merge_request",
    "manual_only",
    "always",
    "never",
]
