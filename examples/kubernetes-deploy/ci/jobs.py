"""Job definitions for Kubernetes deployment pipeline."""

from wetwire_gitlab.intrinsics import CI, When
from wetwire_gitlab.pipeline import Job, Rule

# Build and push Docker image
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
        "docker push $IMAGE_TAG",
    ],
)

# Deploy to development
deploy_dev = Job(
    name="deploy-dev",
    stage="deploy",
    image="alpine/helm:3.14",
    environment={"name": "development", "url": "https://dev.example.com"},
    variables={
        "KUBE_NAMESPACE": "app-dev",
        "HELM_RELEASE_NAME": "myapp-dev",
    },
    before_script=[
        "apk add --no-cache kubectl",
    ],
    script=[
        "kubectl config use-context $KUBE_CONTEXT",
        "helm upgrade --install $HELM_RELEASE_NAME ./charts/app "
        f"--namespace $KUBE_NAMESPACE --create-namespace "
        f"--set image.tag={CI.COMMIT_SHORT_SHA}",
    ],
    needs=["build"],
    rules=[
        Rule(if_=f'{CI.COMMIT_BRANCH} != "{CI.DEFAULT_BRANCH}"'),
    ],
)

# Deploy to staging
deploy_staging = Job(
    name="deploy-staging",
    stage="deploy",
    image="alpine/helm:3.14",
    environment={"name": "staging", "url": "https://staging.example.com"},
    variables={
        "KUBE_NAMESPACE": "app-staging",
        "HELM_RELEASE_NAME": "myapp-staging",
    },
    before_script=[
        "apk add --no-cache kubectl",
    ],
    script=[
        "kubectl config use-context $KUBE_CONTEXT",
        "helm upgrade --install $HELM_RELEASE_NAME ./charts/app "
        f"--namespace $KUBE_NAMESPACE --create-namespace "
        f"--set image.tag={CI.COMMIT_SHORT_SHA}",
    ],
    needs=["build"],
    rules=[
        Rule(if_=f"{CI.COMMIT_BRANCH} == {CI.DEFAULT_BRANCH}"),
    ],
)

# Deploy to production (manual)
deploy_production = Job(
    name="deploy-production",
    stage="deploy",
    image="alpine/helm:3.14",
    environment={"name": "production", "url": "https://example.com"},
    variables={
        "KUBE_NAMESPACE": "app-production",
        "HELM_RELEASE_NAME": "myapp-production",
    },
    before_script=[
        "apk add --no-cache kubectl",
    ],
    script=[
        "kubectl config use-context $KUBE_CONTEXT",
        "helm upgrade --install $HELM_RELEASE_NAME ./charts/app "
        f"--namespace $KUBE_NAMESPACE --create-namespace "
        f"--set image.tag={CI.COMMIT_SHORT_SHA} "
        "--set replicas=3",
    ],
    needs=["deploy-staging"],
    rules=[
        Rule(if_=f"{CI.COMMIT_BRANCH} == {CI.DEFAULT_BRANCH}", when=When.MANUAL),
    ],
)
