# CLI Reference

Complete reference for all wetwire-gitlab CLI commands.

## Global Options

All commands support these options:

| Option | Description |
|--------|-------------|
| `--help` | Show help message |
| `--version` | Show version number |

## Commands

### build

Generate GitLab CI/CD configuration YAML from Python definitions.

```bash
wetwire-gitlab build [OPTIONS]
```

**Options:**

| Option | Default | Description |
|--------|---------|-------------|
| `--directory`, `-d` | `.` | Source directory containing pipeline code |
| `--output`, `-o` | `.gitlab-ci.yml` | Output file path |
| `--format`, `-f` | `yaml` | Output format (`yaml` or `json`) |
| `--stdout` | | Print to stdout instead of file |

**Examples:**

```bash
# Generate .gitlab-ci.yml in current directory
wetwire-gitlab build

# Generate from specific directory
wetwire-gitlab build -d src/ci

# Output as JSON
wetwire-gitlab build --format json

# Print to stdout
wetwire-gitlab build --stdout
```

### validate

Validate pipeline configuration using GitLab CLI (glab).

```bash
wetwire-gitlab validate [OPTIONS]
```

**Options:**

| Option | Default | Description |
|--------|---------|-------------|
| `--file`, `-f` | `.gitlab-ci.yml` | YAML file to validate |
| `--include-jobs` | | Validate expanded job configurations |
| `--dry-run` | | Only validate, don't report to GitLab |

**Examples:**

```bash
# Validate default file
wetwire-gitlab validate

# Validate specific file
wetwire-gitlab validate -f custom.yml

# Include job validation
wetwire-gitlab validate --include-jobs
```

**Note:** Requires `glab` CLI to be installed and configured.

### lint

Check pipeline code for common issues and style violations.

```bash
wetwire-gitlab lint [OPTIONS] [PATH]
```

**Options:**

| Option | Default | Description |
|--------|---------|-------------|
| `--format`, `-f` | `text` | Output format (`text` or `json`) |
| `--rule`, `-r` | | Only run specific rules |
| `--fix` | | Automatically fix issues where possible |

**Examples:**

```bash
# Lint current directory
wetwire-gitlab lint

# Lint specific path
wetwire-gitlab lint src/ci

# Output as JSON
wetwire-gitlab lint --format json

# Run specific rules only
wetwire-gitlab lint -r WGL001 -r WGL002
```

### list

Display discovered jobs and pipelines.

```bash
wetwire-gitlab list [OPTIONS]
```

**Options:**

| Option | Default | Description |
|--------|---------|-------------|
| `--directory`, `-d` | `.` | Source directory |
| `--format`, `-f` | `table` | Output format (`table` or `json`) |

**Examples:**

```bash
# List jobs in current directory
wetwire-gitlab list

# List as JSON
wetwire-gitlab list --format json
```

### import

Convert existing .gitlab-ci.yml to Python code.

```bash
wetwire-gitlab import [OPTIONS] FILE
```

**Options:**

| Option | Default | Description |
|--------|---------|-------------|
| `--output`, `-o` | `ci/` | Output directory |
| `--single-file` | | Generate single file instead of directory |
| `--no-scaffold` | | Don't create __init__.py files |

**Examples:**

```bash
# Import to ci/ directory
wetwire-gitlab import .gitlab-ci.yml

# Import to specific directory
wetwire-gitlab import -o src/pipeline .gitlab-ci.yml

# Generate single file
wetwire-gitlab import --single-file .gitlab-ci.yml
```

### graph

Visualize pipeline dependency graph.

```bash
wetwire-gitlab graph [OPTIONS]
```

**Options:**

| Option | Default | Description |
|--------|---------|-------------|
| `--directory`, `-d` | `.` | Source directory |
| `--format`, `-f` | `mermaid` | Output format (`mermaid` or `dot`) |
| `--output`, `-o` | | Output file (stdout if not specified) |

**Examples:**

```bash
# Generate Mermaid diagram
wetwire-gitlab graph

# Generate DOT format
wetwire-gitlab graph --format dot

# Save to file
wetwire-gitlab graph -o pipeline.mmd
```

### init

Initialize a new wetwire-gitlab project (scaffold).

```bash
wetwire-gitlab init [OPTIONS] [DIRECTORY]
```

**Options:**

| Option | Default | Description |
|--------|---------|-------------|
| `--name`, `-n` | | Project name |

**Examples:**

```bash
# Initialize in current directory
wetwire-gitlab init

# Initialize in new directory
wetwire-gitlab init my-project
```

### design

AI-assisted pipeline design (requires wetwire-core).

```bash
wetwire-gitlab design [OPTIONS]
```

### test

Run persona-based evaluation tests (requires wetwire-core).

```bash
wetwire-gitlab test [OPTIONS]
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Error or issues found |
| 2 | Invalid arguments |
