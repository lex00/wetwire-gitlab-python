"""Executor enum for GitLab Runner."""

from enum import Enum


class Executor(Enum):
    """GitLab Runner executor types.

    The executor determines how the runner processes jobs.
    """

    SHELL = "shell"
    DOCKER = "docker"
    DOCKER_WINDOWS = "docker-windows"
    KUBERNETES = "kubernetes"
    SSH = "ssh"
    PARALLELS = "parallels"
    VIRTUALBOX = "virtualbox"
    DOCKER_MACHINE = "docker+machine"
    DOCKER_AUTOSCALER = "docker-autoscaler"
    INSTANCE = "instance"
    CUSTOM = "custom"
