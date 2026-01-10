"""Tests for GitLab Runner config.toml configuration."""


class TestExecutorEnum:
    """Tests for Executor enum."""

    def test_executor_values(self):
        """Executor enum has correct values."""
        from wetwire_gitlab.runner_config import Executor

        assert Executor.SHELL.value == "shell"
        assert Executor.DOCKER.value == "docker"
        assert Executor.DOCKER_WINDOWS.value == "docker-windows"
        assert Executor.KUBERNETES.value == "kubernetes"
        assert Executor.SSH.value == "ssh"
        assert Executor.PARALLELS.value == "parallels"
        assert Executor.VIRTUALBOX.value == "virtualbox"
        assert Executor.DOCKER_MACHINE.value == "docker+machine"
        assert Executor.DOCKER_AUTOSCALER.value == "docker-autoscaler"
        assert Executor.INSTANCE.value == "instance"
        assert Executor.CUSTOM.value == "custom"


class TestDockerConfig:
    """Tests for Docker executor configuration."""

    def test_default_docker_config(self):
        """Default Docker config has correct values."""
        from wetwire_gitlab.runner_config import DockerConfig

        config = DockerConfig()
        assert config.image is None
        assert config.privileged is False
        assert config.pull_policy == "always"

    def test_docker_config_with_values(self):
        """Docker config with custom values."""
        from wetwire_gitlab.runner_config import DockerConfig

        config = DockerConfig(
            image="python:3.11",
            privileged=True,
            memory="512m",
            cpus="2",
            volumes=["/var/run/docker.sock:/var/run/docker.sock"],
        )

        assert config.image == "python:3.11"
        assert config.privileged is True
        assert config.memory == "512m"
        assert config.cpus == "2"
        assert "/var/run/docker.sock:/var/run/docker.sock" in config.volumes

    def test_docker_config_to_dict(self):
        """Docker config converts to dict."""
        from wetwire_gitlab.runner_config import DockerConfig

        config = DockerConfig(
            image="alpine:latest",
            privileged=True,
        )
        result = config.to_dict()

        assert result["image"] == "alpine:latest"
        assert result["privileged"] is True


class TestKubernetesConfig:
    """Tests for Kubernetes executor configuration."""

    def test_default_kubernetes_config(self):
        """Default Kubernetes config has correct values."""
        from wetwire_gitlab.runner_config import KubernetesConfig

        config = KubernetesConfig()
        assert config.namespace is None
        assert config.privileged is False

    def test_kubernetes_config_with_values(self):
        """Kubernetes config with custom values."""
        from wetwire_gitlab.runner_config import KubernetesConfig

        config = KubernetesConfig(
            namespace="gitlab-ci",
            image="python:3.11",
            privileged=True,
            service_account="gitlab-runner",
            image_pull_secrets=["docker-registry-secret"],
        )

        assert config.namespace == "gitlab-ci"
        assert config.image == "python:3.11"
        assert config.service_account == "gitlab-runner"

    def test_kubernetes_config_to_dict(self):
        """Kubernetes config converts to dict."""
        from wetwire_gitlab.runner_config import KubernetesConfig

        config = KubernetesConfig(
            namespace="ci",
            image="node:18",
        )
        result = config.to_dict()

        assert result["namespace"] == "ci"
        assert result["image"] == "node:18"


class TestCacheS3Config:
    """Tests for S3 cache configuration."""

    def test_cache_s3_config(self):
        """S3 cache config with values."""
        from wetwire_gitlab.runner_config import CacheS3Config

        config = CacheS3Config(
            server_address="s3.amazonaws.com",
            access_key="AKIAIOSFODNN7EXAMPLE",
            secret_key="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
            bucket_name="my-cache-bucket",
            bucket_location="us-east-1",
        )

        assert config.bucket_name == "my-cache-bucket"
        assert config.bucket_location == "us-east-1"


class TestCacheConfig:
    """Tests for cache configuration."""

    def test_cache_s3_type(self):
        """Cache config with S3 type."""
        from wetwire_gitlab.runner_config import CacheConfig, CacheS3Config

        s3 = CacheS3Config(
            bucket_name="my-bucket",
            bucket_location="us-west-2",
        )
        config = CacheConfig(
            type="s3",
            shared=True,
            s3=s3,
        )

        assert config.type == "s3"
        assert config.shared is True
        assert config.s3 is not None


class TestRunner:
    """Tests for Runner configuration."""

    def test_default_runner(self):
        """Default runner config."""
        from wetwire_gitlab.runner_config import Executor, Runner

        runner = Runner(
            name="my-runner",
            url="https://gitlab.com",
            token="glrt-xxxxxxxxxxxx",
            executor=Executor.DOCKER,
        )

        assert runner.name == "my-runner"
        assert runner.url == "https://gitlab.com"
        assert runner.executor == Executor.DOCKER

    def test_runner_with_docker(self):
        """Runner with Docker config."""
        from wetwire_gitlab.runner_config import DockerConfig, Executor, Runner

        docker = DockerConfig(image="python:3.11", privileged=True)
        runner = Runner(
            name="docker-runner",
            url="https://gitlab.com",
            token="glrt-xxxxxxxxxxxx",
            executor=Executor.DOCKER,
            docker=docker,
        )

        assert runner.docker is not None
        assert runner.docker.image == "python:3.11"

    def test_runner_with_kubernetes(self):
        """Runner with Kubernetes config."""
        from wetwire_gitlab.runner_config import Executor, KubernetesConfig, Runner

        k8s = KubernetesConfig(namespace="gitlab-ci", image="alpine:latest")
        runner = Runner(
            name="k8s-runner",
            url="https://gitlab.com",
            token="glrt-xxxxxxxxxxxx",
            executor=Executor.KUBERNETES,
            kubernetes=k8s,
        )

        assert runner.kubernetes is not None
        assert runner.kubernetes.namespace == "gitlab-ci"

    def test_runner_with_cache(self):
        """Runner with cache config."""
        from wetwire_gitlab.runner_config import (
            CacheConfig,
            CacheS3Config,
            Executor,
            Runner,
        )

        cache = CacheConfig(
            type="s3",
            shared=True,
            s3=CacheS3Config(bucket_name="cache-bucket"),
        )
        runner = Runner(
            name="cached-runner",
            url="https://gitlab.com",
            token="glrt-xxxxxxxxxxxx",
            executor=Executor.SHELL,
            cache=cache,
        )

        assert runner.cache is not None
        assert runner.cache.type == "s3"


class TestConfig:
    """Tests for top-level Config."""

    def test_minimal_config(self):
        """Minimal config with required fields."""
        from wetwire_gitlab.runner_config import Config, Executor, Runner

        runner = Runner(
            name="my-runner",
            url="https://gitlab.com",
            token="glrt-xxxxxxxxxxxx",
            executor=Executor.SHELL,
        )
        config = Config(
            concurrent=4,
            runners=[runner],
        )

        assert config.concurrent == 4
        assert len(config.runners) == 1

    def test_config_with_global_settings(self):
        """Config with global settings."""
        from wetwire_gitlab.runner_config import Config, Executor, Runner

        runner = Runner(
            name="my-runner",
            url="https://gitlab.com",
            token="glrt-xxxxxxxxxxxx",
            executor=Executor.SHELL,
        )
        config = Config(
            concurrent=10,
            log_level="debug",
            log_format="json",
            check_interval=5,
            shutdown_timeout=60,
            runners=[runner],
        )

        assert config.log_level == "debug"
        assert config.log_format == "json"
        assert config.check_interval == 5


class TestTomlSerialization:
    """Tests for TOML serialization."""

    def test_minimal_config_to_toml(self):
        """Minimal config serializes to TOML."""
        from wetwire_gitlab.runner_config import Config, Executor, Runner

        runner = Runner(
            name="my-runner",
            url="https://gitlab.com",
            token="glrt-xxxxxxxxxxxx",
            executor=Executor.SHELL,
        )
        config = Config(concurrent=4, runners=[runner])
        toml_str = config.to_toml()

        assert "concurrent = 4" in toml_str
        assert '[[runners]]' in toml_str
        assert 'name = "my-runner"' in toml_str
        assert 'executor = "shell"' in toml_str

    def test_docker_config_to_toml(self):
        """Docker runner serializes to TOML."""
        from wetwire_gitlab.runner_config import Config, DockerConfig, Executor, Runner

        docker = DockerConfig(image="python:3.11", privileged=True)
        runner = Runner(
            name="docker-runner",
            url="https://gitlab.com",
            token="glrt-xxxxxxxxxxxx",
            executor=Executor.DOCKER,
            docker=docker,
        )
        config = Config(concurrent=2, runners=[runner])
        toml_str = config.to_toml()

        assert "[runners.docker]" in toml_str
        assert 'image = "python:3.11"' in toml_str
        assert "privileged = true" in toml_str

    def test_kubernetes_config_to_toml(self):
        """Kubernetes runner serializes to TOML."""
        from wetwire_gitlab.runner_config import (
            Config,
            Executor,
            KubernetesConfig,
            Runner,
        )

        k8s = KubernetesConfig(
            namespace="gitlab-ci",
            image="alpine:latest",
            service_account="runner-sa",
        )
        runner = Runner(
            name="k8s-runner",
            url="https://gitlab.com",
            token="glrt-xxxxxxxxxxxx",
            executor=Executor.KUBERNETES,
            kubernetes=k8s,
        )
        config = Config(concurrent=5, runners=[runner])
        toml_str = config.to_toml()

        assert "[runners.kubernetes]" in toml_str
        assert 'namespace = "gitlab-ci"' in toml_str
        assert 'service_account = "runner-sa"' in toml_str

    def test_cache_config_to_toml(self):
        """Cache config serializes to TOML."""
        from wetwire_gitlab.runner_config import (
            CacheConfig,
            CacheS3Config,
            Config,
            Executor,
            Runner,
        )

        cache = CacheConfig(
            type="s3",
            shared=True,
            path="cache/",
            s3=CacheS3Config(
                bucket_name="my-bucket",
                bucket_location="us-east-1",
            ),
        )
        runner = Runner(
            name="cached-runner",
            url="https://gitlab.com",
            token="glrt-xxxxxxxxxxxx",
            executor=Executor.SHELL,
            cache=cache,
        )
        config = Config(concurrent=2, runners=[runner])
        toml_str = config.to_toml()

        assert "[runners.cache]" in toml_str
        assert 'Type = "s3"' in toml_str
        assert "Shared = true" in toml_str
        assert "[runners.cache.s3]" in toml_str
        assert 'BucketName = "my-bucket"' in toml_str

    def test_multiple_runners_to_toml(self):
        """Multiple runners serialize correctly."""
        from wetwire_gitlab.runner_config import Config, Executor, Runner

        runners = [
            Runner(
                name="runner-1",
                url="https://gitlab.com",
                token="glrt-xxxxxxxxxxxx",
                executor=Executor.SHELL,
            ),
            Runner(
                name="runner-2",
                url="https://gitlab.com",
                token="glrt-yyyyyyyyyyyy",
                executor=Executor.DOCKER,
            ),
        ]
        config = Config(concurrent=4, runners=runners)
        toml_str = config.to_toml()

        # Should have two [[runners]] sections
        assert toml_str.count("[[runners]]") == 2
        assert 'name = "runner-1"' in toml_str
        assert 'name = "runner-2"' in toml_str


class TestFromToml:
    """Tests for parsing TOML config."""

    def test_parse_minimal_toml(self):
        """Parse minimal TOML config."""
        from wetwire_gitlab.runner_config import Config

        toml_str = '''
concurrent = 4

[[runners]]
name = "my-runner"
url = "https://gitlab.com"
token = "glrt-xxxxxxxxxxxx"
executor = "shell"
'''
        config = Config.from_toml(toml_str)

        assert config.concurrent == 4
        assert len(config.runners) == 1
        assert config.runners[0].name == "my-runner"

    def test_parse_docker_config(self):
        """Parse TOML with Docker config."""
        from wetwire_gitlab.runner_config import Config, Executor

        toml_str = '''
concurrent = 2

[[runners]]
name = "docker-runner"
url = "https://gitlab.com"
token = "glrt-xxxxxxxxxxxx"
executor = "docker"

[runners.docker]
image = "python:3.11"
privileged = true
'''
        config = Config.from_toml(toml_str)

        assert config.runners[0].executor == Executor.DOCKER
        assert config.runners[0].docker is not None
        assert config.runners[0].docker.image == "python:3.11"
        assert config.runners[0].docker.privileged is True
