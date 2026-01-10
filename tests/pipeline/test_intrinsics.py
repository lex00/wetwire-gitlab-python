"""Tests for intrinsics module."""



class TestCIContext:
    """Tests for CI predefined variables context."""

    def test_ci_commit_sha(self):
        """CI.commit_sha returns correct variable reference."""
        from wetwire_gitlab.intrinsics import CI

        assert CI.commit_sha == "$CI_COMMIT_SHA"

    def test_ci_commit_ref_name(self):
        """CI.commit_ref_name returns correct variable reference."""
        from wetwire_gitlab.intrinsics import CI

        assert CI.commit_ref_name == "$CI_COMMIT_REF_NAME"

    def test_ci_commit_branch(self):
        """CI.commit_branch returns correct variable reference."""
        from wetwire_gitlab.intrinsics import CI

        assert CI.commit_branch == "$CI_COMMIT_BRANCH"

    def test_ci_commit_tag(self):
        """CI.commit_tag returns correct variable reference."""
        from wetwire_gitlab.intrinsics import CI

        assert CI.commit_tag == "$CI_COMMIT_TAG"

    def test_ci_default_branch(self):
        """CI.default_branch returns correct variable reference."""
        from wetwire_gitlab.intrinsics import CI

        assert CI.default_branch == "$CI_DEFAULT_BRANCH"

    def test_ci_pipeline_id(self):
        """CI.pipeline_id returns correct variable reference."""
        from wetwire_gitlab.intrinsics import CI

        assert CI.pipeline_id == "$CI_PIPELINE_ID"

    def test_ci_pipeline_source(self):
        """CI.pipeline_source returns correct variable reference."""
        from wetwire_gitlab.intrinsics import CI

        assert CI.pipeline_source == "$CI_PIPELINE_SOURCE"

    def test_ci_job_id(self):
        """CI.job_id returns correct variable reference."""
        from wetwire_gitlab.intrinsics import CI

        assert CI.job_id == "$CI_JOB_ID"

    def test_ci_job_name(self):
        """CI.job_name returns correct variable reference."""
        from wetwire_gitlab.intrinsics import CI

        assert CI.job_name == "$CI_JOB_NAME"

    def test_ci_project_path(self):
        """CI.project_path returns correct variable reference."""
        from wetwire_gitlab.intrinsics import CI

        assert CI.project_path == "$CI_PROJECT_PATH"

    def test_ci_project_name(self):
        """CI.project_name returns correct variable reference."""
        from wetwire_gitlab.intrinsics import CI

        assert CI.project_name == "$CI_PROJECT_NAME"

    def test_ci_registry_image(self):
        """CI.registry_image returns correct variable reference."""
        from wetwire_gitlab.intrinsics import CI

        assert CI.registry_image == "$CI_REGISTRY_IMAGE"


class TestGitLabContext:
    """Tests for GitLab predefined variables context."""

    def test_gitlab_user_login(self):
        """GitLab.user_login returns correct variable reference."""
        from wetwire_gitlab.intrinsics import GitLab

        assert GitLab.user_login == "$GITLAB_USER_LOGIN"

    def test_gitlab_user_email(self):
        """GitLab.user_email returns correct variable reference."""
        from wetwire_gitlab.intrinsics import GitLab

        assert GitLab.user_email == "$GITLAB_USER_EMAIL"

    def test_gitlab_user_name(self):
        """GitLab.user_name returns correct variable reference."""
        from wetwire_gitlab.intrinsics import GitLab

        assert GitLab.user_name == "$GITLAB_USER_NAME"

    def test_gitlab_user_id(self):
        """GitLab.user_id returns correct variable reference."""
        from wetwire_gitlab.intrinsics import GitLab

        assert GitLab.user_id == "$GITLAB_USER_ID"


class TestMRContext:
    """Tests for Merge Request predefined variables context."""

    def test_mr_iid(self):
        """MR.iid returns correct variable reference."""
        from wetwire_gitlab.intrinsics import MR

        assert MR.iid == "$CI_MERGE_REQUEST_IID"

    def test_mr_source_branch(self):
        """MR.source_branch returns correct variable reference."""
        from wetwire_gitlab.intrinsics import MR

        assert MR.source_branch == "$CI_MERGE_REQUEST_SOURCE_BRANCH_NAME"

    def test_mr_target_branch(self):
        """MR.target_branch returns correct variable reference."""
        from wetwire_gitlab.intrinsics import MR

        assert MR.target_branch == "$CI_MERGE_REQUEST_TARGET_BRANCH_NAME"

    def test_mr_title(self):
        """MR.title returns correct variable reference."""
        from wetwire_gitlab.intrinsics import MR

        assert MR.title == "$CI_MERGE_REQUEST_TITLE"

    def test_mr_labels(self):
        """MR.labels returns correct variable reference."""
        from wetwire_gitlab.intrinsics import MR

        assert MR.labels == "$CI_MERGE_REQUEST_LABELS"


class TestWhenConstants:
    """Tests for When constants."""

    def test_when_always(self):
        """When.ALWAYS is correct."""
        from wetwire_gitlab.intrinsics import When

        assert When.ALWAYS == "always"

    def test_when_never(self):
        """When.NEVER is correct."""
        from wetwire_gitlab.intrinsics import When

        assert When.NEVER == "never"

    def test_when_on_success(self):
        """When.ON_SUCCESS is correct."""
        from wetwire_gitlab.intrinsics import When

        assert When.ON_SUCCESS == "on_success"

    def test_when_on_failure(self):
        """When.ON_FAILURE is correct."""
        from wetwire_gitlab.intrinsics import When

        assert When.ON_FAILURE == "on_failure"

    def test_when_manual(self):
        """When.MANUAL is correct."""
        from wetwire_gitlab.intrinsics import When

        assert When.MANUAL == "manual"

    def test_when_delayed(self):
        """When.DELAYED is correct."""
        from wetwire_gitlab.intrinsics import When

        assert When.DELAYED == "delayed"


class TestCachePolicyConstants:
    """Tests for CachePolicy constants."""

    def test_cache_policy_pull(self):
        """CachePolicy.PULL is correct."""
        from wetwire_gitlab.intrinsics import CachePolicy

        assert CachePolicy.PULL == "pull"

    def test_cache_policy_push(self):
        """CachePolicy.PUSH is correct."""
        from wetwire_gitlab.intrinsics import CachePolicy

        assert CachePolicy.PUSH == "push"

    def test_cache_policy_pull_push(self):
        """CachePolicy.PULL_PUSH is correct."""
        from wetwire_gitlab.intrinsics import CachePolicy

        assert CachePolicy.PULL_PUSH == "pull-push"


class TestPredefinedRules:
    """Tests for predefined rule helpers."""

    def test_on_default_branch(self):
        """on_default_branch creates correct rule."""
        from wetwire_gitlab.intrinsics import on_default_branch
        from wetwire_gitlab.pipeline import Rule

        rule = on_default_branch
        assert isinstance(rule, Rule)
        assert "$CI_COMMIT_BRANCH" in rule.if_
        assert "$CI_DEFAULT_BRANCH" in rule.if_

    def test_on_tag(self):
        """on_tag creates correct rule."""
        from wetwire_gitlab.intrinsics import on_tag
        from wetwire_gitlab.pipeline import Rule

        rule = on_tag
        assert isinstance(rule, Rule)
        assert "$CI_COMMIT_TAG" in rule.if_

    def test_on_merge_request(self):
        """on_merge_request creates correct rule."""
        from wetwire_gitlab.intrinsics import on_merge_request
        from wetwire_gitlab.pipeline import Rule

        rule = on_merge_request
        assert isinstance(rule, Rule)
        assert "merge_request" in rule.if_.lower() or "$CI_PIPELINE_SOURCE" in rule.if_

    def test_manual_only(self):
        """manual_only creates correct rule."""
        from wetwire_gitlab.intrinsics import manual_only
        from wetwire_gitlab.pipeline import Rule

        rule = manual_only
        assert isinstance(rule, Rule)
        assert rule.when == "manual"

    def test_always(self):
        """always creates correct rule."""
        from wetwire_gitlab.intrinsics import always
        from wetwire_gitlab.pipeline import Rule

        rule = always
        assert isinstance(rule, Rule)
        assert rule.when == "always"

    def test_never(self):
        """never creates correct rule."""
        from wetwire_gitlab.intrinsics import never
        from wetwire_gitlab.pipeline import Rule

        rule = never
        assert isinstance(rule, Rule)
        assert rule.when == "never"


class TestArtifactsWhenConstants:
    """Tests for ArtifactsWhen constants."""

    def test_artifacts_when_on_success(self):
        """ArtifactsWhen.ON_SUCCESS is correct."""
        from wetwire_gitlab.intrinsics import ArtifactsWhen

        assert ArtifactsWhen.ON_SUCCESS == "on_success"

    def test_artifacts_when_on_failure(self):
        """ArtifactsWhen.ON_FAILURE is correct."""
        from wetwire_gitlab.intrinsics import ArtifactsWhen

        assert ArtifactsWhen.ON_FAILURE == "on_failure"

    def test_artifacts_when_always(self):
        """ArtifactsWhen.ALWAYS is correct."""
        from wetwire_gitlab.intrinsics import ArtifactsWhen

        assert ArtifactsWhen.ALWAYS == "always"


class TestPipelineSource:
    """Tests for PipelineSource constants."""

    def test_pipeline_source_push(self):
        """PipelineSource.PUSH is correct."""
        from wetwire_gitlab.intrinsics import PipelineSource

        assert PipelineSource.PUSH == "push"

    def test_pipeline_source_merge_request_event(self):
        """PipelineSource.MERGE_REQUEST_EVENT is correct."""
        from wetwire_gitlab.intrinsics import PipelineSource

        assert PipelineSource.MERGE_REQUEST_EVENT == "merge_request_event"

    def test_pipeline_source_schedule(self):
        """PipelineSource.SCHEDULE is correct."""
        from wetwire_gitlab.intrinsics import PipelineSource

        assert PipelineSource.SCHEDULE == "schedule"

    def test_pipeline_source_web(self):
        """PipelineSource.WEB is correct."""
        from wetwire_gitlab.intrinsics import PipelineSource

        assert PipelineSource.WEB == "web"

    def test_pipeline_source_api(self):
        """PipelineSource.API is correct."""
        from wetwire_gitlab.intrinsics import PipelineSource

        assert PipelineSource.API == "api"

    def test_pipeline_source_trigger(self):
        """PipelineSource.TRIGGER is correct."""
        from wetwire_gitlab.intrinsics import PipelineSource

        assert PipelineSource.TRIGGER == "trigger"

    def test_pipeline_source_pipeline(self):
        """PipelineSource.PIPELINE is correct."""
        from wetwire_gitlab.intrinsics import PipelineSource

        assert PipelineSource.PIPELINE == "pipeline"


class TestImagesConstants:
    """Tests for Images constants."""

    def test_images_python_3_11(self):
        """Images.PYTHON_3_11 returns correct image string."""
        from wetwire_gitlab.intrinsics import Images

        assert Images.PYTHON_3_11 == "python:3.11"

    def test_images_python_3_11_slim(self):
        """Images.PYTHON_3_11_SLIM returns correct image string."""
        from wetwire_gitlab.intrinsics import Images

        assert Images.PYTHON_3_11_SLIM == "python:3.11-slim"

    def test_images_python_3_12(self):
        """Images.PYTHON_3_12 returns correct image string."""
        from wetwire_gitlab.intrinsics import Images

        assert Images.PYTHON_3_12 == "python:3.12"

    def test_images_python_3_12_slim(self):
        """Images.PYTHON_3_12_SLIM returns correct image string."""
        from wetwire_gitlab.intrinsics import Images

        assert Images.PYTHON_3_12_SLIM == "python:3.12-slim"

    def test_images_python_3_13(self):
        """Images.PYTHON_3_13 returns correct image string."""
        from wetwire_gitlab.intrinsics import Images

        assert Images.PYTHON_3_13 == "python:3.13"

    def test_images_node_18(self):
        """Images.NODE_18 returns correct image string."""
        from wetwire_gitlab.intrinsics import Images

        assert Images.NODE_18 == "node:18"

    def test_images_node_20(self):
        """Images.NODE_20 returns correct image string."""
        from wetwire_gitlab.intrinsics import Images

        assert Images.NODE_20 == "node:20"

    def test_images_node_20_alpine(self):
        """Images.NODE_20_ALPINE returns correct image string."""
        from wetwire_gitlab.intrinsics import Images

        assert Images.NODE_20_ALPINE == "node:20-alpine"

    def test_images_go_1_21(self):
        """Images.GO_1_21 returns correct image string."""
        from wetwire_gitlab.intrinsics import Images

        assert Images.GO_1_21 == "golang:1.21"

    def test_images_go_1_22(self):
        """Images.GO_1_22 returns correct image string."""
        from wetwire_gitlab.intrinsics import Images

        assert Images.GO_1_22 == "golang:1.22"

    def test_images_go_1_23(self):
        """Images.GO_1_23 returns correct image string."""
        from wetwire_gitlab.intrinsics import Images

        assert Images.GO_1_23 == "golang:1.23"

    def test_images_ruby_3_2(self):
        """Images.RUBY_3_2 returns correct image string."""
        from wetwire_gitlab.intrinsics import Images

        assert Images.RUBY_3_2 == "ruby:3.2"

    def test_images_ruby_3_3(self):
        """Images.RUBY_3_3 returns correct image string."""
        from wetwire_gitlab.intrinsics import Images

        assert Images.RUBY_3_3 == "ruby:3.3"

    def test_images_rust_1_75(self):
        """Images.RUST_1_75 returns correct image string."""
        from wetwire_gitlab.intrinsics import Images

        assert Images.RUST_1_75 == "rust:1.75"

    def test_images_rust_latest(self):
        """Images.RUST_LATEST returns correct image string."""
        from wetwire_gitlab.intrinsics import Images

        assert Images.RUST_LATEST == "rust:latest"

    def test_images_alpine_latest(self):
        """Images.ALPINE_LATEST returns correct image string."""
        from wetwire_gitlab.intrinsics import Images

        assert Images.ALPINE_LATEST == "alpine:latest"

    def test_images_alpine_3_19(self):
        """Images.ALPINE_3_19 returns correct image string."""
        from wetwire_gitlab.intrinsics import Images

        assert Images.ALPINE_3_19 == "alpine:3.19"

    def test_images_ubuntu_22_04(self):
        """Images.UBUNTU_22_04 returns correct image string."""
        from wetwire_gitlab.intrinsics import Images

        assert Images.UBUNTU_22_04 == "ubuntu:22.04"

    def test_images_ubuntu_24_04(self):
        """Images.UBUNTU_24_04 returns correct image string."""
        from wetwire_gitlab.intrinsics import Images

        assert Images.UBUNTU_24_04 == "ubuntu:24.04"


class TestServicesConstants:
    """Tests for Services constants."""

    def test_services_docker_dind(self):
        """Services.DOCKER_DIND returns correct service string."""
        from wetwire_gitlab.intrinsics import Services

        assert Services.DOCKER_DIND == "docker:dind"

    def test_services_docker_24_dind(self):
        """Services.DOCKER_24_DIND returns correct service string."""
        from wetwire_gitlab.intrinsics import Services

        assert Services.DOCKER_24_DIND == "docker:24-dind"

    def test_services_postgres_14(self):
        """Services.POSTGRES_14 returns correct service string."""
        from wetwire_gitlab.intrinsics import Services

        assert Services.POSTGRES_14 == "postgres:14"

    def test_services_postgres_15(self):
        """Services.POSTGRES_15 returns correct service string."""
        from wetwire_gitlab.intrinsics import Services

        assert Services.POSTGRES_15 == "postgres:15"

    def test_services_postgres_16(self):
        """Services.POSTGRES_16 returns correct service string."""
        from wetwire_gitlab.intrinsics import Services

        assert Services.POSTGRES_16 == "postgres:16"

    def test_services_mysql_8(self):
        """Services.MYSQL_8 returns correct service string."""
        from wetwire_gitlab.intrinsics import Services

        assert Services.MYSQL_8 == "mysql:8"

    def test_services_redis_7(self):
        """Services.REDIS_7 returns correct service string."""
        from wetwire_gitlab.intrinsics import Services

        assert Services.REDIS_7 == "redis:7"

    def test_services_mongodb_6(self):
        """Services.MONGODB_6 returns correct service string."""
        from wetwire_gitlab.intrinsics import Services

        assert Services.MONGODB_6 == "mongo:6"

    def test_services_elasticsearch_8(self):
        """Services.ELASTICSEARCH_8 returns correct service string."""
        from wetwire_gitlab.intrinsics import Services

        assert Services.ELASTICSEARCH_8 == "elasticsearch:8"
