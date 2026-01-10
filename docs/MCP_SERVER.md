# MCP Server

This guide documents the Model Context Protocol (MCP) server for wetwire-gitlab.

## Overview

The wetwire-gitlab MCP server exposes pipeline generation tools to AI agents. It enables AI assistants like Claude to create, lint, and validate GitLab CI/CD pipelines through a standardized protocol.

## Installation

```bash
# Install with MCP support
pip install wetwire-gitlab[mcp]

# Verify installation
wetwire-gitlab-mcp --help
```

## Running the Server

### Standalone (stdio transport)

```bash
wetwire-gitlab-mcp
```

### With Claude Desktop

Add to your Claude Desktop configuration (`~/.config/claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "wetwire-gitlab-mcp": {
      "command": "wetwire-gitlab-mcp"
    }
  }
}
```

### With Kiro CLI

The Kiro provider automatically installs MCP configuration:

```bash
wetwire-gitlab design --provider kiro
```

## Available Tools

### wetwire_init

Initialize a new wetwire-gitlab package.

**Arguments:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `path` | string | Yes | Directory where package should be created |
| `module_name` | string | Yes | Package name (snake_case) |

**Example:**

```json
{
  "name": "wetwire_init",
  "arguments": {
    "path": ".",
    "module_name": "my_pipeline"
  }
}
```

**Returns:**

```json
{
  "success": true,
  "message": "Created package: ./my_pipeline"
}
```

### wetwire_lint

Lint Python code for wetwire-gitlab issues.

**Arguments:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `path` | string | Yes | Path to Python file or directory |

**Example:**

```json
{
  "name": "wetwire_lint",
  "arguments": {
    "path": "./my_pipeline"
  }
}
```

**Returns:**

```json
{
  "success": true,
  "issues": [],
  "files_checked": 3
}
```

Or with issues:

```json
{
  "success": false,
  "issues": [
    {
      "code": "WGL010",
      "message": "Use When.MANUAL instead of 'manual'",
      "file_path": "./my_pipeline/jobs.py",
      "line_number": 15
    }
  ],
  "files_checked": 3
}
```

### wetwire_build

Generate .gitlab-ci.yml from a package.

**Arguments:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `path` | string | Yes | Path to Python package |
| `output` | string | No | Output file (default: stdout) |
| `format` | string | No | Output format: yaml or json |

**Example:**

```json
{
  "name": "wetwire_build",
  "arguments": {
    "path": "./my_pipeline",
    "output": ".gitlab-ci.yml"
  }
}
```

**Returns:**

```json
{
  "success": true,
  "output_path": ".gitlab-ci.yml",
  "jobs_count": 5
}
```

### wetwire_validate

Validate pipeline with GitLab CI lint API (requires glab CLI).

**Arguments:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `path` | string | Yes | Path to .gitlab-ci.yml |

**Example:**

```json
{
  "name": "wetwire_validate",
  "arguments": {
    "path": ".gitlab-ci.yml"
  }
}
```

**Returns:**

```json
{
  "valid": true,
  "errors": []
}
```

### wetwire_import

Import existing YAML to Python code.

**Arguments:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `input` | string | Yes | Path to .gitlab-ci.yml |
| `output` | string | No | Output directory |

**Example:**

```json
{
  "name": "wetwire_import",
  "arguments": {
    "input": ".gitlab-ci.yml",
    "output": "./imported_pipeline"
  }
}
```

## Typical Workflow

An AI agent using the MCP server typically follows this workflow:

```
1. wetwire_init
   Create package structure

2. Write code
   Create jobs.py, pipeline.py using file tools

3. wetwire_lint
   Check for issues

4. Fix issues
   Update code based on lint feedback

5. wetwire_lint (repeat until clean)
   Verify fixes

6. wetwire_build
   Generate .gitlab-ci.yml

7. wetwire_validate (optional)
   Validate with GitLab API
```

## Error Handling

All tools return structured error responses:

```json
{
  "success": false,
  "error": "Package already exists: ./my_pipeline"
}
```

Common errors:

| Error | Cause | Solution |
|-------|-------|----------|
| `Directory does not exist` | Invalid path | Create directory first |
| `Package already exists` | Name collision | Use different name or delete existing |
| `Invalid module name` | Non-alphanumeric characters | Use snake_case |
| `glab not installed` | Missing GitLab CLI | Install glab for validation |

## Integration with Kiro

The `--provider kiro` option in design/test commands uses the MCP server:

```bash
# Interactive design session
wetwire-gitlab design --provider kiro

# Automated testing
wetwire-gitlab test --provider kiro "Create a Python CI pipeline"
```

This automatically:

1. Installs agent configuration in `~/.kiro/agents/wetwire-runner.json`
2. Configures MCP server in project `.kiro/mcp.json`
3. Launches Kiro CLI with the wetwire-runner agent

## Debugging

Enable verbose logging:

```bash
# Set environment variable
export MCP_DEBUG=1
wetwire-gitlab-mcp
```

Check server is responding:

```bash
# Send a simple request
echo '{"jsonrpc":"2.0","method":"tools/list","id":1}' | wetwire-gitlab-mcp
```
