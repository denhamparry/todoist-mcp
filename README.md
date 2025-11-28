# Todoist MCP Server

[![CI](https://github.com/denhamparry/todoist-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/denhamparry/todoist-mcp/actions/workflows/ci.yml)

An MCP (Model Context Protocol) server that enables AI agents to manage Todoist tasks through natural language commands.

## Features

- Create, read, update, and delete tasks
- Manage projects and labels
- Natural language due dates (e.g., "tomorrow", "next Monday at 3pm")
- Priority and label support
- Complete task workflow integration
- Rate limit handling with clear error messages and optional retry logic

## Installation

### Prerequisites

- Python 3.10 or later
- A Todoist account and API token

### Setup

1. Clone the repository:

```bash
git clone https://github.com/denhamparry/todoist-mcp.git
cd todoist-mcp
```

2. Install dependencies using one of the following methods:

**Option A: Using `uv` (Recommended - Fast and Modern)**

```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Install development dependencies
uv sync --dev
```

**Option B: Using `pip` (Traditional)**

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install package and dependencies
pip install -e ".[dev]"
```

3. Create a `.env` file with your Todoist API token:

```bash
cp .env.example .env
# Edit .env and add your token
```

4. Get your API token from Todoist:
   - Visit: <https://todoist.com/help/articles/find-your-api-token-Jpzx9IIlB>
   - Copy your API token
   - Paste it into `.env` file

## Usage with Claude Code

### Recommended: Using CLI (Easiest)

The `claude mcp add` command automatically configures the MCP server for you. This is the easiest and recommended method.

#### Using uv (Recommended)

```bash
claude mcp add --transport stdio todoist \
  --env TODOIST_API_TOKEN=your_token_here \
  --env LOG_LEVEL=INFO \
  -- uv run --directory /path/to/todoist-mcp todoist-mcp
```

Replace `/path/to/todoist-mcp` with the actual path where you cloned this repository.

**Example:**

```bash
claude mcp add --transport stdio todoist \
  --env TODOIST_API_TOKEN=abc123xyz \
  --env LOG_LEVEL=INFO \
  -- uv run --directory /Users/lewis/git/todoist-mcp todoist-mcp
```

#### Using System Python

If you prefer not to use `uv`, you can use Python directly:

```bash
claude mcp add --transport stdio todoist \
  --env TODOIST_API_TOKEN=your_token_here \
  --env LOG_LEVEL=INFO \
  -- python -m todoist_mcp.server
```

**Note:** When using system Python, ensure you've activated the virtual environment first, or provide the full path to the Python interpreter in your project's virtual environment.

#### Verification

After running the command, verify the server is configured correctly:

```bash
claude mcp list
```

You should see `todoist` in the list of configured MCP servers with a status indicator showing it's ready.

### Alternative: Manual Configuration

For advanced users or if you need to troubleshoot, you can manually edit the Claude Code MCP configuration file.

**Location:**

- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

Add the following to your MCP settings:

```json
{
  "mcpServers": {
    "todoist": {
      "command": "python",
      "args": ["-m", "todoist_mcp.server"],
      "env": {
        "TODOIST_API_TOKEN": "your_token_here"
      }
    }
  }
}
```

Or if using `uv`:

```json
{
  "mcpServers": {
    "todoist": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/todoist-mcp", "todoist-mcp"],
      "env": {
        "TODOIST_API_TOKEN": "your_token_here",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

### Troubleshooting Setup

**Issue: "Failed to connect" error**

If you see `✗ Failed to connect` after running `claude mcp add`:

1. **Check the command syntax** - Ensure you included `run` and the script name:
   - ✓ Correct: `-- uv run --directory /path/to/todoist-mcp todoist-mcp`
   - ✗ Wrong: `-- uv --directory /path/to/todoist-mcp`

2. **Verify the path** - Make sure the directory path is absolute and correct:

   ```bash
   ls -la /path/to/todoist-mcp/pyproject.toml  # Should exist
   ```

3. **Test the server manually** - Run the server directly to check for errors:

   ```bash
   cd /path/to/todoist-mcp
   uv run todoist-mcp
   # Should start without errors (press Ctrl+C to stop)
   ```

4. **Check your API token** - Verify it's valid:

   ```bash
   # Test the token manually with curl
   # Use your actual API token from Todoist
   curl -H "Authorization: Bearer $TODOIST_API_TOKEN" \
     https://api.todoist.com/rest/v2/projects
   # Should return your projects, not 401 error
   ```

**Issue: Server not appearing in `claude mcp list`**

1. **Restart Claude Code** - The configuration may need a restart to take effect
2. **Check the configuration file manually** - Verify the JSON was written correctly
3. **Look for syntax errors** - Ensure the JSON is valid (no trailing commas, proper quotes)

For more troubleshooting help, see [docs/troubleshooting.md](docs/troubleshooting.md).

## Logging

The server uses structured logging to help with debugging and monitoring.

### Configuration

Set the log level via environment variable in your `.env` file:

```bash
LOG_LEVEL=INFO  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
```

Or when configuring the MCP server (manual configuration method):

```json
{
  "mcpServers": {
    "todoist": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/todoist-mcp", "todoist-mcp"],
      "env": {
        "TODOIST_API_TOKEN": "your_token_here",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

When using the CLI method (`claude mcp add`), the `LOG_LEVEL` environment variable is set with the `--env` flag:

```bash
claude mcp add --transport stdio todoist \
  --env TODOIST_API_TOKEN=your_token_here \
  --env LOG_LEVEL=DEBUG \
  -- uv run --directory /path/to/todoist-mcp todoist-mcp
```

### Log Levels

- **DEBUG** - Detailed diagnostic information (API calls, parameters, internal operations)
- **INFO** - General informational messages (tool calls, successful operations, task counts)
- **WARNING** - Warning messages (validation failures, failed operations)
- **ERROR** - Error messages (API failures, exceptions with stack traces)
- **CRITICAL** - Critical errors (server startup failures, configuration errors)

### Log Output

All logs are written to **stderr** (stdout is reserved for the MCP protocol communication).

**Example log output:**

```text
2025-11-27 10:30:45 - todoist-mcp - INFO - Todoist MCP Server initialized with log level: INFO
2025-11-27 10:30:50 - todoist-mcp - INFO - Tool called: todoist_create_task - content='Buy groceries' priority=3
2025-11-27 10:30:51 - todoist-mcp - INFO - Task created successfully - id=12345 content='Buy groceries' priority=3
2025-11-27 10:31:00 - todoist-mcp - INFO - Tool called: todoist_get_tasks - project_id=None label=None
2025-11-27 10:31:01 - todoist-mcp - INFO - Retrieved 15 task(s) from Todoist
```

### Debugging

When troubleshooting issues, set `LOG_LEVEL=DEBUG` for detailed diagnostic information:

```bash
# In .env file
LOG_LEVEL=DEBUG
```

This will show:

- All tool calls with full parameters
- Todoist API interactions
- Validation checks
- Internal operations

### Log Security

The logging system is designed with security in mind:

- **API tokens are never logged** - Token values are filtered from all log output
- **Only necessary data is logged** - Task IDs, content, and metadata (not sensitive credentials)
- **Exceptions include context** - Error logs include stack traces for debugging without exposing secrets

### Viewing Logs

Logs are output to stderr. To view them:

**When running directly:**

```bash
uv run python -m todoist_mcp.server
# Logs appear in terminal
```

**When using with Claude Code:**

- Logs are captured by the Claude Code MCP framework
- Check your MCP server logs in the Claude Code interface
- Or redirect stderr to a file in your MCP configuration

## Available Tools

### Task Management

- **`todoist_get_tasks`** - Retrieve tasks with optional filtering
  - **Parameters:**
    - `project_id` (optional) - Filter by project ID
    - `label` (optional) - Filter by label name
    - `filter` (optional) - Todoist filter query for advanced filtering
  - **Filter Examples:**
    - Time-based: `filter="today"`, `filter="overdue"`, `filter="7 days"`
    - Priority: `filter="p1"` (urgent), `filter="p2"` (high)
    - Combined: `filter="today & p1"` (urgent tasks due today)
    - Complex: `filter="(today | overdue) & @work"` (work tasks today or overdue)
  - **Note:** When using `filter`, it takes precedence over `project_id`/`label`
  - **Reference:** [Todoist Filter Syntax](https://todoist.com/help/articles/introduction-to-filters)
  - Returns formatted list with IDs, due dates, priorities, and labels

- **`todoist_create_task`** - Create new tasks
  - Support for natural language due dates
  - Set priority, labels, project, and description
  - Returns task ID for further operations

- **`todoist_update_task`** - Update existing tasks
  - Modify content, description, due date, priority, or labels
  - Requires task ID

- **`todoist_complete_task`** - Mark tasks as complete
  - Simple completion with task ID

- **`todoist_delete_task`** - Delete tasks permanently
  - Requires task ID

### Organization

- **`todoist_get_projects`** - List all projects
  - Shows project IDs and names
  - Indicates favorite projects

- **`todoist_get_labels`** - List all labels
  - Shows label IDs and names

## Examples

Ask Claude Code:

- "Show me all my tasks due today"
- "Create a task to review the PR tomorrow with high priority"
- "Complete the task with ID 12345"
- "What projects do I have?"
- "Create a task 'Buy groceries' due next Monday with label 'personal'"
- "Update task 67890 to be urgent priority"

## Development

### Running Tests

**Unit Tests** (default - no API token required):

```bash
# Using uv
uv run pytest

# Using pip (with activated venv)
pytest

# With coverage report
pytest --cov=src/todoist_mcp --cov-report=html
```

**Integration Tests** (requires real Todoist API token):

Integration tests make real API calls to Todoist and require additional setup.
See [Integration Testing Guide](docs/integration-testing.md) for detailed
instructions.

```bash
# Run integration tests
pytest tests/test_integration.py -m integration -v

# Run all tests (unit + integration)
pytest -v
```

**Important:** Integration tests:

- Require `TODOIST_API_TOKEN` environment variable
- Make real API calls and create/delete actual tasks
- Should use a dedicated test account and project
- Are not run in CI/CD (manual only)

For complete setup instructions, troubleshooting, and best practices, see the
[Integration Testing Guide](docs/integration-testing.md).

### Code Quality

```bash
# Run pre-commit hooks
pre-commit install
pre-commit run --all-files

# Format code
black src/ tests/
isort src/ tests/

# Type checking
mypy src/
```

### Testing the Server

```bash
# Using uv
uv run python -m todoist_mcp.server

# Using pip
python -m todoist_mcp.server

# Test with MCP inspector (if available)
npx @modelcontextprotocol/inspector python -m todoist_mcp.server
```

## Architecture

The server uses:

- **FastMCP** - High-level MCP SDK for simple tool definition
- **todoist-api-python** - Official Todoist Python SDK
- **stdio transport** - Communication over standard input/output
- **Async/await** - Efficient concurrent operations

## Project Structure

```text
todoist-mcp/
├── src/
│   └── todoist_mcp/
│       ├── __init__.py
│       └── server.py         # Complete MCP server implementation
├── tests/
│   ├── __init__.py
│   ├── conftest.py           # Pytest fixtures
│   ├── test_server.py        # Unit tests
│   └── test_integration.py   # Integration tests
├── docs/
│   ├── api.md                # Tool API documentation
│   └── setup.md              # Development setup guide
├── pyproject.toml            # Project configuration
├── .env.example              # Environment template
├── .pre-commit-config.yaml   # Code quality hooks
└── README.md                 # This file
```

## Contributing

1. Follow TDD principles - write tests first
2. Run pre-commit hooks before committing
3. Ensure test coverage stays above 80%
4. Update documentation for new features
5. Use conventional commit messages

## Security

- Never commit API tokens to version control
- Use `.env` file for sensitive credentials
- `.env` is included in `.gitignore`
- Review `.env.example` for required variables

## License

MIT

## Support

- **Troubleshooting**: [docs/troubleshooting.md](docs/troubleshooting.md) - Setup, runtime, and MCP integration issues
- **Issues**: <https://github.com/denhamparry/todoist-mcp/issues>
- **Todoist API Docs**: <https://developer.todoist.com/rest/v2/>
- **MCP Specification**: <https://modelcontextprotocol.io/>
- **Claude Code**: <https://docs.claude.com/en/docs/claude-code>
- **Claude MCP CLI**: <https://docs.anthropic.com/claude/docs/claude-code#mcp-servers>

## Acknowledgments

Built with:

- [Model Context Protocol](https://modelcontextprotocol.io/) by Anthropic
- [Todoist API](https://developer.todoist.com/) by Doist
- [todoist-api-python](https://github.com/Doist/todoist-api-python) - Official Python SDK
