# FAQ

For general wetwire questions, see the [central FAQ](https://github.com/lex00/wetwire/blob/main/docs/FAQ.md).

## Getting Started

### How do I install wetwire-gitlab?

```bash
pip install wetwire-gitlab
```

### How do I generate a pipeline file?

```bash
wetwire-gitlab build
# Creates .gitlab-ci.yml
```

### How do I import an existing pipeline?

```bash
wetwire-gitlab import .gitlab-ci.yml
```

## Syntax

### How do I declare a job?

Use the `Job` dataclass:

```python
from wetwire_gitlab.pipeline import *

build = Job(
    name="build",
    stage="build",
    script=["make build"],
)
```

### How do I use CI variables?

Use typed variable namespaces instead of raw strings:

```python
from wetwire_gitlab.intrinsics import *

# These expand to proper $VARIABLE syntax
branch = CI.COMMIT_BRANCH     # $CI_COMMIT_BRANCH
user = GitLab.USER_LOGIN      # $GITLAB_USER_LOGIN
source = MR.SOURCE_BRANCH     # $CI_MERGE_REQUEST_SOURCE_BRANCH_NAME
```

### How do I add conditional rules?

Use the `Rule` dataclass or pre-defined rules:

```python
from wetwire_gitlab.pipeline import *
from wetwire_gitlab.intrinsics import *

# Pre-defined rule
deploy = Job(rules=[Rules.ON_DEFAULT_BRANCH])

# Custom rule
custom = Rule(if_=f"{CI.COMMIT_BRANCH} == 'main'")
```

### How do I configure artifacts?

Use the `Artifacts` dataclass:

```python
from wetwire_gitlab.pipeline import *

build = Job(
    name="build",
    artifacts=Artifacts(
        paths=["build/", "dist/"],
        expire_in="1 week",
    ),
)
```

## Lint Rules

### What lint rules are available?

| Rule | Description |
|------|-------------|
| WGL001 | Use typed component wrappers |
| WGL002 | Use Rule dataclass not raw dict |
| WGL003 | Use predefined variables from intrinsics |
| WGL004 | Use Cache dataclass not raw dict |
| WGL005 | Use Artifacts dataclass not raw dict |
| WGL006 | Use typed stage constants |
| WGL007 | Duplicate job names |
| WGL008 | Oversized files |

### How do I run the linter?

```bash
wetwire-gitlab lint
```

## Advanced Usage

### How do I use Auto DevOps templates?

```python
from wetwire_gitlab.templates import AutoDevOps, SAST, DAST

# Full Auto DevOps
auto_devops = AutoDevOps(
    deploy_enabled=True,
    sast_disabled=False,
)

# Individual security templates
sast = SAST(excluded_paths=["vendor/"])
dast = DAST(website="https://example.com")
```

### How do I configure GitLab Runner?

```python
from wetwire_gitlab.runner_config import Config, Runner, Executor, DockerConfig

docker = DockerConfig(image="python:3.11", privileged=True)
runner = Runner(
    name="my-runner",
    url="https://gitlab.com",
    token="glrt-xxx",
    executor=Executor.DOCKER,
    docker=docker,
)
config = Config(concurrent=4, runners=[runner])
print(config.to_toml())
```

### How do I visualize the pipeline graph?

```bash
# Mermaid format (for GitLab/GitHub rendering)
wetwire-gitlab graph

# DOT format (for Graphviz)
wetwire-gitlab graph --format dot
```

### How do I handle child pipelines?

```python
from wetwire_gitlab.pipeline import *, Trigger

trigger_frontend = Job(
    name="trigger-frontend",
    stage="trigger",
    trigger=Trigger(
        include=[{"local": "frontend/.gitlab-ci.yml"}],
        strategy="depend",
    ),
)
```

## Troubleshooting

### glab validation fails

Ensure glab CLI is installed and configured:

```bash
# Install glab
brew install glab  # macOS

# Authenticate
glab auth login
```

### Import produces unexpected output

The importer converts YAML to typed Python. Complex includes or anchors may need manual adjustment.

### Jobs not discovered

Ensure your Python files:
1. Import `Job` from `wetwire_gitlab.pipeline`
2. Declare jobs at module level (not inside functions)
3. Are in the package specified in `pyproject.toml`

### Type errors in IDE

Install the package in development mode:

```bash
pip install -e .
```

## Resources

- [Wetwire Specification](https://github.com/lex00/wetwire/blob/main/docs/WETWIRE_SPEC.md)
- [wetwire-gitlab-go](https://github.com/lex00/wetwire-gitlab-go) - Go implementation
