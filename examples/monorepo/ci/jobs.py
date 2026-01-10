"""Job definitions for monorepo pipeline."""

from wetwire_gitlab.intrinsics import CI
from wetwire_gitlab.pipeline import Artifacts, Job, Rule, Trigger

# Detect changes in each package
detect_changes = Job(
    name="detect-changes",
    stage="detect",
    image="alpine:latest",
    before_script=[
        "apk add --no-cache git",
    ],
    script=[
        # Detect changes in each package directory
        "echo 'Detecting changes...'",
        f"git diff --name-only {CI.COMMIT_BEFORE_SHA}...{CI.COMMIT_SHA} > changes.txt",
        "grep -q '^packages/frontend/' changes.txt && echo 'FRONTEND_CHANGED=true' >> build.env || echo 'FRONTEND_CHANGED=false' >> build.env",
        "grep -q '^packages/backend/' changes.txt && echo 'BACKEND_CHANGED=true' >> build.env || echo 'BACKEND_CHANGED=false' >> build.env",
        "grep -q '^packages/shared/' changes.txt && echo 'SHARED_CHANGED=true' >> build.env || echo 'SHARED_CHANGED=false' >> build.env",
        "cat build.env",
    ],
    artifacts=Artifacts(
        paths=["changes.txt"],
        reports={"dotenv": "build.env"},
    ),
)

# Trigger frontend child pipeline
trigger_frontend = Job(
    name="trigger-frontend",
    stage="trigger",
    trigger=Trigger(
        include=[{"local": "packages/frontend/.gitlab-ci.yml"}],
        strategy="depend",
    ),
    needs=["detect-changes"],
    rules=[
        Rule(if_='$FRONTEND_CHANGED == "true"'),
    ],
)

# Trigger backend child pipeline
trigger_backend = Job(
    name="trigger-backend",
    stage="trigger",
    trigger=Trigger(
        include=[{"local": "packages/backend/.gitlab-ci.yml"}],
        strategy="depend",
    ),
    needs=["detect-changes"],
    rules=[
        Rule(if_='$BACKEND_CHANGED == "true"'),
    ],
)

# Trigger shared child pipeline
trigger_shared = Job(
    name="trigger-shared",
    stage="trigger",
    trigger=Trigger(
        include=[{"local": "packages/shared/.gitlab-ci.yml"}],
        strategy="depend",
    ),
    needs=["detect-changes"],
    rules=[
        Rule(if_='$SHARED_CHANGED == "true"'),
    ],
)
