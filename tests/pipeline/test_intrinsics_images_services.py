"""Tests for Images and Services constants in intrinsics module."""


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
