"""Generated GitLab CI pipeline."""

from wetwire_gitlab.pipeline import Job


testcargo = Job(
    name="test:cargo",
    script=[
        'rustc --version && cargo --version',
        'cargo test --workspace --verbose',
    ],
)


deploy = Job(
    name="deploy",
    stage="deploy",
    script='echo "Define your deployment script!"',
    environment="production",
)
