"""Job definitions for Docker build pipeline."""

from wetwire_gitlab.intrinsics import CI, Rules
from wetwire_gitlab.pipeline import Artifacts, Job

# Build Docker image
build = Job(
    name="build",
    stage="build",
    image="docker:24",
    services=["docker:24-dind"],
    variables={
        "DOCKER_TLS_CERTDIR": "/certs",
        "IMAGE_TAG": f"{CI.REGISTRY_IMAGE}:{CI.COMMIT_SHORT_SHA}",
    },
    before_script=[
        f"docker login -u {CI.REGISTRY_USER} -p {CI.REGISTRY_PASSWORD} {CI.REGISTRY}",
    ],
    script=[
        "docker build -t $IMAGE_TAG .",
        "docker save $IMAGE_TAG > image.tar",
    ],
    artifacts=Artifacts(
        paths=["image.tar"],
        expire_in="1 hour",
    ),
)

# Test the built image
test = Job(
    name="test",
    stage="test",
    image="docker:24",
    services=["docker:24-dind"],
    variables={
        "DOCKER_TLS_CERTDIR": "/certs",
        "IMAGE_TAG": f"{CI.REGISTRY_IMAGE}:{CI.COMMIT_SHORT_SHA}",
    },
    script=[
        "docker load < image.tar",
        "docker run --rm $IMAGE_TAG echo 'Container starts successfully'",
    ],
    needs=["build"],
)

# Push to registry
push = Job(
    name="push",
    stage="push",
    image="docker:24",
    services=["docker:24-dind"],
    variables={
        "DOCKER_TLS_CERTDIR": "/certs",
        "IMAGE_TAG": f"{CI.REGISTRY_IMAGE}:{CI.COMMIT_SHORT_SHA}",
    },
    before_script=[
        f"docker login -u {CI.REGISTRY_USER} -p {CI.REGISTRY_PASSWORD} {CI.REGISTRY}",
    ],
    script=[
        "docker load < image.tar",
        "docker push $IMAGE_TAG",
        # Tag as latest on default branch
        f'if [ "{CI.COMMIT_BRANCH}" = "{CI.DEFAULT_BRANCH}" ]; then '
        f"docker tag $IMAGE_TAG {CI.REGISTRY_IMAGE}:latest && "
        f"docker push {CI.REGISTRY_IMAGE}:latest; fi",
    ],
    needs=["test"],
    rules=[Rules.ON_DEFAULT_BRANCH, Rules.ON_TAG],
)
