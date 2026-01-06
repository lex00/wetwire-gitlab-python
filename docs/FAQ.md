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
from wetwire_gitlab.pipeline import Job

build = Job(
    name="build",
    stage="build",
    script=["make build"],
)
```

### How do I use CI variables?

Use typed variable namespaces instead of raw strings:

```python
from wetwire_gitlab.intrinsics import CI, GitLab, MR

# These expand to proper $VARIABLE syntax
branch = CI.COMMIT_BRANCH     # $CI_COMMIT_BRANCH
user = GitLab.USER_LOGIN      # $GITLAB_USER_LOGIN
source = MR.SOURCE_BRANCH     # $CI_MERGE_REQUEST_SOURCE_BRANCH_NAME
```

### How do I add conditional rules?

Use the `Rule` dataclass or pre-defined rules:

```python
from wetwire_gitlab.pipeline import Rule
from wetwire_gitlab.intrinsics import Rules, CI

# Pre-defined rule
deploy = Job(rules=[Rules.ON_DEFAULT_BRANCH])

# Custom rule
custom = Rule(if_=f"{CI.COMMIT_BRANCH} == 'main'")
```

### How do I configure artifacts?

Use the `Artifacts` dataclass:

```python
from wetwire_gitlab.pipeline import Artifacts

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

## Resources

- [Wetwire Specification](https://github.com/lex00/wetwire/blob/main/docs/WETWIRE_SPEC.md)
- [wetwire-gitlab-go](https://github.com/lex00/wetwire-gitlab-go) - Go implementation
