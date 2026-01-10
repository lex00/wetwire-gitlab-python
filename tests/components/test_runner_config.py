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

    def test_parse_kubernetes_config(self):
        """Parse TOML with Kubernetes config."""
        from wetwire_gitlab.runner_config import Config, Executor

        toml_str = '''
concurrent = 2

[[runners]]
name = "k8s-runner"
url = "https://gitlab.com"
token = "glrt-xxxxxxxxxxxx"
executor = "kubernetes"

[runners.kubernetes]
host = "https://kubernetes.default.svc"
namespace = "gitlab-ci"
image = "alpine:latest"
privileged = true
service_account = "runner-sa"
image_pull_secrets = ["docker-registry"]
'''
        config = Config.from_toml(toml_str)

        assert config.runners[0].executor == Executor.KUBERNETES
        assert config.runners[0].kubernetes is not None
        assert config.runners[0].kubernetes.host == "https://kubernetes.default.svc"
        assert config.runners[0].kubernetes.namespace == "gitlab-ci"
        assert config.runners[0].kubernetes.service_account == "runner-sa"

    def test_parse_cache_s3_config(self):
        """Parse TOML with S3 cache config."""
        from wetwire_gitlab.runner_config import Config

        toml_str = '''
concurrent = 2

[[runners]]
name = "cached-runner"
url = "https://gitlab.com"
token = "glrt-xxxxxxxxxxxx"
executor = "shell"

[runners.cache]
Type = "s3"
Path = "cache/prefix/"
Shared = true

[runners.cache.s3]
ServerAddress = "s3.amazonaws.com"
AccessKey = "AKIAIOSFODNN7EXAMPLE"
SecretKey = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
BucketName = "my-bucket"
BucketLocation = "us-east-1"
'''
        config = Config.from_toml(toml_str)

        assert config.runners[0].cache is not None
        assert config.runners[0].cache.type == "s3"
        assert config.runners[0].cache.shared is True
        assert config.runners[0].cache.s3 is not None
        assert config.runners[0].cache.s3.bucket_name == "my-bucket"

    def test_parse_cache_gcs_config(self):
        """Parse TOML with GCS cache config."""
        from wetwire_gitlab.runner_config import Config

        toml_str = '''
concurrent = 2

[[runners]]
name = "gcs-runner"
url = "https://gitlab.com"
token = "glrt-xxxxxxxxxxxx"
executor = "shell"

[runners.cache]
Type = "gcs"
Path = "cache/gcs/"
Shared = true

[runners.cache.gcs]
CredentialsFile = "/path/to/credentials.json"
BucketName = "my-gcs-bucket"
AccessID = "sa@project.iam.gserviceaccount.com"
PrivateKey = "-----BEGIN PRIVATE KEY-----"
'''
        config = Config.from_toml(toml_str)

        assert config.runners[0].cache is not None
        assert config.runners[0].cache.type == "gcs"
        assert config.runners[0].cache.gcs is not None
        assert config.runners[0].cache.gcs.bucket_name == "my-gcs-bucket"
        assert config.runners[0].cache.gcs.credentials_file == "/path/to/credentials.json"


class TestGCSCacheToToml:
    """Tests for GCS cache TOML serialization."""

    def test_gcs_cache_to_toml(self):
        """GCS cache serializes to TOML output."""
        from wetwire_gitlab.runner_config import (
            CacheConfig,
            CacheGCSConfig,
            Config,
            Executor,
            Runner,
        )

        gcs = CacheGCSConfig(
            credentials_file="/path/to/creds.json",
            bucket_name="my-gcs-bucket",
        )
        cache = CacheConfig(type="gcs", path="cache/gcs/", shared=True, gcs=gcs)
        runner = Runner(
            name="gcs-runner",
            url="https://gitlab.com",
            token="glrt-xxxxxxxxxxxx",
            executor=Executor.SHELL,
            cache=cache,
        )
        config = Config(concurrent=2, runners=[runner])
        toml_str = config.to_toml()

        assert "[runners.cache]" in toml_str
        assert 'Type = "gcs"' in toml_str
        assert "[runners.cache.gcs]" in toml_str
        assert 'CredentialsFile = "/path/to/creds.json"' in toml_str
        assert 'BucketName = "my-gcs-bucket"' in toml_str


class TestDockerConfigFullCoverage:
    """Tests for full DockerConfig coverage."""

    def test_docker_config_all_optional_fields(self):
        """DockerConfig with all optional fields set."""
        from wetwire_gitlab.runner_config import DockerConfig

        config = DockerConfig(
            image="python:3.11",
            host="tcp://localhost:2375",
            privileged=True,
            memory="512m",
            cpus="2",
            volumes=["/data:/data"],
            dns=["8.8.8.8"],
            pull_policy="if-not-present",
            allowed_images=["python:*"],
            allowed_services=["postgres:*"],
            wait_for_services_timeout=60,
            disable_cache=True,
            cap_add=["SYS_ADMIN"],
            devices=["/dev/kvm"],
            gpus="all",
        )
        result = config.to_dict()

        assert result["image"] == "python:3.11"
        assert result["host"] == "tcp://localhost:2375"
        assert result["privileged"] is True
        assert result["memory"] == "512m"
        assert result["cpus"] == "2"
        assert result["volumes"] == ["/data:/data"]
        assert result["dns"] == ["8.8.8.8"]
        assert result["pull_policy"] == "if-not-present"
        assert result["allowed_images"] == ["python:*"]
        assert result["allowed_services"] == ["postgres:*"]
        assert result["wait_for_services_timeout"] == 60
        assert result["disable_cache"] is True
        assert result["cap_add"] == ["SYS_ADMIN"]
        assert result["devices"] == ["/dev/kvm"]
        assert result["gpus"] == "all"


class TestKubernetesConfigFullCoverage:
    """Tests for full KubernetesConfig coverage."""

    def test_kubernetes_config_all_fields(self):
        """KubernetesConfig with all fields set."""
        from wetwire_gitlab.runner_config import KubernetesConfig

        config = KubernetesConfig(
            host="https://kubernetes.default.svc",
            namespace="gitlab-ci",
            image="python:3.11",
            privileged=True,
            service_account="runner-sa",
            image_pull_secrets=["docker-registry"],
            allowed_images=["python:*", "node:*"],
            allowed_services=["postgres:*", "redis:*"],
        )
        result = config.to_dict()

        assert result["host"] == "https://kubernetes.default.svc"
        assert result["namespace"] == "gitlab-ci"
        assert result["image"] == "python:3.11"
        assert result["privileged"] is True
        assert result["service_account"] == "runner-sa"
        assert result["image_pull_secrets"] == ["docker-registry"]
        assert result["allowed_images"] == ["python:*", "node:*"]
        assert result["allowed_services"] == ["postgres:*", "redis:*"]


class TestRunnerFullCoverage:
    """Tests for full Runner coverage."""

    def test_runner_all_optional_fields(self):
        """Runner with all optional fields set."""
        from wetwire_gitlab.runner_config import Executor, Runner

        runner = Runner(
            name="full-runner",
            url="https://gitlab.com",
            token="glrt-xxxxxxxxxxxx",
            executor=Executor.DOCKER,
            limit=10,
            request_concurrency=5,
            output_limit=8192,  # Non-default value to include in result
            builds_dir="/builds",
            cache_dir="/cache",
            environment=["VAR1=value1", "VAR2=value2"],
            shell="bash",
            clone_url="https://gitlab.com/clone",
        )
        result = runner.to_dict()

        assert result["name"] == "full-runner"
        assert result["limit"] == 10
        assert result["request_concurrency"] == 5
        assert result["output_limit"] == 8192
        assert result["builds_dir"] == "/builds"
        assert result["cache_dir"] == "/cache"
        assert result["environment"] == ["VAR1=value1", "VAR2=value2"]
        assert result["shell"] == "bash"
        assert result["clone_url"] == "https://gitlab.com/clone"


class TestCacheConfigFullCoverage:
    """Tests for full CacheConfig coverage."""

    def test_cache_gcs_config(self):
        """CacheConfig with GCS backend."""
        from wetwire_gitlab.runner_config import CacheConfig, CacheGCSConfig

        gcs = CacheGCSConfig(
            bucket_name="my-gcs-bucket",
            credentials_file="/path/to/credentials.json",
        )
        cache = CacheConfig(
            type="gcs",
            path="cache/prefix/",
            shared=True,
            gcs=gcs,
        )
        result = cache.to_dict()

        assert result["Type"] == "gcs"
        assert result["Path"] == "cache/prefix/"
        assert result["Shared"] is True

        # GCS config is serialized separately in Config.to_toml()
        gcs_result = gcs.to_dict()
        assert gcs_result["BucketName"] == "my-gcs-bucket"
        assert gcs_result["CredentialsFile"] == "/path/to/credentials.json"

    def test_cache_gcs_config_all_fields(self):
        """CacheGCSConfig with all fields set."""
        from wetwire_gitlab.runner_config import CacheGCSConfig

        gcs = CacheGCSConfig(
            credentials_file="/path/to/credentials.json",
            access_id="service-account@project.iam.gserviceaccount.com",
            private_key="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----",
            bucket_name="my-gcs-bucket",
        )
        result = gcs.to_dict()

        assert result["CredentialsFile"] == "/path/to/credentials.json"
        assert result["AccessID"] == "service-account@project.iam.gserviceaccount.com"
        assert "PrivateKey" in result
        assert result["BucketName"] == "my-gcs-bucket"


class TestConfigFullCoverage:
    """Tests for full Config coverage."""

    def test_config_all_optional_fields(self):
        """Config with all optional fields set."""
        from wetwire_gitlab.runner_config import Config, Executor, Runner

        runner = Runner(
            name="full-config-runner",
            url="https://gitlab.com",
            token="glrt-xxxxxxxxxxxx",
            executor=Executor.SHELL,
        )
        config = Config(
            concurrent=4,
            log_level="debug",
            log_format="json",
            check_interval=5,
            sentry_dsn="https://xxxxx@sentry.io/12345",
            connection_max_age="15m0s",
            listen_address="0.0.0.0:9252",
            shutdown_timeout=60,
            runners=[runner],
        )
        toml_str = config.to_toml()

        assert 'log_level = "debug"' in toml_str
        assert 'log_format = "json"' in toml_str
        assert "check_interval = 5" in toml_str
        assert 'sentry_dsn = "https://xxxxx@sentry.io/12345"' in toml_str
        assert 'connection_max_age = "15m0s"' in toml_str
        assert 'listen_address = "0.0.0.0:9252"' in toml_str
        assert "shutdown_timeout = 60" in toml_str


class TestCacheS3ConfigFullCoverage:
    """Tests for full CacheS3Config coverage."""

    def test_s3_config_all_fields(self):
        """CacheS3Config with all fields set."""
        from wetwire_gitlab.runner_config import CacheS3Config

        config = CacheS3Config(
            server_address="s3.amazonaws.com",
            access_key="AKIAIOSFODNN7EXAMPLE",
            secret_key="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
            bucket_name="my-cache-bucket",
            bucket_location="us-east-1",
            insecure=True,
            authentication_type="access-key",
        )
        result = config.to_dict()

        assert result["ServerAddress"] == "s3.amazonaws.com"
        assert result["AccessKey"] == "AKIAIOSFODNN7EXAMPLE"
        assert result["SecretKey"] == "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
        assert result["BucketName"] == "my-cache-bucket"
        assert result["BucketLocation"] == "us-east-1"
        assert result["Insecure"] is True
        assert result["AuthenticationType"] == "access-key"

    def test_s3_config_iam_auth(self):
        """CacheS3Config with IAM authentication."""
        from wetwire_gitlab.runner_config import CacheS3Config

        config = CacheS3Config(
            bucket_name="my-cache-bucket",
            bucket_location="us-west-2",
            authentication_type="iam",
        )
        result = config.to_dict()

        assert result["BucketName"] == "my-cache-bucket"
        assert result["BucketLocation"] == "us-west-2"
        assert result["AuthenticationType"] == "iam"
        # No access_key or secret_key with IAM auth
        assert "AccessKey" not in result
        assert "SecretKey" not in result
