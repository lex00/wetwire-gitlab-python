"""Generated GitLab CI pipeline."""

from wetwire_gitlab.pipeline import Job


test_async = Job(
    name="test_async",
    script=[
        'npm install',
        'node ./specs/start.js ./specs/async.spec.js',
    ],
)


test_db = Job(
    name="test_db",
    script=[
        'npm install',
        'node ./specs/start.js ./specs/db-postgres.spec.js',
    ],
)


deploy = Job(
    name="deploy",
    stage="deploy",
    script='echo "Define your deployment script!"',
    environment="production",
)
