# Imported Real-World Examples

These pipelines were imported from official GitLab CI/CD templates.

## Examples

| Template | Source | Description |
|----------|--------|-------------|
| gitlab-python-template | [Python.gitlab-ci.yml](https://gitlab.com/gitlab-org/gitlab/-/blob/master/lib/gitlab/ci/templates/Python.gitlab-ci.yml) | Python project CI template |
| gitlab-nodejs-template | [Nodejs.gitlab-ci.yml](https://gitlab.com/gitlab-org/gitlab/-/blob/master/lib/gitlab/ci/templates/Nodejs.gitlab-ci.yml) | Node.js project CI template |
| gitlab-rust-template | [Rust.gitlab-ci.yml](https://gitlab.com/gitlab-org/gitlab/-/blob/master/lib/gitlab/ci/templates/Rust.gitlab-ci.yml) | Rust project CI template |

## License

The original templates are from [gitlab-org/gitlab](https://gitlab.com/gitlab-org/gitlab) and are licensed under the MIT License.

## Import Date

2026-01-10

## Usage

Build the examples to regenerate the GitLab CI YAML:

```bash
wetwire-gitlab build examples/imported/gitlab-python-template
wetwire-gitlab build examples/imported/gitlab-nodejs-template
wetwire-gitlab build examples/imported/gitlab-rust-template
```

## Round-Trip Testing

These examples verify that:
1. The importer correctly parses official GitLab CI templates
2. The generated Python code is valid
3. The build command produces valid YAML output

Run the tests with:
```bash
pytest tests/ -k "imported"
```
