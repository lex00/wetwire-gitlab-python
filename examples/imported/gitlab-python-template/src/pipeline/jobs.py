"""Generated GitLab CI pipeline."""

from wetwire_gitlab.pipeline import Artifacts, Job, Rule


test = Job(
    name="test",
    script=[
        'pip install ruff tox',
        'pip install --editable ".[test]"',
        'tox -e py,ruff',
    ],
)


run = Job(
    name="run",
    script=['pip install .'],
    artifacts={
        'paths': ['build/*'],
    },
)


pages = Job(
    name="pages",
    script=[
        'pip install sphinx sphinx-rtd-theme',
        'cd doc',
        'make html',
        'mv build/html/ ../public/',
    ],
    rules=[Rule(if_='$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH')],
    artifacts={
        'paths': ['public'],
    },
)


deploy = Job(
    name="deploy",
    stage="deploy",
    script='echo "Define your deployment script!"',
    environment="production",
)
